from pathlib import Path
import json
from src.extract.extractor import extract_data
from src.transform.transformer import transform_data
from src.load.loader import load_data
def run(data_dir=Path("data/raw"),db_path=Path("data/warehouse.sqlite")):
    raw=extract_data(Path(data_dir));result=transform_data(raw);loaded=load_data(result,Path(db_path))
    Path("output").mkdir(exist_ok=True)
    Path("output/quality_report.json").write_text(json.dumps({"run_id":loaded["run_id"],"loaded_fact_rows":len(result["fact"]),"rejected_rows":len(result["rejects"]),"checks":result["quality"]},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"success","loaded_fact_rows":len(result["fact"]),"reject_rows":len(result["rejects"]),**loaded},ensure_ascii=False,indent=2))
if __name__=="__main__":run()
