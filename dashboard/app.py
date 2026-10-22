import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Mekong CRM Dashboard", layout="wide")

dwh_url = os.environ.get('DWH_URL', 'postgresql+psycopg://dwh_user:doi_mat_khau_nay_truoc_khi_dung_that@localhost:5433/mekong_dwh')

@st.cache_data(ttl=60)
def load_data_from_db():
    engine = create_engine(dwh_url)
    query = """
        SELECT d.store_name, dt.full_date, f.total_amount 
        FROM fact_sales f
        JOIN dim_store d ON f.store_id = d.store_id
        JOIN dim_date dt ON f.date_key = dt.date_key
    """
    try:
        df = pd.read_sql(query, engine)
        return df, None
    except Exception as e:
        return None, "Lỗi kết nối Kho dữ liệu" # Không in chuỗi kết nối ra ngoài

st.title("Mekong Mobile - Báo cáo Doanh thu")

# Trạng thái 1: Đang tải
with st.spinner("Đang truy xuất dữ liệu từ Data Warehouse..."):
    df, error = load_data_from_db()

# Trạng thái 2: Lỗi
if error:
    st.error(error)
    if st.button("Thử lại"):
        st.cache_data.clear()
        st.rerun()
# Trạng thái 3: Rỗng hoặc có dữ liệu
elif df is not None:
    if df.empty:
        st.warning("Kho dữ liệu hiện chưa có dữ liệu bán hàng. Vui lòng chạy Pipeline ETL.")
    else:
        st.success("Tải dữ liệu thành công!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Doanh thu theo ngày")
            daily_rev = df.groupby('full_date')['total_amount'].sum().reset_index()
            st.line_chart(data=daily_rev, x='full_date', y='total_amount')
            
        with col2:
            st.subheader("Top Cửa hàng doanh thu cao nhất")
            store_rev = df.groupby('store_name')['total_amount'].sum().sort_values(ascending=False).head(5)
            st.bar_chart(store_rev)
