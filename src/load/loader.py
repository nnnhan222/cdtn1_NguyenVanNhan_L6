import pandas as pd
from sqlalchemy import text

def load_data(df_valid: pd.DataFrame, df_error: pd.DataFrame, engine):
    """Nạp dữ liệu vào DB, nạp lại không bị nhân đôi (UPSERT)."""
    with engine.begin() as conn:
        # Nạp bảng reject
        if not df_error.empty:
            for _, row in df_error.iterrows():
                conn.execute(text("""
                    INSERT INTO reject_rows (ma_quy_tac, ly_do, du_lieu_goc)
                    VALUES ('DATA_QUALITY', :ly_do, :du_lieu_goc)
                """), {"ly_do": row['ly_do'], "du_lieu_goc": str(row.to_dict())})
        
        if df_valid.empty:
            return

        # Load Dimensions (Upsert) & Fact
        for _, row in df_valid.iterrows():
            # dim_store
            res_store = conn.execute(text("""
                INSERT INTO dim_store (store_code, store_name, city)
                VALUES (:scode, :sname, :city)
                ON CONFLICT (store_code) DO UPDATE SET store_name = EXCLUDED.store_name
                RETURNING store_id
            """), {"scode": row['store_code'], "sname": row['store_name'], "city": row['city']})
            store_id = res_store.scalar()

            # dim_product
            res_prod = conn.execute(text("""
                INSERT INTO dim_product (product_code, product_name, category)
                VALUES (:pcode, :pname, :cat)
                ON CONFLICT (product_code) DO UPDATE SET product_name = EXCLUDED.product_name
                RETURNING product_id
            """), {"pcode": row['product_code'], "pname": row['product_name'], "cat": row['category']})
            prod_id = res_prod.scalar()

            # dim_customer
            res_cust = conn.execute(text("""
                INSERT INTO dim_customer (customer_name, phone)
                VALUES (:cname, :phone)
                ON CONFLICT (phone) DO UPDATE SET customer_name = EXCLUDED.customer_name
                RETURNING customer_id
            """), {"cname": row['customer_name'], "phone": row['customer_phone']})
            cust_id = res_cust.scalar()

            # dim_date
            conn.execute(text("""
                INSERT INTO dim_date (date_key, full_date, month, year)
                VALUES (:dkey, :fdate, :mon, :yr)
                ON CONFLICT (date_key) DO NOTHING
            """), {"dkey": row['date_key'], "fdate": row['order_date'], "mon": row['order_date'].month, "yr": row['order_date'].year})

            # fact_sales (Upsert để không duplicate)
            conn.execute(text("""
                INSERT INTO fact_sales (order_code, date_key, store_id, product_id, customer_id, quantity, unit_price, total_amount)
                VALUES (:ocode, :dkey, :sid, :pid, :cid, :qty, :price, :total)
                ON CONFLICT (order_code, product_id) DO UPDATE SET 
                    quantity = EXCLUDED.quantity, total_amount = EXCLUDED.total_amount
            """), {
                "ocode": row['order_code'], "dkey": row['date_key'], "sid": store_id,
                "pid": prod_id, "cid": cust_id, "qty": row['quantity'], 
                "price": row['unit_price'], "total": row['total_amount']
            })
