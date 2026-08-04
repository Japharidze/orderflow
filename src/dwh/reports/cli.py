import argparse
from decimal import Decimal

from duckdb import connect
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from dwh.config import SQL_DIR, WAREHOUSE

NUMERIC = (int, float, Decimal)
BUSINESS = {
    "Monthly sales": "monthly_sales",
    "Top devices": "top_devices",
    "Top products in top country": "top_products_by_country",
}
STYLES = {
    "business": dict(
        box=box.SIMPLE_HEAD,
        header_style="bold cyan",
        row_styles=["", "dim"],
    ),
    "runs": dict(
        box=box.ROUNDED,
        header_style="bold blue",
        border_style="blue",
    ),
    "quality": dict(
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold yellow",
        border_style="yellow",
        row_styles=["", "dim"],
    ),
}
console = Console()

def _fmt(v) -> str:
    if isinstance(v, Decimal | float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)

def _sql(name: str) -> str:
    return (SQL_DIR / f"{name}.sql").read_text()

def _fetch(conn, query: str) -> list[dict]:
    result = conn.execute(query)
    columns = [d[0] for d in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]

def _get_table(title: str, rows: list[dict], style: str = "business") -> Table:
    table = Table(
        title=title,
        title_style="bold",
        caption_style="dim",
        **STYLES[style]
    )
    if not rows:
        table.title = f"{title} — no rows"
        return table
    for column, value in rows[0].items():
        table.add_column(column, justify="right" if isinstance(value, NUMERIC) else "left")
    for r in rows:
        table.add_row(*(_fmt(v) for v in r.values()))
    return table

def _print(tables: list[Table]) -> None:
    console.print(Padding(Columns(tables, padding=(0,4)), (1,10)))

def _print_business():
    with connect(WAREHOUSE) as conn:
        tables = []
        for title, name in BUSINESS.items():
            tables.append(_get_table(title, _fetch(conn, _sql(name)), "business"))
        _print(tables)

def _print_runs():
    with connect(WAREHOUSE) as conn:
        tables = [
            _get_table("Last runs", _fetch(conn, _sql("last_runs")), "runs"),
            _get_table("Jobs in the latest run", _fetch(conn, _sql("latest_jobs")), "runs"),
        ]
        _print(tables)

def _print_quality():
    with connect(WAREHOUSE) as conn:
        tables = [
            _get_table("Rejected rows", _fetch(conn, _sql("rejects_summary")), "quality"),
            _get_table("Examples", _fetch(conn, _sql("rejects_examples")), "quality"),
        ]
        _print(tables)

def run(section: str = "business") -> None:
    console.clear()
    if section in ("business", "all"):
        console.rule("[bold]Business reports")
        _print_business()
    if section in ("runs", "all"):
        console.rule("[bold]Run summary")
        _print_runs()
    if section in ("quality", "all"):
        console.rule("[bold]Data quality")
        _print_quality()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", choices=["business", "runs", "quality", "all"],
                        default="business")
    run(parser.parse_args().section)