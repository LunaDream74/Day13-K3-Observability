# Group Today Plan — Observability Lab

## 1. Mục tiêu chung hôm nay
- Hoàn thành các công việc chính của lab Observability theo phân vai nhóm.
- Đảm bảo hệ thống có logging, tracing, dashboard, alerts và evidence đủ để nộp bài.

## 2. Phân vai và trách nhiệm
- Thành viên A (Tech Lead/Backend Engineer): CP1 — Middleware, Correlation ID, Enrichment Logs.
- Thành viên B (SRE & Alerts Engineer): CP2 — Langfuse, SLO/Alert Rules, Alert Runbook.
- Thành viên C (QA & Chief Investigator): CP3 — Dashboard Spec, load test, challenge/practice incident, tổng hợp báo cáo nhóm.

## 3. Những việc cả nhóm cần hoàn thành hôm nay
- Hoàn thành phần logging và observability cơ bản của API.
- Cung cấp evidence cho log, metrics, trace và dashboard.
- Chuẩn bị báo cáo và tài liệu handoff cho các thành viên còn lại.
- Đảm bảo test và validator chạy thành công trước khi nộp.

## 4. Những việc đã hoàn thành bởi Thành viên A
- Triển khai middleware correlation ID trong app/middleware.py.
- Gán correlation_id vào structlog contextvars và request.state.
- Trả về header x-request-id và x-response-time-ms trên response.
- Enrich các event request_received, response_sent và request_failed bằng metadata: correlation_id, user_id_hash, session_id, feature, model, env.
- Kích hoạt PII scrubbing trong logging pipeline để redact email, phone và credit card trước khi ghi log.
- Chuyển FastAPI startup event cũ sang lifespan để loại bỏ warning deprecation.
- Thêm test và chạy kiểm thử: pytest -q và scripts/validate_logs.py.

## 5. Kết quả đã đạt được
- 26 passed khi chạy pytest.
- validate_logs.py cho Estimated Score: 100/100.
- Logs hiện tại có schema đầy đủ, correlation_id xuyên suốt request, không lộ PII.

## 6. Gợi ý tiếp theo cho nhóm
- Thành viên B nên tiếp tục với CP2: cấu hình Langfuse, SLO/Alert Rules và runbook.
- Thành viên C nên tiếp tục với CP3: dashboard, load test, incident practice/challenge và tổng hợp báo cáo.
- Tất cả các tài liệu liên quan nên được cập nhật liên tục vào thư mục my_workspace.
