from dwh import metadata, transform
from dwh.load import bronze, landing

STAGES = ['landing', 'bronze', 'transform']
OPS = {
    'landing': landing,
    'bronze': bronze,
    'transform': transform}

def run(from_stage: str = "landing") -> None:
    metadata.init()
    run_id = metadata.start_run(from_stage=from_stage)
    start = STAGES.index(from_stage)
    for stage in STAGES[start:]:
        try:
            OPS[stage].run(run_id=run_id)
        except Exception as e:
            metadata.finish_run(run_id, status="failed", error=str(e))
            raise
    metadata.finish_run(run_id, status="success")

if __name__ == "__main__":
    run()