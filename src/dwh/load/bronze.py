from duckdb import connect

from dwh.config import WAREHOUSE, LANDING, ROOT


QUERY = """
    CREATE OR REPLACE TABLE raw_{} AS
    SELECT *, now() AS _loaded_at, ? AS _run_id, filename AS _source_file
    FROM read_parquet('{}/*.parquet', filename = true)
"""

def bronze(run_id: int = 0) -> None:
    with connect(WAREHOUSE) as con:
        for path in LANDING.iterdir():
            if path.name.startswith('rejects'):
                continue
            query = QUERY.format(path.name, path.relative_to(ROOT), [run_id])
            con.execute(query)

        con.sql("show all tables").show()
