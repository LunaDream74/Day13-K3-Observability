# Cấu hình Alert & Alert Runbook (Day 13 Observability)

Mỗi cảnh báo trong tài liệu này dựa trên triệu chứng ảnh hưởng trực tiếp tới người dùng (symptom-based) hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

---

## Alert 1: `high_latency_p95` <a id="alert-1"></a>

- **Tên alert**: `high_latency_p95`
- **Severity**: `warning`
- **SLI/SLO liên quan**: `latency_p95_ms <= 3000` (target 99.5%)
- **Điều kiện kích hoạt**: `latency_p95 > 3000ms for 5 minutes` (P95 latency vượt quá 3000ms liên tục trong 5 phút).
- **Ảnh hưởng tới người dùng**: Người dùng gặp phản hồi chậm khi gửi câu hỏi qua `/chat`, giao diện có nguy cơ đơ hoặc bị client timeout.
- **Ba bước kiểm tra đầu tiên (Triage Steps)**:
  1. **Xác nhận cửa sổ thời gian & triệu chứng trên Dashboard**: Mở panel *Latency percentiles* trên Streamlit (`http://127.0.0.1:8501`) để kiểm tra xem P95 latency tăng từ mốc thời gian nào và có kèm theo tăng traffic hay không.
  2. **So sánh Trace Spans trên Langfuse**: Lọc các trace có latency cao trong cùng khung giờ, kiểm tra waterfall graph để so sánh thời gian thực thi giữa span `retrieve` (RAG search) và span `generate` (LLM completion), xác định span nào gây nghẽn.
  3. **Kiểm tra Log chi tiết theo Correlation ID**: Truy vết log trong `data/logs.jsonl` với `correlation_id` của các request bị chậm để tìm nguyên nhân (ví dụ: incident `rag_slow`, vector DB timeout, hay LLM retries).
- **Mitigation tạm thời**:
  - Giảm `concurrency` tải từ các client thử nghiệm.
  - Tắt incident bằng `python scripts/inject_incident.py --scenario rag_slow --disable` nếu phát hiện incident practice đang bật.
  - Chuyển sang cấu hình fallback RAG/model phản hồi nhanh nếu hệ thống bị overload.
- **Owner**: `on-call-engineer`

---

## Alert 2: `elevated_error_rate` <a id="alert-2"></a>

- **Tên alert**: `elevated_error_rate`
- **Severity**: `critical`
- **SLI/SLO liên quan**: `error_rate_pct <= 2` (target 99.0%)
- **Điều kiện kích hoạt**: `error_rate_pct > 5 for 3 minutes` (Tỷ lệ lỗi request vượt quá 5% liên tục trong 3 phút).
- **Ảnh hưởng tới người dùng**: Người dùng nhận phản hồi lỗi HTTP 500 hoặc ứng dụng không trả về kết quả trả lời câu hỏi.
- **Ba bước kiểm tra đầu tiên (Triage Steps)**:
  1. **Kiểm tra Error Breakdown trên Dashboard**: Xem panel *Error rate and breakdown* trên Streamlit dashboard để xác định loại lỗi đang gia tăng (ví dụ: `HTTPException`, `ToolError`, `ConnectionError`).
  2. **Truy vết Trace bị lỗi trên Langfuse**: Lọc các trace có status `ERROR` hoặc chứa exception, mở chi tiết trace để kiểm tra bước bị gãy (tool call, external API, hay LLM backend).
  3. **Tra cứu Log lỗi theo Correlation ID**: Tìm log `request_failed` trong `data/logs.jsonl` trùng với thời gian xảy ra cảnh báo để lấy full stacktrace và thông tin `error_type`.
- **Mitigation tạm thời**:
  - Cô lập feature hoặc tool đang bị lỗi (ví dụ: tắt bớt external tool bị ngắt kết nối).
  - Kích hoạt cơ chế fallback trả về phản hồi mặc định hoặc thông báo bận hợp lý thay vì crash API HTTP 500.
  - Khởi động lại service API hoặc rollback phiên bản release vừa triển khai.
- **Owner**: `on-call-engineer`

---

## Alert 3: `cost_budget_exceeded` <a id="alert-3"></a>

- **Tên alert**: `cost_budget_exceeded`
- **Severity**: `warning`
- **SLI/SLO liên quan**: `daily_cost_usd <= 2.5` (target 100.0%)
- **Điều kiện kích hoạt**: `daily_cost_usd > 2.5` (Tổng chi phí API LLM trong ngày vượt quá ngân sách $2.5 USD).
- **Ảnh hưởng tới người dùng**: Không ảnh hưởng trực tiếp đến trải nghiệm phản hồi ngay lập tức, nhưng có nguy cơ hết ngân sách API gây gián đoạn dịch vụ toàn hệ thống.
- **Ba bước kiểm tra đầu tiên (Triage Steps)**:
  1. **Xem xu hướng chi phí & Token trên Dashboard**: Kiểm tra các panel *Cost over time* và *Input and output tokens* trên Streamlit dashboard để xem lượng token spike ở đâu (input hay output).
  2. **Kiểm tra Prompt Version & Model Config**: Mở Langfuse tracing để phân tích xem có prompt version nào mới (ví dụ: candidate prompt với system prompt quá dài) làm tăng vọt `tokens_in` hoặc sinh `tokens_out` quá dài không.
  3. **Phân tích Traffic anomaly theo User/Session**: Kiểm tra xem có `user_id_hash` hoặc `session_id` nào đang gửi lượng request bất thường (spam/loop load test) hay không.
- **Mitigation tạm thời**:
  - Rollback prompt về phiên bản baseline gọn nhẹ hơn bằng `python scripts/manage_prompts.py rollback`.
  - Áp dụng rate limiting hoặc token cap cho các request có dung lượng câu hỏi quá lớn.
  - Tạm dừng các đợt load test tự động không cần thiết.
- **Owner**: `team-lead`
