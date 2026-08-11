import argparse
import concurrent.futures
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.challenge import load_challenge, ordered_queries
from app.cli import configure_utf8_stdio

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


@dataclass(frozen=True)
class RequestResult:
    status_code: int | None
    correlation_id: str | None
    feature: str
    latency_ms: float
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None and self.status_code is not None and self.status_code < 400


def send_request(
    client: httpx.Client, payload: dict[str, Any], base_url: str = BASE_URL
) -> RequestResult:
    started = time.perf_counter()
    try:
        response = client.post(f"{base_url.rstrip('/')}/chat", json=payload)
        latency_ms = (time.perf_counter() - started) * 1000
        try:
            body = response.json()
        except ValueError:
            body = {}
        correlation_id = body.get("correlation_id") if isinstance(body, dict) else None
        error = None if response.is_success else f"HTTP {response.status_code}"
        return RequestResult(
            status_code=response.status_code,
            correlation_id=correlation_id if isinstance(correlation_id, str) else None,
            feature=str(payload.get("feature", "unknown")),
            latency_ms=latency_ms,
            error=error,
        )
    except httpx.HTTPError as exc:
        return RequestResult(
            status_code=None,
            correlation_id=None,
            feature=str(payload.get("feature", "unknown")),
            latency_ms=(time.perf_counter() - started) * 1000,
            error=f"{type(exc).__name__}: {exc}",
        )


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((percent / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def summarize(results: list[RequestResult]) -> dict[str, int | float]:
    latencies = [result.latency_ms for result in results]
    successful = sum(result.succeeded for result in results)
    valid_correlation_ids = sum(
        bool(result.correlation_id and result.correlation_id != "MISSING")
        for result in results
    )
    return {
        "requests": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "correlation_ids_present": valid_correlation_ids,
        "client_latency_p50_ms": round(percentile(latencies, 50), 1),
        "client_latency_p95_ms": round(percentile(latencies, 95), 1),
        "client_latency_p99_ms": round(percentile(latencies, 99), 1),
    }


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--repeat", type=int, default=1, help="Repeat the selected input set")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL")
    parser.add_argument(
        "--challenge",
        action="store_true",
        help="Dùng input chính thức trong config/challenge.json sau khi được release.",
    )
    args = parser.parse_args()

    if args.concurrency < 1 or args.repeat < 1 or args.timeout <= 0:
        parser.error("--concurrency, --repeat and --timeout must be positive")

    if args.challenge:
        challenge = load_challenge()
        payloads = ordered_queries(challenge)
        print(f"Challenge: {challenge.challenge_id} | Cohort: {challenge.cohort}")
    else:
        payloads = [
            json.loads(line)
            for line in QUERIES.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    payloads *= args.repeat
    results: list[RequestResult] = []
    with httpx.Client(timeout=args.timeout) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [
                    executor.submit(send_request, client, payload, args.base_url)
                    for payload in payloads
                ]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        else:
            for payload in payloads:
                results.append(send_request(client, payload, args.base_url))

    for result in results:
        status = result.status_code if result.status_code is not None else "ERR"
        detail = result.error or result.correlation_id or "no-correlation-id"
        print(f"[{status}] {detail} | {result.feature} | {result.latency_ms:.1f}ms")

    summary = summarize(results)
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
