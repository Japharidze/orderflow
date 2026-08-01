from pathlib import Path

PG_URL = "postgresql+psycopg://dwh:dwh@localhost:5432/dwh_platform"

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
LANDING = DATA / "landing"
SOURCE = DATA / "source"