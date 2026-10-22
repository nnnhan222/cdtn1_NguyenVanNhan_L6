import pandas as pd
from src.transform.transformer import transform_data
from src.quality.checker import check_quality

def test_luong_dung():
    """Luồng đúng: Xử lý dòng dữ liệu hoàn toàn hợp lệ."""
    df = pd.DataFrame([{
        'order_code': 'ORD01', 'order_date': '2026-10-12', 'customer_phone': '0901234567',
        'quantity': 2, 'unit_price': 150000, 'store_code': 'ST01', 'product_code': 'P01'
    }])
    df_trans = transform_data(df)
    df_valid, df_err, metrics = check_quality(df_trans)
    
    assert len(df_valid) == 1
    assert len(df_err) == 0
    assert df_valid.iloc[0]['total_amount'] == 300000

def test_gia_tri_bien():
    """Giá trị biên: SĐT có định dạng +84 (QT-01)."""
    df = pd.DataFrame([{
        'order_code': 'ORD02', 'order_date': '2026-10-12', 'customer_phone': '+84901234567',
        'quantity': 1, 'unit_price': 100, 'store_code': 'ST', 'product_code': 'P'
    }])
    df_trans = transform_data(df)
    assert df_trans.iloc[0]['customer_phone'] == '0901234567'

def test_du_lieu_sai():
    """Dữ liệu sai: Số lượng âm (phải vào bảng reject)."""
    df = pd.DataFrame([{
        'order_code': 'ORD03', 'order_date': '2026-10-12', 'customer_phone': '0901234567',
        'quantity': -5, 'unit_price': 100, 'store_code': 'ST', 'product_code': 'P'
    }])
    df_trans = transform_data(df)
    df_valid, df_err, metrics = check_quality(df_trans)
    
    assert len(df_valid) == 0
    assert len(df_err) == 1
    assert 'Số lượng <=0' in df_err.iloc[0]['ly_do']
