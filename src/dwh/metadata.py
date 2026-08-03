from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace

from duckdb import connect

from dwh.config import SQL_DIR, WAREHOUSE


def init() -> None:
    """Create the metadata tables and close any run left behind by a crash."""
    with open(SQL_DIR / "metadata.sql") as f:
        sql = f.read()
    with connect(WAREHOUSE) as con:
        con.execute(sql)
        con.execute("""
            update job_runs
            set status = 'failed',
                finished_at = ?,
                error = 'abandoned: process did not finish'
            where status = 'running'
        """, [datetime.now()])
        con.execute("""
            update runs
            set status = 'failed',
                finished_at = ?,
                error = 'abandoned: process did not finish'
            where status = 'running'
        """, [datetime.now()])

def last_run() -> dict | None:
    with connect(WAREHOUSE) as con:
        row = con.execute(
            "select run_id, from_stage, status from runs order by run_id desc limit 1"
        ).fetchone()
    return {"run_id": row[0], "from_stage": row[1], "status": row[2]} if row else None

def start_run(from_stage: str) -> int:
    """Insert a running row for a pipeline run and return its id."""
    with connect(WAREHOUSE) as con:
        run_id = con.execute(
            """
            insert into runs (run_id, from_stage, status, started_at)
            values (nextval('run_id_seq'), ?, 'running', ?)
            returning run_id
            """,
            [from_stage, datetime.now()],
        ).fetchone()[0]
    return run_id


def finish_run(run_id: int, status: str, error: str | None = None) -> None:
    """Close a run row with its outcome."""
    with connect(WAREHOUSE) as con:
        con.execute(
            """
            update runs
            set status = ?, finished_at = ?, error = ?
            where run_id = ?
            """,
            [status, datetime.now(), error[:500] if error else None, run_id],
        )

def start_job(run_id: int, stage: str, job_name: str) -> int:
    """Insert a running row for a job and return its id."""
    with connect(WAREHOUSE) as con:
        job_run_id = con.execute(
            """
            insert into job_runs
                (job_run_id, run_id, stage, job_name, status, started_at)
            values (nextval('job_run_id_seq'), ?, ?, ?, 'running', ?)
            returning job_run_id
            """,
            [run_id, stage, job_name, datetime.now()],
        ).fetchone()[0]
    return job_run_id


def finish_job(
    job_run_id: int,
    status: str,
    rows_read: int | None = None,
    rows_written: int | None = None,
    rows_rejected: int | None = None,
    error: str | None = None,
) -> None:
    """Close a job row with its outcome and counts."""
    with connect(WAREHOUSE) as con:
        con.execute(
            """
            update job_runs
            set status = ?,
                finished_at = ?,
                rows_read = ?,
                rows_written = ?,
                rows_rejected = ?,
                error = ?
            where job_run_id = ?
            """,
            [
                status,
                datetime.now(),
                rows_read,
                rows_written,
                rows_rejected,
                error[:500] if error else None,
                job_run_id,
            ],
        )

def save_rejects(run_id: int, source: str, rows: list[dict]) -> None:
    """Store rejected rows with the reason they failed."""
    if not rows:
        return
    with connect(WAREHOUSE) as con:
        con.executemany(
            """
            insert into rejects (run_id, source, raw_row, reason, rejected_at)
            values (?, ?, ?, ?, ?)
            """,
            [[run_id, source, r["row"], r["reason"], datetime.now()] for r in rows],
        )

def completed_jobs(run_id: int) -> set[str]:
    """Job names that already succeeded in this run."""
    with connect(WAREHOUSE) as con:
        rows = con.execute(
            "select distinct job_name from job_runs where run_id = ? and status = 'success'",
            [run_id],
        ).fetchall()
    return {r[0] for r in rows}

@contextmanager
def job(run_id: int, stage: str, name: str):
    job_run_id = start_job(run_id, stage, name)
    counts = SimpleNamespace(rows_read=None, rows_written=None, rows_rejected=None)
    try:
        yield counts
    except Exception as e:
        finish_job(job_run_id, "failed", error=str(e), **vars(counts))
        raise
    else:
        finish_job(job_run_id, "success", **vars(counts))