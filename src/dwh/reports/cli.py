import time
from decimal import Decimal

from duckdb import connect
from rich import box
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich.padding import Padding

from dwh.config import WAREHOUSE

NUMERIC = (int, float, Decimal)
BUSINESS = {
    "Monthly sales": "select * from rpt_monthly_sales",
    "Top devices": "select * from rpt_top_devices",
    "Top products in top country": "select * from rpt_top_products_by_country",
}
console = Console()

def _fmt(v) -> str:
    if isinstance(v, Decimal | float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)

def _fetch(conn, query: str) -> list[dict]:
    result = conn.execute(query)
    columns = [d[0] for d in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]

def _get_table(title: str, rows: list[dict]) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        header_style="bold cyan",
        row_styles=["", "dim"],
        title_style="bold",
        caption_style="dim",
    )
    for column, value in rows[0].items():
        table.add_column(column, justify="right" if isinstance(value, NUMERIC) else "left")
    for r in rows:
        table.add_row(*(_fmt(v) for v in r.values()))
    return table

def run():
    with connect(WAREHOUSE) as conn:
        console.clear()
        console.rule("[bold]Business reports")
        tables = []
        for title, query in BUSINESS.items():
            tables.append(_get_table(title, _fetch(conn, query)))
        console.print(Padding(Columns(tables, padding=(0,4), expand=True), (2,30)))

if __name__ == '__main__':
    run()