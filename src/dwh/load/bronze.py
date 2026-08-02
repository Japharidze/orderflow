from duckdb import connect

from dwh.config import WAREHOUSE, LANDING, ROOT


QUERY = """
    CREATE OR REPLACE TABLE raw_{} AS
    SELECT * EXCLUDE(filename), now() AS _loaded_at, ? AS _run_id, filename as _source_file
    FROM read_parquet('{}/*.parquet', filename = true)
"""

def bronze(run_id: int = 0) -> None:
    with connect(WAREHOUSE) as con:
        for path in LANDING.iterdir():
            if path.name.startswith('rejects'):
                continue
            query = QUERY.format(path.name, path.relative_to(ROOT))
            con.execute(query, [run_id])
