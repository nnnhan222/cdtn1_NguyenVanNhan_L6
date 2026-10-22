import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa dữ liệu theo QT-01, QT-02 từ BT1."""
    df_clean = df.copy()
    
    # 1. Chuẩn hóa ngày (chuyển về datetime)
    df_clean['order_date'] = pd.to_datetime(df_clean['order_date'], errors='coerce')
    df_clean['date_key'] = df_clean['order_date'].dt.strftime('%Y%m%d').fillna(0).astype(int)
    
    # 2. Chuẩn hóa SĐT (QT-01: 10 số bắt đầu bằng 0)
    df_clean['customer_phone'] = df_clean['customer_phone'].astype(str).str.replace(r'\D', '', regex=True)
    df_clean['customer_phone'] = df_clean['customer_phone'].apply(
        lambda x: '0' + x[2:] if x.startswith('84') else ('0' + x if not x.startswith('0') else x)
    )
    
    # 3. Tính lại thành tiền (QT-02: Thành tiền = Số lượng x Đơn giá)
    df_clean['quantity'] = pd.to_numeric(df_clean['quantity'], errors='coerce').fillna(0)
    df_clean['unit_price'] = pd.to_numeric(df_clean['unit_price'], errors='coerce').fillna(0)
    df_clean['total_amount'] = df_clean['quantity'] * df_clean['unit_price']
    
    return df_clean
