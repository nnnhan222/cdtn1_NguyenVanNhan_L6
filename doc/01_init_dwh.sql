CREATE TABLE IF NOT EXISTS dim_store (
    store_id SERIAL PRIMARY KEY,
    store_code VARCHAR(50) UNIQUE,
    store_name VARCHAR(255),
    city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE,
    product_name VARCHAR(255),
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    phone VARCHAR(20) UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    day_of_week INT,
    month INT,
    quarter INT,
    year INT
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_fact_id SERIAL PRIMARY KEY,
    order_code VARCHAR(50),
    date_key INT REFERENCES dim_date(date_key),
    store_id INT REFERENCES dim_store(store_id),
    product_id INT REFERENCES dim_product(product_id),
    customer_id INT REFERENCES dim_customer(customer_id),
    quantity INT,
    unit_price DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    UNIQUE(order_code, product_id) -- Dùng để chống duplicate khi chạy lại
);

CREATE TABLE IF NOT EXISTS reject_rows (
    id SERIAL PRIMARY KEY,
    ma_quy_tac VARCHAR(100),
    ly_do TEXT,
    du_lieu_goc TEXT,
    thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
