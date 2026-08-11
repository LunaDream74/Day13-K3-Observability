from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


NUMERIC_FIELDS = (
    "latency_ms",
    "cost_usd",
    "tokens_in",
    "tokens_out",
    "quality_score",
)


def load_log_frame(path: Path) -> pd.DataFrame:
    """Load valid JSON log records and normalize dashboard fields."""
    records: list[dict] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)

    frame = pd.DataFrame(records)
    if frame.empty:
        return pd.DataFrame(columns=["ts", "event", *NUMERIC_FIELDS])

    if "ts" not in frame:
        frame["ts"] = pd.NaT
    frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    frame = frame.dropna(subset=["ts"]).copy()
    for field in NUMERIC_FIELDS:
        if field not in frame:
            frame[field] = pd.NA
        frame[field] = pd.to_numeric(frame[field], errors="coerce")
    return frame.sort_values("ts")


def filter_recent(frame: pd.DataFrame, minutes: int, *, now: pd.Timestamp | None = None) -> pd.DataFrame:
    """Return records in the requested rolling UTC time window."""
    if frame.empty:
        return frame.copy()
    current = now if now is not None else pd.Timestamp.now(tz="UTC")
    if current.tzinfo is None:
        current = current.tz_localize("UTC")
    return frame.loc[frame["ts"] >= current - pd.Timedelta(minutes=minutes)].copy()


def summarize_dashboard(frame: pd.DataFrame) -> dict:
    """Compute the six metric groups defined by config/dashboard.yaml."""
    responses = frame.loc[frame.get("event", pd.Series(index=frame.index, dtype="object")) == "response_sent"]
    requests = frame.loc[frame.get("event", pd.Series(index=frame.index, dtype="object")) == "request_received"]
    failures = frame.loc[frame.get("event", pd.Series(index=frame.index, dtype="object")) == "request_failed"]

    latency = responses["latency_ms"].dropna()
    quality = responses["quality_score"].dropna()
    request_count = int(len(requests))
    failure_count = int(len(failures))

    return {
        "latency": {
            "p50": float(latency.quantile(0.50)) if not latency.empty else 0.0,
            "p95": float(latency.quantile(0.95)) if not latency.empty else 0.0,
            "p99": float(latency.quantile(0.99)) if not latency.empty else 0.0,
        },
        "traffic": {"count": request_count},
        "errors": {
            "count": failure_count,
            "rate_pct": (failure_count / request_count * 100) if request_count else 0.0,
        },
        "cost": {"total": float(responses["cost_usd"].fillna(0).sum())},
        "tokens": {
            "input": int(responses["tokens_in"].fillna(0).sum()),
            "output": int(responses["tokens_out"].fillna(0).sum()),
        },
        "quality": {"mean": float(quality.mean()) if not quality.empty else 0.0},
    }


def per_minute(frame: pd.DataFrame, event: str, fields: list[str] | None = None) -> pd.DataFrame:
    """Aggregate matching records into UTC minute buckets."""
    matching = frame.loc[frame.get("event", pd.Series(index=frame.index, dtype="object")) == event].copy()
    if matching.empty:
        return pd.DataFrame(columns=["minute", *(fields or ["count"])])
    matching["minute"] = matching["ts"].dt.floor("min")
    if not fields:
        return matching.groupby("minute", as_index=False).size().rename(columns={"size": "count"})
    return matching.groupby("minute", as_index=False)[fields].sum()
