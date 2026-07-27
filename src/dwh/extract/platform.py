from collections.abc import Iterator

from sqlalchemy import text

from dwh.db.models import engine

BATCH = 5000

QUERY = """
select ol.id, o.id as order_id, o.company_id, o.customer_id,
       ol.product_id, ol.quantity, ol.unit_price, o.ordered_at
from order_lines ol
join orders o on o.id = ol.order_id
"""


def extract_order_lines() -> Iterator[list[dict]]:
    """Yield batches of order-line rows so memory stays flat."""
    with engine().connect() as conn:
        result = conn.execution_options(stream_results=True).execute(text(QUERY))   # stream results in case of big data
        while batch := result.fetchmany(BATCH):
            yield [dict(row._mapping) for row in batch]