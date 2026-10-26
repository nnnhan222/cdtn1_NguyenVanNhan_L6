from pathlib import Path
import pandas as pd

def extract_data(data_dir: Path):
    """Đọc các nguồn CSV của luồng doanh thu."""
    def read(name):
        path=data_dir/name
        if not path.exists(): raise FileNotFoundError(f"Thiếu tệp nguồn: {path}")
        return pd.read_csv(path,dtype=str,keep_default_na=False,encoding="utf-8-sig")
    return {"orders":read("orders_2024_2026(1).csv"),"items":read("order_items(1).csv"),"stores":read("stores(1).csv"),"products":read("products(1).csv"),"customers":read("customers_raw(1).csv")}

