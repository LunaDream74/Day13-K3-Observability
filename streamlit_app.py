from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import yaml

from app.dashboard_data import filter_recent, load_log_frame, per_minute, summarize_dashboard


ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "data" / "logs.jsonl"
CONFIG_PATH = ROOT / "config" / "dashboard.yaml"
CHART_HEIGHT = 245

st.set_page_config(
    page_title="Day 13 AI Observability",
    page_icon=":material/monitoring:",
    layout="wide",
)


@st.cache_data(ttl=30, show_spinner=False)
def load_dashboard_inputs(log_mtime_ns: int) -> tuple[pd.DataFrame, dict]:
    del log_mtime_ns
    frame = load_log_frame(LOG_PATH)
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["dashboard"]
    return frame, config


def threshold_chart(data: pd.DataFrame, *, x: str, y: str, threshold: float, unit: str) -> alt.LayerChart:
    line = (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x}:T", title="Time (UTC)"),
            y=alt.Y(f"{y}:Q", title=unit),
            tooltip=[alt.Tooltip(f"{x}:T", title="Time"), alt.Tooltip(f"{y}:Q", title=unit)],
        )
    )
    limit = alt.Chart(pd.DataFrame({"limit": [threshold]})).mark_rule(color="#e45756", strokeDash=[6, 4]).encode(y="limit:Q")
    return (line + limit).properties(height=CHART_HEIGHT)


def status_text(value: float, operator: str, threshold: float) -> str:
    healthy = value <= threshold if operator == "lte" else value >= threshold
    symbol = ":green[:material/check_circle:]" if healthy else ":red[:material/warning:]"
    relation = "≤" if operator == "lte" else "≥"
    return f"{symbol} Threshold: **{relation} {threshold:g}**"


def panel_config(config: dict, panel_id: str) -> dict:
    return next(panel for panel in config["panels"] if panel["id"] == panel_id)


@st.fragment(run_every=30)
def render_dashboard() -> None:
    mtime = LOG_PATH.stat().st_mtime_ns if LOG_PATH.exists() else 0
    all_records, config = load_dashboard_inputs(mtime)
    records = filter_recent(all_records, config["time_range_minutes"])
    summary = summarize_dashboard(records)

    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        st.caption(
            f"Source: `data/logs.jsonl` · Last {config['time_range_minutes']} minutes · "
            f"Auto-refresh every {config['refresh_seconds']} seconds"
        )
        st.caption(f"{len(records):,} log records in range")

    if records.empty:
        st.warning("No log records are available in the last 60 minutes. Run `python scripts/load_test.py`.")
        return

    latency_cfg = panel_config(config, "latency")
    traffic_cfg = panel_config(config, "traffic")
    errors_cfg = panel_config(config, "errors")
    cost_cfg = panel_config(config, "cost")
    tokens_cfg = panel_config(config, "tokens")
    quality_cfg = panel_config(config, "quality")

    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader("Latency percentiles")
        with st.container(horizontal=True):
            st.metric("P50", f"{summary['latency']['p50']:.0f} ms")
            st.metric("P95", f"{summary['latency']['p95']:.0f} ms")
            st.metric("P99", f"{summary['latency']['p99']:.0f} ms")
        limit = latency_cfg["threshold"]
        st.markdown(status_text(summary["latency"]["p95"], limit["operator"], limit["value"]))
        latency_points = records.loc[records["event"] == "response_sent", ["ts", "latency_ms"]].dropna()
        st.altair_chart(
            threshold_chart(latency_points, x="ts", y="latency_ms", threshold=limit["value"], unit="Latency (ms)"),
            width="stretch",
        )

    with right, st.container(border=True):
        st.subheader("Request traffic")
        traffic = per_minute(records, "request_received")
        rate = float(traffic["count"].mean()) if not traffic.empty else 0.0
        st.metric("Requests", f"{summary['traffic']['count']:,}", f"{rate:.1f} requests/min")
        limit = traffic_cfg["threshold"]
        st.markdown(status_text(rate, limit["operator"], limit["value"]))
        st.altair_chart(
            threshold_chart(traffic, x="minute", y="count", threshold=limit["value"], unit="Requests/min"),
            width="stretch",
        )

    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader("Error rate and breakdown")
        limit = errors_cfg["threshold"]
        st.metric("Error rate", f"{summary['errors']['rate_pct']:.2f}%", f"{summary['errors']['count']} failures")
        st.markdown(status_text(summary["errors"]["rate_pct"], limit["operator"], limit["value"]))
        failures = records.loc[records["event"] == "request_failed"].copy()
        if failures.empty:
            st.info("No request failures in this time range.")
        else:
            breakdown = failures["error_type"].fillna("Unknown").value_counts().rename_axis("Error type").reset_index(name="Count")
            st.bar_chart(breakdown, x="Error type", y="Count", height=CHART_HEIGHT)

    with right, st.container(border=True):
        st.subheader("Cost over time")
        limit = cost_cfg["threshold"]
        st.metric("Total cost", f"${summary['cost']['total']:.4f}")
        st.markdown(status_text(summary["cost"]["total"], limit["operator"], limit["value"]))
        cost = per_minute(records, "response_sent", ["cost_usd"])
        st.altair_chart(
            threshold_chart(cost, x="minute", y="cost_usd", threshold=limit["value"], unit="USD/min"),
            width="stretch",
        )

    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader("Input and output tokens")
        total_tokens = summary["tokens"]["input"] + summary["tokens"]["output"]
        limit = tokens_cfg["threshold"]
        with st.container(horizontal=True):
            st.metric("Input tokens", f"{summary['tokens']['input']:,}")
            st.metric("Output tokens", f"{summary['tokens']['output']:,}")
        st.markdown(status_text(total_tokens, limit["operator"], limit["value"]))
        token_data = pd.DataFrame(
            {"Token type": ["Input", "Output"], "Tokens": [summary["tokens"]["input"], summary["tokens"]["output"]]}
        )
        st.bar_chart(token_data, x="Token type", y="Tokens", height=CHART_HEIGHT)

    with right, st.container(border=True):
        st.subheader("Quality proxy")
        limit = quality_cfg["threshold"]
        st.metric("Mean quality", f"{summary['quality']['mean']:.2f} / 1.00")
        st.markdown(status_text(summary["quality"]["mean"], limit["operator"], limit["value"]))
        quality = per_minute(records, "response_sent", ["quality_score"])
        counts = per_minute(records, "response_sent").rename(columns={"count": "samples"})
        quality = quality.merge(counts, on="minute", how="left")
        quality["quality_score"] = quality["quality_score"] / quality["samples"]
        st.altair_chart(
            threshold_chart(quality, x="minute", y="quality_score", threshold=limit["value"], unit="Score (0–1)"),
            width="stretch",
        )

    with st.expander("Recent observability records"):
        display_columns = [
            column
            for column in ("ts", "event", "correlation_id", "feature", "latency_ms", "cost_usd", "quality_score")
            if column in records
        ]
        st.dataframe(records[display_columns].tail(100).sort_values("ts", ascending=False), hide_index=True)


st.title("Day 13 AI Observability")
st.caption("Metrics → Traces → Logs · Six-panel Checkpoint 2 dashboard")
render_dashboard()
