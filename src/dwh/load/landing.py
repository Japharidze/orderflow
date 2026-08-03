import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from dwh import metadata, schemas
from dwh.config import LANDING
from dwh.db import models
from dwh.extract import leads, table, weblog
from dwh.validate import split

DB_MODELS = [
    models.CatalogItem, models.Company, models.Customer,
    models.Product, models.Order, models.OrderLine]
DB_SCHEMAS = [
    schemas.CatalogItem, schemas.Company, schemas.Customer,
    schemas.Product, schemas.Order, schemas.OrderLine]
MODEL_NAMES = [obj.__tablename__.lower() for obj in DB_MODELS]

DB_ITERATOR_TUPLES = [(lambda m=model: table(m), schema) for model, schema in zip(DB_MODELS, DB_SCHEMAS)]
ITERATORS = {name : tup for name, tup in zip(MODEL_NAMES, DB_ITERATOR_TUPLES)}
ITERATORS = ITERATORS | {
    "weblog": (weblog, schemas.WeblogLine),
    "leads": (leads, schemas.Lead),
}

def _write_batch(rows: list[dict], dataset: str, batch_no: int) -> Path:
    out_dir = LANDING / dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"part-{batch_no:05d}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path

def _land(run_id: int, name: str, iterator: callable, schema: callable) -> None:
    """Land one dataset. Returns how many rows were kept and rejected."""
    path = LANDING / name
    if path.exists():
        shutil.rmtree(path)

    good_rows = bad_rows = 0
    for i, batch in enumerate(iterator()):
        good, bad = split(batch, schema)
        if good:
            _write_batch(good, name, i)
        if bad:
            metadata.save_rejects(run_id, name, bad)
        good_rows += len(good)
        bad_rows += len(bad)

    return good_rows + bad_rows, good_rows, bad_rows

def run(run_id: int, done: set[str]) -> None:
    """Extracts data from source files and lands them in the landing zone."""

    for name, (iterator, schema) in ITERATORS.items():
        if name in done:
            continue
        with metadata.job(run_id, "landing", name) as j:
            j.rows_read, j.rows_written, j.rows_rejected = _land(run_id, name, iterator, schema)