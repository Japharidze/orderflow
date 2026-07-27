from pathlib import Path

PG_URL = "postgresql+psycopg://b2b:b2b@localhost:5432/b2b_platform"

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
LANDING = DATA / "landing"