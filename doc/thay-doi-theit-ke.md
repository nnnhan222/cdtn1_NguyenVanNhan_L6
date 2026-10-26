# Thay đổi thiết kế so với BT1

1. Thay đổi: đầu vào thực tế dùng CSV thay cho Excel.  
Vì sao: bộ dữ liệu được giảng viên cung cấp gồm CSV.  
Ảnh hưởng: `src/extract/extractor.py` đọc CSV; vẫn giữ nguyên luồng batch ETL.

2. Thay đổi: kho chạy mẫu bằng SQLite thay cho PostgreSQL.  
Vì sao: giúp giảng viên dựng nhanh mà không cần máy chủ DB.  
Ảnh hưởng: `src/load/loader.py` tạo schema cục bộ; mô hình fact/dimension được giữ.

3. Thay đổi: ghép orders và order_items bằng `order_id`, khóa fact là store_code + order_code + product_code.  
Vì sao: mã đơn có thể trùng giữa cửa hàng và grain BT1 là dòng sản phẩm.  
Ảnh hưởng: transform và tính idempotent ở `src/transform` và `src/load`.
