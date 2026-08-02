from pathlib import Path

PG_URL = "postgresql+psycopg://b2b:b2b@localhost:5432/b2b_platform"

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
LANDING = DATA / "landing"
SOURCE = DATA / "source"

LANDING.mkdir(parents=True, exist_ok=True)
SOURCE.mkdir(parents=True, exist_ok=True)

WEBLOG_FILE = SOURCE / "weblog.log"
LEADS_FILE = SOURCE / "marketing_leads.xlsx"

WAREHOUSE = DATA / "dwh.db"