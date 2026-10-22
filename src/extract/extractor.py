import pandas as pd
import glob
import os

def extract_data(data_dir: str) -> pd.DataFrame:
    """Đọc toàn bộ file CSV thô, KHÔNG biến đổi."""
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not all_files:
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu nào trong {data_dir}")
    
    df_list = [pd.read_csv(f) for f in all_files]
    return pd.concat(df_list, ignore_index=True)
