# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Baseline (2026-08-11, không bật incident): 10/10 request thành công với
  concurrency 5; client P50 `1451.9 ms`, P95/P99 `1795.4 ms`.
- Điểm `validate_logs.py`: `30/100` trên 67 log record; 60 record thiếu trường
  bắt buộc và enrichment, 0 correlation ID hợp lệ. Đang chờ hoàn tất CP1.
- Tổng số traces: Chưa xác minh trên Langfuse; chờ bàn giao CP2.
- Số PII leak còn lại: `0` theo `validate_logs.py`.
- Link/đường dẫn dashboard: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md)
  (contract: [`config/dashboard.yaml`](../config/dashboard.yaml), validator `6/6`).

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
