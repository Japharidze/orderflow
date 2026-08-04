import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PG_URL = os.environ.get("PG_URL")

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "src" / "dwh" / "sql"
DATA = ROOT / "data"
LANDING = DATA / "landing"
SOURCE = DATA / "source"
DBT_DIR = ROOT / "dbt_project"

LANDING.mkdir(parents=True, exist_ok=True)
SOURCE.mkdir(parents=True, exist_ok=True)

WEBLOG_FILE = SOURCE / "weblog.log"
LEADS_FILE = SOURCE / "marketing_leads.xlsx"

WAREHOUSE = DATA / "dwh.db"