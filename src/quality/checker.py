import pandas as pd

def check_quality(df: pd.DataFrame) -> tuple:
    """Thực hiện 5 hàm đo chất lượng, trả về df hợp lệ, df lỗi và báo cáo."""
    rejects = []
    
    # 1. Thiếu mã đơn hàng
    mask_no_order = df['order_code'].isna() | (df['order_code'] == '')
    # 2. Số lượng không hợp lệ (<= 0)
    mask_inv_qty = df['quantity'] <= 0
    # 3. Đơn giá không hợp lệ (<= 0)
    mask_inv_price = df['unit_price'] <= 0
    # 4. Thiếu ngày bán
    mask_no_date = df['date_key'] == 0
    # 5. Thiếu thông tin khách hàng (SDT quá ngắn)
    mask_inv_phone = df['customer_phone'].str.len() < 10

    # Gom các dòng lỗi
    error_mask = mask_no_order | mask_inv_qty | mask_inv_price | mask_no_date | mask_inv_phone
    
    df_valid = df[~error_mask].copy()
    df_error = df[error_mask].copy()
    
    # Ghi nhận lý do reject
    if not df_error.empty:
        df_error['ly_do'] = 'Lỗi dữ liệu: '
        df_error.loc[mask_no_order, 'ly_do'] += 'Thiếu mã đơn; '
        df_error.loc[mask_inv_qty, 'ly_do'] += 'Số lượng <=0; '
        df_error.loc[mask_inv_price, 'ly_do'] += 'Đơn giá <=0; '
        df_error.loc[mask_no_date, 'ly_do'] += 'Sai định dạng ngày; '
        df_error.loc[mask_inv_phone, 'ly_do'] += 'SĐT sai định dạng; '

    metrics = {
        'total_rows': len(df),
        'missing_order_rate': mask_no_order.sum() / len(df) if len(df) else 0,
        'invalid_qty_rate': mask_inv_qty.sum() / len(df) if len(df) else 0,
        'invalid_price_rate': mask_inv_price.sum() / len(df) if len(df) else 0,
        'invalid_date_rate': mask_no_date.sum() / len(df) if len(df) else 0,
        'invalid_phone_rate': mask_inv_phone.sum() / len(df) if len(df) else 0
    }
    
    return df_valid, df_error, metrics
