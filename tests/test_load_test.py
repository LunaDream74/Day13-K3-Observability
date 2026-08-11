from __future__ import annotations

import httpx

from scripts.load_test import RequestResult, send_request, summarize


def test_send_request_returns_observable_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat"
        return httpx.Response(200, json={"correlation_id": "req-1234abcd"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = send_request(
            client,
            {"feature": "qa", "message": "hello"},
            base_url="http://test",
        )

    assert result.succeeded
    assert result.correlation_id == "req-1234abcd"
    assert result.status_code == 200


def test_summary_counts_failures_and_missing_correlation_ids() -> None:
    results = [
        RequestResult(200, "req-1234abcd", "qa", 100.0),
        RequestResult(200, "MISSING", "qa", 200.0),
        RequestResult(500, None, "qa", 300.0, "HTTP 500"),
    ]

    summary = summarize(results)

    assert summary["requests"] == 3
    assert summary["successful"] == 2
    assert summary["failed"] == 1
    assert summary["correlation_ids_present"] == 1
    assert summary["client_latency_p95_ms"] == 300.0
