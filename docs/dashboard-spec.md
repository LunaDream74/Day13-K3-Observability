# Thiết kế & Yêu cầu Dashboard Observability (Day 13)

Contract kiểm tra bằng máy nằm tại [`config/dashboard.yaml`](../config/dashboard.yaml). Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

---

## 1. Danh sách 6 Nhóm Chỉ số (Panel Specs)

| STT | Nhóm chỉ số | Nguồn dữ liệu (/metrics & log) | Tên Panel | Đơn vị (Unit) | Phép tính / Aggregations | Threshold / SLO Line | Hình thức hiển thị |
|---|---|---|---|---|---|---|---|
| **1** | **Latency** | `/metrics` (`latency_p50`, `latency_p95`, `latency_p99`) / `data/logs.jsonl` (`latency_ms`) | Latency percentiles | `ms` | Percentiles (P50, P95, P99) | `P95 <= 3000 ms` | Line Chart + Threshold Line (P50/P95/P99) |
| **2** | **Traffic** | `/metrics` (`traffic`) / `data/logs.jsonl` (`request_received`) | Request traffic | `requests_per_minute` | Count, Rate per minute | `rate_per_minute >= 1` | Metric Counter & Line Chart theo phút |
| **3** | **Error** | `/metrics` (`error_rate_pct`, `error_breakdown`) / `data/logs.jsonl` (`error_type`) | Error rate and breakdown | `percent` (`%`) | Error rate %, Count by error type | `error_rate_pct <= 2%` | Single Value Metric (%) & Bar Chart Error Breakdown |
| **4** | **Cost** | `/metrics` (`total_cost_usd`, `avg_cost_usd`) / `data/logs.jsonl` (`cost_usd`) | Cost over time | `usd` (`$`) | Total cost, Sum by minute | `total_cost_usd <= $2.5` | Metric total cost & Line Chart USD/min |
| **5** | **Tokens** | `/metrics` (`tokens_in_total`, `tokens_out_total`) / `data/logs.jsonl` (`tokens_in`, `tokens_out`) | Input and output tokens | `tokens` | Sum of tokens (Input / Output) | `total_tokens <= 50,000` | Multi-Metric & Bar Chart Input vs Output |
| **6** | **Quality** | `/metrics` (`quality_avg`) / `data/logs.jsonl` (`quality_score`) | Quality proxy | `score_0_to_1` | Mean quality score | `quality_avg >= 0.75` | Single Value Metric & Line Chart Quality over time |

---

## 2. Tiêu chuẩn Trình bày & Cấu hình Runtime

- **Khoảng thời gian mặc định (Time Range)**: `60 phút` (`time_range_minutes: 60`).
- **Tự động refresh**: `30 giây` (`refresh_seconds: 30`).
- **Ngưỡng SLO / Threshold**: Hiển thị đường nét đứt đỏ (Red Dashed Rule) trên biểu đồ Streamlit/Altair.
- **Đơn vị hiển thị**: Ghi rõ đơn vị trên trục tung (Y-axis) và tooltip (`ms`, `requests_per_minute`, `%`, `$`, `tokens`, `score_0_to_1`).
- **Công cụ sử dụng**: 
  - **Streamlit App**: `streamlit_app.py` (Local: `http://127.0.0.1:8501`) đọc log realtime từ `data/logs.jsonl` và `/metrics`.
  - **FastAPI Metric Endpoint**: `http://localhost:8000/metrics`.
  - **Contract YAML**: `config/dashboard.yaml`.

---

## 3. Kiểm tra endpoint `/metrics`

Gọi endpoint `/metrics` trực tiếp từ ứng dụng FastAPI:

```bash
curl http://localhost:8000/metrics | python -m json.tool
```

Cấu trúc JSON phản hồi mẫu từ `/metrics`:

```json
{
    "traffic": 42,
    "latency_p50": 320.0,
    "latency_p95": 850.0,
    "latency_p99": 1420.0,
    "avg_cost_usd": 0.0015,
    "total_cost_usd": 0.063,
    "tokens_in_total": 8400,
    "tokens_out_total": 4200,
    "error_breakdown": {},
    "quality_avg": 0.92
}
```

---

## 4. Kiểm tra Contract & Evidence

Kiểm tra contract tự động bằng script validator:

```bash
python scripts/validate_dashboard.py
```

**Bằng chứng (Evidence)**:
1. **Contract validation result**: [`submission/evidence/dashboard-validator.txt`](../submission/evidence/dashboard-validator.txt)
2. **Dashboard screenshot**: [`submission/evidence/dashboard.png`](../submission/evidence/dashboard.png)
