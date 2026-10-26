import pandas as pd
def result(name, mask, total):
    errors=int(mask.fillna(True).sum()); return {"check_name":name,"row_count":int(total),"error_count":errors,"error_rate":round(errors/total,6) if total else 0.0}
def required_fields(df,fields):
    mask=df[fields].apply(lambda c:c.astype(str).str.strip().eq("")).any(axis=1);return result("required_fields",mask,len(df))
def valid_dates(df):
    mask=pd.to_datetime(df["sale_date"],errors="coerce").isna();return result("valid_sale_date",mask,len(df))
def positive_amounts(df):
    q=pd.to_numeric(df["quantity"],errors="coerce");p=pd.to_numeric(df["unit_price"],errors="coerce");mask=q.isna()|p.isna()|(q<=0)|(p<0);return result("positive_quantity_price",mask,len(df))
def valid_store_fk(df,stores):
    return result("store_foreign_key",~df["store_code"].isin(set(stores["store_code"])),len(df))
def valid_product_fk(df,products):
    return result("product_foreign_key",~df["product_code"].isin(set(products["product_code"])),len(df))
def unique_business_key(df):
    return result("unique_order_item_key",df.duplicated(["store_code","order_code","product_code"],keep="first"),len(df))
def run_checks(df,stores,products):
    return [required_fields(df,["store_code","order_code","sale_date","product_code","quantity","unit_price"]),valid_dates(df),positive_amounts(df),valid_store_fk(df,stores),valid_product_fk(df,products),unique_business_key(df)]
