import re
import pandas as pd
from src.quality.checks import run_checks
def money(v):
    s=str(v).strip().replace("đ","").replace("Đ","").replace("₫","").replace(" ","")
    if not s:return None
    # Nguồn dùng số nguyên hoặc dấu chấm phân cách hàng nghìn.
    s=s.replace(".","").replace(",","")
    try:return float(s)
    except ValueError:return None
def date_value(v):
    s=str(v).strip()
    for fmt in ("%d/%m/%Y","%d-%m-%y","%Y.%m.%d","%Y-%m-%d"):
        try:return pd.to_datetime(s,format=fmt).date().isoformat()
        except (ValueError,TypeError):pass
    return None
def normalize_phone(v):
    s=re.sub(r"\D","",str(v))
    if s.startswith("0084"):s="0"+s[4:]
    elif s.startswith("84"):s="0"+s[2:]
    return s if len(s)==10 and s.startswith("0") else None
def transform_data(raw):
    orders=raw["orders"].copy();items=raw["items"].copy();stores=raw["stores"].copy();products=raw["products"].copy();customers=raw["customers"].copy()
    stores=stores.rename(columns={"store_code":"store_code","store_name":"store_name","thanh_pho":"city"})[["store_code","store_name","city"]].drop_duplicates("store_code")
    products=products.rename(columns={"product_code":"product_code","product_name":"product_name","nhom_san_pham":"category"})[["product_code","product_name","category"]].drop_duplicates("product_code")
    items["quantity"]=pd.to_numeric(items["so_luong"],errors="coerce");items["unit_price"]=items["don_gia"].map(money);items["item_total_source"]=items["thanh_tien"].map(money)
    # Gắn sản phẩm theo khóa product_id thực tế trong hai tệp.
    pmap=raw["products"].set_index("product_id")["product_code"].to_dict();items["product_code"]=items["product_id"].map(pmap)
    o=orders.rename(columns={"ma_don":"order_code","ma_cua_hang":"store_code","ngay":"sale_date_raw","ten_khach":"customer_name","so_dien_thoai":"phone","thanh_tien":"order_total_raw"})
    o["sale_date"]=o["sale_date_raw"].map(date_value);o["order_total_source"]=o["order_total_raw"].map(money)
    # orders là tổng đơn; order_items là grain sản phẩm. Ghép theo order_id, không dùng mã đơn trùng liên cửa hàng làm khóa.
    o["order_id"]=o["order_id"].astype(str);items["order_id"]=items["order_id"].astype(str)
    df=o.merge(items,on="order_id",how="left",suffixes=("_order","_item"),validate="one_to_many")
    df["order_code"]=df["order_code"].fillna("");df["store_code"]=df["store_code"].fillna("")
    df["customer_name"]=df["customer_name"].fillna("").astype(str).str.strip();df["phone"]=df["phone"].map(normalize_phone)
    # Quy tắc QT-02: thành tiền fact là quantity * unit_price.
    df["total_amount"]=(df["quantity"]*df["unit_price"]).round(2)
    df["total_amount"] = df["total_amount"].fillna(df["order_total_source"])
    df["order_item_key"]=df["store_code"].astype(str)+"|"+df["order_code"].astype(str)+"|"+df["product_code"].fillna("").astype(str)
    checks=run_checks(df,stores,products)
    df["reject_reason"]=""
    for c in checks:
        if c["check_name"]=="required_fields":
            bad=df[["store_code","order_code","sale_date","product_code","quantity","unit_price"]].apply(lambda x:x.astype(str).str.strip().eq("")).any(axis=1);df.loc[bad,"reject_reason"]+="missing_required;"
        elif c["check_name"]=="valid_sale_date":df.loc[df["sale_date"].isna(),"reject_reason"]+="invalid_date;"
        elif c["check_name"]=="positive_quantity_price":df.loc[df["quantity"].isna()|(df["quantity"]<=0)|df["unit_price"].isna()|(df["unit_price"]<0),"reject_reason"]+="invalid_quantity_price;"
        elif c["check_name"]=="store_foreign_key":df.loc[~df["store_code"].isin(stores.store_code),"reject_reason"]+="unknown_store;"
        elif c["check_name"]=="product_foreign_key":df.loc[~df["product_code"].isin(products.product_code),"reject_reason"]+="unknown_product;"
        elif c["check_name"]=="unique_order_item_key":df.loc[df.duplicated("order_item_key",keep="first"),"reject_reason"]+="duplicate_business_key;"
    rejects=df[df.reject_reason.ne("")].copy();clean=df[df.reject_reason.eq("")].copy()
    clean=clean.merge(stores,on="store_code",how="left").merge(products,on="product_code",how="left")
    clean["customer_key"]=clean["phone"].fillna("UNKNOWN")
    clean["sale_date"]=pd.to_datetime(clean["sale_date"],errors="coerce")
    clean=clean[clean["sale_date"].notna()].copy()
    clean["date_key"]=clean["sale_date"].dt.strftime("%Y%m%d").astype("int64")
    clean["day_of_week"]=clean["sale_date"].dt.day_name();clean["month"]=clean["sale_date"].dt.month;clean["quarter"]=clean["sale_date"].dt.quarter;clean["year"]=clean["sale_date"].dt.year
    return {"fact":clean,"rejects":rejects,"stores":stores,"products":products,"customers":customers,"quality":checks}
