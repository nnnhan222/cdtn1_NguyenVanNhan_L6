# Nhật ký thay đổi so với thiết kế Bài tập 1
- Thay đổi: Thêm UNIQUE CONSTRAINT `(order_code, product_id)` trong `fact_sales`.
- Vì sao: Để đảm bảo cơ chế "nạp lại lần hai không nhân đôi dữ liệu" (UPSERT).
- Ảnh hưởng: Cấu trúc CSDL (`sql/01_init_dwh.sql`) và pha Load.
