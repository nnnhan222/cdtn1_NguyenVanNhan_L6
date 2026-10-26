# Mekong Mobile Sales ETL – BT2 Track DA

Pipeline ETL theo lô cho dữ liệu doanh thu Mekong Mobile, tiếp nối mô hình star schema đã thiết kế ở BT1. Pipeline đọc dữ liệu CSV, chuẩn hóa dữ liệu đơn hàng và chi tiết sản phẩm, chạy các phép kiểm chất lượng, ghi dòng lỗi vào reject và nạp fact/dimension vào SQLite. Khóa nghiệp vụ của fact bảo đảm chạy lặp không tạo thêm bản ghi. Dataset nguồn là bộ dữ liệu mô phỏng dùng trong học phần.

## Yêu cầu
- Python 3.10+
- pandas 2.2.3

## Cài đặt và chạy
Từ thư mục gốc repo:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Cài thư viện:
```bash
pip install -r requirements.txt
```

Chạy pipeline:
```bash
python -m src.pipeline
```

Nguồn cần đặt trong `data/raw/`: `orders_2024_2026(1).csv`, `order_items(1).csv`, `stores(1).csv`, `products(1).csv`, `customers_raw(1).csv`. Các file CSV lớn không nên commit theo quy định dataset; đặt chúng tại thư mục này trên máy chạy.

## Kiểm chứng
Chạy pipeline hai lần:
```bash
python -m src.pipeline
python -m src.pipeline
```
Kết quả đã kiểm tra với bộ dữ liệu được gửi: cả hai lượt có 35.492 dòng fact; có 51 dòng reject. Đây là kết quả của lần chạy trên snapshot hiện tại, có thể thay đổi nếu dữ liệu đầu vào được chỉnh sửa. Chi tiết nằm ở `output/quality_report.json`, dữ liệu ở `data/warehouse.sqlite`.

Truy vấn bằng Python:
```bash
python -c "import sqlite3; c=sqlite3.connect('data/warehouse.sqlite'); print(c.execute('select count(*) from fact_sales').fetchone()); print(c.execute('select count(*) from reject_rows').fetchone())"
```

Bảng `etl_quality` chứa từng phép kiểm, tổng dòng, số lỗi và tỷ lệ lỗi; `reject_rows` lưu lý do và payload; `fact_sales` cùng bốn dimension phục vụ truy vấn phân tích.

## Quy tắc chính
- Nối orders với order_items theo `order_id`.
- `total_amount = quantity * unit_price` ở grain mặt hàng.
- Dòng thiếu trường bắt buộc, ngày sai, số lượng/giá sai hoặc mã chiều không tồn tại được đưa vào reject.
- Sáu phép kiểm: trường bắt buộc, ngày hợp lệ, số lượng/đơn giá, khóa cửa hàng, khóa sản phẩm, khóa nghiệp vụ duy nhất.
- Nạp lặp dùng `ON CONFLICT` theo khóa fact; dimension cũng upsert.

## Cấu trúc
`src/extract`, `src/transform`, `src/quality`, `src/load` tách riêng các pha và quy tắc. `src/pipeline.py` điều phối bằng một lệnh. Thay đổi so với thiết kế BT1 được ghi ở `docs/thay-doi-thiet-ke.md`; khai báo AI ở `docs/ai-disclosure.md`.
