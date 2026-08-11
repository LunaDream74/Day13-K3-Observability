# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Fishing
- Repository URL: [github.com/LunaDream74/Day13-K3-Observability](https://github.com/LunaDream74/Day13-K3-Observability)
- Commit SHA cuối:
  [`6a29bb61de2de3fe49b98ff80206e5413774af48`](https://github.com/LunaDream74/Day13-K3-Observability/commit/6a29bb61de2de3fe49b98ff80206e5413774af48)
- Thành viên và vai trò:
  - Nguyễn Hữu Hiếu - **Tech Lead/Backend Engineer**
  - Nguyễn Hữu Thắng - **SRE & Alerts Engineer**
  - Trần Nguyễn Anh Minh - **QA & Chief Investigator**

## 2. Kết quả kỹ thuật

- Baseline (2026-08-11, không bật incident): 10/10 request thành công với
  concurrency 5; client P50 `1451.9 ms`, P95/P99 `1795.4 ms`.
- Điểm `validate_logs.py`: `30/100` ở baseline trước CP1; fresh verification sau
  CP1 đạt `100/100` trên 24 log record.
- Tổng số traces: ≥10 (`submission/evidence/trace_list.png`)
- Số PII leak còn lại: `0` theo fresh verification sau CP1.
- Link/đường dẫn dashboard: `streamlit_app.py` (local: `http://127.0.0.1:8501`),
  contract [`config/dashboard.yaml`](../config/dashboard.yaml), validator `6/6`.

## 3. Logging và tracing

- Evidence correlation ID: [`data/test_cp1_3.log`](../data/test_cp1_3.log) cho thấy
  `req-test-001` xuyên suốt `request_received` → `response_sent`.
- Evidence PII redaction: [`data/test_cp1_3.log`](../data/test_cp1_3.log) chứa
  `[REDACTED_PHONE_VN]` và `[REDACTED_EMAIL]`, không chứa giá trị thô.
- Evidence trace waterfall: [`submission/evidence/trace_waterfall.png`](evidence/trace_waterfall.png).
- Giải thích một span đáng chú ý: `retrieve` đo riêng thời gian truy xuất RAG; `generate` đo thời gian sinh câu trả lời, giúp phân biệt dependency nào làm P95 tăng.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, labels `baseline`, `production`.
- Version/label candidate: version 2, labels `candidate`, `latest`.
- Trace ID của mỗi version: baseline
  `a6fbc7215bfc6395c5581356688791e0`; candidate
  `d44a8ecc404f0705eaec29831adf866d`.
- Bằng chứng version: [`submission/evidence/prompt_ver.png`](evidence/prompt_ver.png).
- Bằng chứng đổi label hoặc rollback:
  [`submission/evidence/rollback_production.png`](evidence/rollback_production.png);
  trạng thái xác minh cuối: `production` trỏ về version 1.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ — 6/6 panel (`submission/evidence/dashboard-validator.txt`)
- Evidence dashboard: [`submission/evidence/dashboard.png`](evidence/dashboard.png),
  đủ 6 panel, time range 60 phút, đơn vị và threshold.
- SLO đã chọn và lý do: P95 latency ≤ 3000 ms, error rate ≤ 2%, daily cost ≤ $2.5 và quality trung bình ≥ 0.75; đây là các ngưỡng triệu chứng trực tiếp theo contract.
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md`

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` (`rag_slow`, feature `refund`).
- Triệu chứng từ metrics: cùng 5 input/concurrency 5, client P95 tăng từ
  `2520.9 ms` lên `13304.2 ms` (5.28x); service P95 tăng từ `1086 ms` lên
  `2652 ms`, vượt challenge threshold `2000 ms`. Error vẫn 0 và quality vẫn 0.86.
- Trace ID liên quan: incident `704d74cdc2270503481e3f2dddea0cf4`
  (`2.652 s`), baseline cùng session `e3bc39c8055e676cfa80ac1d9fad9edf`
  (`1.086 s`). Trong incident trace, `retrieve=2.501 s`, `generate=0.150 s`.
- Log line/correlation ID liên quan: `req-e920e3ba`, session
  `k3-challenge-s01`, event `response_sent` lúc `2026-08-11T05:02:13.086641Z`,
  `latency_ms=2651`.
- Root cause: RAG retrieval chiếm khoảng 94% trace và tăng thêm 2.5 giây; LLM
  generation, error rate và quality không bất thường.
- Fix action: tắt incident `rag_slow` sau phép đo; với production, áp retrieval
  timeout và fallback/cache context.
- Preventive measure: thêm cảnh báo sớm ở 2000 ms trước SLO 3000 ms, theo dõi
  retrieval duration cùng service P95, và test timeout/fallback trong CI.
- Evidence: [`submission/evidence/challenge-investigation.md`](evidence/challenge-investigation.md).

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên                        | Phần việc                                                                                                                                                                                                | Commit/PR                                                                                                                                  | Điều đã học                                                                                                                                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nguyễn Hữu Hiếu (A — Tech Lead/Backend Engineer) | Hoàn thiện middleware correlation ID, request/response headers và structlog context; enrich log với user/session/feature/model/env; kích hoạt PII scrubbing; bổ sung test middleware, enrichment và evidence CP1. | [`8ddc7c5`](https://github.com/LunaDream74/Day13-K3-Observability/commit/8ddc7c5fcaad9a4179f60ae05763296ed29968db) | Cách xóa và bind contextvars cho từng request, truyền correlation ID xuyên suốt API, hash định danh người dùng và scrub PII trước khi JSON log được ghi. |
| Nguyễn Hữu Thắng (B — SRE & Alerts Engineer) | Cấu hình Langfuse và prompt versioning/rollback; thêm span retrieval/generation; hoàn thiện SLO, ba alert và runbook; xây dashboard Streamlit 6 panel, test dữ liệu và thu thập evidence CP2. | [`cb5bacb`](https://github.com/LunaDream74/Day13-K3-Observability/commit/cb5bacb2dd84707cc42743fb25d3964108423e80) | Cách liên kết prompt label/version với trace, thiết kế alert theo triệu chứng và SLO, viết runbook có bước triage, đồng thời chuyển log JSONL thành các chỉ số dashboard có threshold. |
| Trần Nguyễn Anh Minh (C — QA & Chief Investigator) | Thiết kế và nghiệm thu dashboard 6 panel; nâng cấp load test và thêm test QA; chạy baseline; điều tra challenge chính thức theo Metrics → Traces → Logs; tổng hợp evidence và báo cáo. | [`1d55fff`](https://github.com/LunaDream74/Day13-K3-Observability/commit/1d55fff6eca03e7df3f1b138f39b32a54f02e41c), tích hợp CP1/CP2 tại [`6a29bb6`](https://github.com/LunaDream74/Day13-K3-Observability/commit/6a29bb61de2de3fe49b98ff80206e5413774af48) | Cách giữ cùng input/concurrency để so sánh baseline–incident, đọc percentile, đối chiếu trace span với correlation ID và chỉ kết luận root cause khi cả ba lớp evidence khớp. |
