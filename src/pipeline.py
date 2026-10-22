import os
from sqlalchemy import create_engine
from src.extract.extractor import extract_data
from src.transform.transformer import transform_data
from src.quality.checker import check_quality
from src.load.loader import load_data
import sys

def run_pipeline():
    data_dir = os.environ.get('DATA_DIR', './data/mau')
    dwh_url = os.environ.get('DWH_URL', 'postgresql+psycopg://dwh_user:doi_mat_khau_nay_truoc_khi_dung_that@localhost:5433/mekong_dwh')
    
    print("1. Extracting data...")
    df_raw = extract_data(data_dir)
    
    print("2. Transforming data...")
    df_transformed = transform_data(df_raw)
    
    print("3. Checking quality...")
    df_valid, df_error, metrics = check_quality(df_transformed)
    
    print(f"Metrics: {metrics}")
    if metrics['total_rows'] == 0 or (len(df_valid) / len(df_raw) < 0.5):
        print("Dữ liệu lỗi quá nhiều. Dừng pipeline!")
        sys.exit(2)
        
    print("4. Loading to DWH...")
    engine = create_engine(dwh_url)
    load_data(df_valid, df_error, engine)
    print("Pipeline hoàn tất thành công!")

if __name__ == "__main__":
    run_pipeline()
