# Khai báo sử dụng công cụ AI

| Công cụ | Dùng vào việc gì | Tệp/hàm áp dụng | Kiểm chứng |
|---|---|---|---|
| ChatGPT | Gợi ý cấu trúc ETL, kiểm tra chất lượng, idempotent SQLite và diễn đạt tài liệu | `src/extract`, `src/transform`, `src/quality`, `src/load`, docs | Đã chạy pipeline hai lần trên dữ liệu mẫu; số dòng fact giữ nguyên 35.492. |

