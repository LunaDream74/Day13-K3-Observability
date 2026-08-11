# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

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

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall: `submission/evidence/trace_waterfall.png`
- Giải thích một span đáng chú ý: `retrieve` đo riêng thời gian truy xuất RAG; `generate` đo thời gian sinh câu trả lời, giúp phân biệt dependency nào làm P95 tăng.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ — 6/6 panel (`submission/evidence/dashboard-validator.txt`)
- Evidence dashboard: `submission/evidence/dashboard.png` (cần chụp runtime)
- SLO đã chọn và lý do: P95 latency ≤ 3000 ms, error rate ≤ 2%, daily cost ≤ $2.5 và quality trung bình ≥ 0.75; đây là các ngưỡng triệu chứng trực tiếp theo contract.
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md`

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Minh (C — QA & Chief Investigator) | Thiết kế contract và tiêu chí nghiệm thu dashboard 6 panel; nâng cấp load test với summary P50/P95/P99, kiểm soát lỗi và thống kê correlation ID; thêm test QA; chạy và ghi baseline vào báo cáo. | [`1d55fff`](https://github.com/LunaDream74/Day13-K3-Observability/commit/1d55fff6eca03e7df3f1b138f39b32a54f02e41c) | Cách giữ cùng input/concurrency để so sánh baseline–incident, đọc percentile và dùng validator để phát hiện dependency CP1 trước khi điều tra theo Metrics → Traces → Logs. |
