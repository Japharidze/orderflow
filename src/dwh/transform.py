import subprocess

from dwh import metadata
from dwh.config import DBT_DIR


def _dbt(*args: str) -> None:
    subprocess.run(["dbt", *args, "--profiles-dir", "."], cwd=DBT_DIR, check=True)


def run(run_id: int) -> None:
    """Build the warehouse models and run the data tests."""
    with metadata.job(run_id, "transform", "dbt_run"):
        _dbt("run")

    with metadata.job(run_id, "transform", "dbt_test"):
        _dbt("test")