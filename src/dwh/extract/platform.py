from collections.abc import Iterator

from sqlalchemy import select

from dwh.db.models import Base, engine

BATCH = 5000

def table(model: type[Base]) -> Iterator[list[dict]]:
    """Yield batches of rows from a source table."""
    with engine().connect() as conn:
        result = conn.execution_options(stream_results=True).execute(select(model))
        while batch := result.fetchmany(BATCH):
            yield [dict(row._mapping) for row in batch]