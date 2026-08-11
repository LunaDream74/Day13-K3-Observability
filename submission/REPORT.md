# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 30/100 (baseline)
- Tổng số traces: ≥10 (`submission/evidence/trace_list.png`)
- Số PII leak còn lại:
- Link/đường dẫn dashboard: `streamlit_app.py` (local: `http://127.0.0.1:8501`)

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
| | | | |
