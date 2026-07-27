from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from dwh.config import LANDING


def write_batch(rows: list[dict], dataset: str, batch_no: int) -> Path:
    out_dir = LANDING / dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"part-{batch_no:05d}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path