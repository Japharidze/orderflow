from duckdb import connect

from dwh import metadata
from dwh.config import WAREHOUSE, LANDING, ROOT


QUERY = """
    CREATE OR REPLACE TABLE raw_{} AS
    SELECT * EXCLUDE(filename), now() AS _loaded_at, ? AS _run_id, filename as _source_file
    FROM read_parquet('{}/*.parquet', filename = true)
"""

def run(run_id: int, done: set[str]) -> None:
    """Load every landed dataset into a raw table."""
    if "bronze" in done:
        return
    with metadata.job(run_id, "bronze", "bronze") as j:
        tables = rows = 0
        with connect(WAREHOUSE) as con:
            for path in LANDING.iterdir():
                query = QUERY.format(path.name, path.relative_to(ROOT))
                con.execute(query, [run_id])
                rows += con.execute(f"select count(*) from raw_{path.name}").fetchone()[0]
                tables += 1
        j.rows_written = rows
    print(f"loaded {tables} tables, {rows} rows")