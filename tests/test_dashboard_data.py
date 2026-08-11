import json
from pathlib import Path

import pandas as pd

from app.dashboard_data import filter_recent, load_log_frame, summarize_dashboard


def test_dashboard_summary_uses_contract_events(tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    records = [
        {"ts": "2026-08-11T04:00:00Z", "event": "request_received"},
        {"ts": "2026-08-11T04:00:01Z", "event": "request_received"},
        {
            "ts": "2026-08-11T04:00:02Z",
            "event": "response_sent",
            "latency_ms": 100,
            "cost_usd": 0.1,
            "tokens_in": 10,
            "tokens_out": 20,
            "quality_score": 0.8,
        },
        {"ts": "2026-08-11T04:00:03Z", "event": "request_failed", "error_type": "Timeout"},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    summary = summarize_dashboard(load_log_frame(path))

    assert summary["traffic"]["count"] == 2
    assert summary["errors"]["rate_pct"] == 50
    assert summary["latency"]["p95"] == 100
    assert summary["cost"]["total"] == 0.1
    assert summary["tokens"] == {"input": 10, "output": 20}
    assert summary["quality"]["mean"] == 0.8


def test_filter_recent_uses_rolling_utc_window(tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text(
        '\n'.join(
            [
                '{"ts":"2026-08-11T03:59:59Z","event":"request_received"}',
                '{"ts":"2026-08-11T04:00:00Z","event":"request_received"}',
            ]
        ),
        encoding="utf-8",
    )
    frame = load_log_frame(path)
    recent = filter_recent(frame, 60, now=pd.Timestamp("2026-08-11T05:00:00Z"))
    assert len(recent) == 1
