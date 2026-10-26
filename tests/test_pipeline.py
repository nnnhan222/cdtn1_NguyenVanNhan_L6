import sqlite3
import tempfile
import unittest
from pathlib import Path
from src.pipeline import run
from src.transform.transformer import date_value, normalize_phone

ROOT=Path(__file__).resolve().parents[1]
class PipelineTests(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(date_value('17/08/2025'),'2025-08-17')
        self.assertEqual(normalize_phone('+84 896 790 293'),'0896790293')
    def test_boundary_date(self):
        self.assertEqual(date_value('1-1-24'),'2024-01-01')
    def test_bad_date_rejected_without_crash(self):
        self.assertIsNone(date_value('not-a-date'))
    def test_second_load_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'dw.sqlite'
            run(ROOT/'data/raw',db);run(ROOT/'data/raw',db)
            with sqlite3.connect(db) as c:
                self.assertEqual(c.execute('select count(*) from fact_sales').fetchone()[0],35492)
                self.assertGreater(c.execute('select count(*) from reject_rows').fetchone()[0],0)
if __name__=='__main__':unittest.main()
