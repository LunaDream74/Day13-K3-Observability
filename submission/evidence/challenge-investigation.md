# CP3 Challenge Investigation Evidence

- Run date: 2026-08-11
- Challenge: `day13-k3-observability-v1` (K3)
- Released incident: `rag_slow`; affected feature: `refund`
- Method: run the same five released queries at concurrency 5 before and after
  enabling the official incident. All other incidents remained disabled.

## Metrics

| Signal | Baseline | Incident | Change |
|---|---:|---:|---:|
| Client P95 | 2520.9 ms | 13304.2 ms | 5.28x |
| Service P95 | 1086 ms | 2652 ms | 2.44x |
| Errors | 0 | 0 | unchanged |
| Quality average | 0.86 | 0.86 | unchanged |

The incident service P95 exceeded the released challenge threshold of 2000 ms.

## Trace and log correlation

- Incident trace: `704d74cdc2270503481e3f2dddea0cf4`, total `2.652 s`.
- Baseline trace for the same session: `e3bc39c8055e676cfa80ac1d9fad9edf`,
  total `1.086 s`.
- Incident trace spans: `retrieve=2.501 s`; `generate=0.150 s`. Retrieval accounts
  for about 94% of the incident trace.
- Session: `k3-challenge-s01`; correlation ID: `req-e920e3ba`.
- Matching log: `2026-08-11T05:02:13.086641Z`, event `response_sent`, feature
  `refund`, `latency_ms=2651`.

## Conclusion and actions

The slowdown is localized to RAG retrieval, not generation, errors, traffic, or
answer quality. Immediate mitigation was to disable `rag_slow`; the cleanup call
confirmed the incident was off before the temporary API stopped.

For a production analogue, enforce a retrieval timeout with cached/fallback
context and record timeout/fallback outcomes. Add a warning before the 3000 ms
service SLO (the released 2000 ms challenge threshold would have detected this
run earlier), then monitor retrieval duration and service P95 together.
