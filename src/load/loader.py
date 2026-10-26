import sqlite3
from pathlib import Path
import pandas as pd
def load_data(result,db_path:Path):
    db_path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript('''
        CREATE TABLE IF NOT EXISTS dim_store(store_code TEXT PRIMARY KEY,store_name TEXT,city TEXT);
        CREATE TABLE IF NOT EXISTS dim_product(product_code TEXT PRIMARY KEY,product_name TEXT,category TEXT);
        CREATE TABLE IF NOT EXISTS dim_customer(customer_key TEXT PRIMARY KEY,customer_name TEXT,phone TEXT);
        CREATE TABLE IF NOT EXISTS dim_date(date_key INTEGER PRIMARY KEY,full_date TEXT,day_of_week TEXT,month INTEGER,quarter INTEGER,year INTEGER);
        CREATE TABLE IF NOT EXISTS fact_sales(order_item_key TEXT PRIMARY KEY,order_code TEXT,date_key INTEGER,store_code TEXT,product_code TEXT,customer_key TEXT,quantity REAL,unit_price REAL,total_amount REAL);
        CREATE TABLE IF NOT EXISTS reject_rows(reject_id INTEGER PRIMARY KEY AUTOINCREMENT,source_order_id TEXT,order_code TEXT,store_code TEXT,product_code TEXT,reject_reason TEXT,source_payload TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(source_order_id,product_code,reject_reason));
        CREATE TABLE IF NOT EXISTS etl_quality(run_id TEXT,check_name TEXT,row_count INTEGER,error_count INTEGER,error_rate REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(run_id,check_name));
        ''')
        for table,cols in [("dim_store",["store_code","store_name","city"]),("dim_product",["product_code","product_name","category"])]:
            result["stores" if table == "dim_store" else "products"][cols].drop_duplicates(cols[0]).to_sql("_tmp",con,if_exists="replace",index=False)
            con.execute(f"INSERT INTO {table} SELECT * FROM _tmp WHERE 1 ON CONFLICT({cols[0]}) DO UPDATE SET "+",".join(f"{c}=excluded.{c}" for c in cols[1:]));con.execute("DROP TABLE _tmp")
        cust=result["fact"][["customer_key","customer_name","phone"]].drop_duplicates("customer_key")
        con.execute("CREATE TABLE IF NOT EXISTS _customer(customer_key TEXT PRIMARY KEY,customer_name TEXT,phone TEXT)")
        cust.to_sql("_customer",con,if_exists="replace",index=False);con.execute("INSERT INTO dim_customer SELECT * FROM _customer WHERE 1 ON CONFLICT(customer_key) DO UPDATE SET customer_name=excluded.customer_name,phone=excluded.phone");con.execute("DROP TABLE _customer")
        d=result["fact"][["date_key","sale_date","day_of_week","month","quarter","year"]].drop_duplicates("date_key").copy();d["full_date"]=d.pop("sale_date").astype(str);d.to_sql("_d",con,if_exists="replace",index=False)
        con.execute("INSERT INTO dim_date SELECT * FROM _d WHERE 1 ON CONFLICT(date_key) DO UPDATE SET full_date=excluded.full_date,day_of_week=excluded.day_of_week,month=excluded.month,quarter=excluded.quarter,year=excluded.year");con.execute("DROP TABLE _d")
        f=result["fact"][["order_item_key","order_code","date_key","store_code","product_code","customer_key","quantity","unit_price","total_amount"]].drop_duplicates("order_item_key")
        f.to_sql("_f",con,if_exists="replace",index=False);con.execute("INSERT INTO fact_sales SELECT * FROM _f WHERE 1 ON CONFLICT(order_item_key) DO UPDATE SET order_code=excluded.order_code,date_key=excluded.date_key,store_code=excluded.store_code,product_code=excluded.product_code,customer_key=excluded.customer_key,quantity=excluded.quantity,unit_price=excluded.unit_price,total_amount=excluded.total_amount");con.execute("DROP TABLE _f")
        rej=result["rejects"]
        if len(rej):
            rows=rej[["order_id","order_code","store_code","product_code","reject_reason"]].copy();rows=rows.rename(columns={"order_id":"source_order_id"});rows["source_payload"]=rej.astype(str).agg(" | ".join,axis=1).values
            rows.to_sql("_r",con,if_exists="replace",index=False);con.execute("INSERT OR IGNORE INTO reject_rows(source_order_id,order_code,store_code,product_code,reject_reason,source_payload) SELECT * FROM _r");con.execute("DROP TABLE _r")
        import uuid
        run_id=str(uuid.uuid4())
        con.executemany("INSERT INTO etl_quality(run_id,check_name,row_count,error_count,error_rate) VALUES(?,?,?,?,?)",[(run_id,x["check_name"],x["row_count"],x["error_count"],x["error_rate"]) for x in result["quality"]])
        count=con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    return {"fact_count":count,"run_id":run_id}
