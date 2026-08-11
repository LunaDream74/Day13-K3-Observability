# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

## Bố cục và contract của nhóm

Nguồn duy nhất cho số liệu dashboard là các event JSONL trong `data/logs.jsonl`.
Sắp xếp hai hàng, mỗi hàng ba panel, theo thứ tự điều tra từ triệu chứng đến tác
động:

| Panel | Event và phép tính | Đơn vị | Ngưỡng |
|---|---|---|---:|
| Latency | `response_sent`; P50/P95/P99 của `latency_ms` | ms | P95 <= 3000 |
| Traffic | số `request_received` mỗi phút | request/phút | >= 1 |
| Errors | `request_failed / request_received`; nhóm theo `error_type` | % | <= 2 |
| Cost | tổng `response_sent.cost_usd` theo phút/cửa sổ | USD | <= 2.5 |
| Tokens | tổng riêng `tokens_in` và `tokens_out` | token | <= 50000 |
| Quality | trung bình `response_sent.quality_score` | 0–1 | >= 0.75 |

Các giá trị trên phải đồng bộ với `config/dashboard.yaml`; thay đổi contract cần
được review cùng người phụ trách SLO/alert.

## Tiêu chí nghiệm thu runtime

- Cửa sổ mặc định 60 phút, refresh 30 giây, tên panel và đơn vị luôn hiển thị.
- Mỗi panel có SLO/threshold line và trạng thái đạt/vi phạm dễ nhận biết.
- Tổng request thành công của load test khớp số `request_received` trong cùng cửa sổ.
- Practice `rag_slow` làm P95 tăng rõ ràng; tắt incident trước khi lấy baseline mới.
- Screenshot thấy đủ sáu panel và time range; không chứa secret hoặc PII.
- Một điểm bất thường phải truy ngược được tới trace rồi log qua correlation ID.

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
