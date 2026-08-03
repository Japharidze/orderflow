import argparse

from dwh import metadata, transform
from dwh.load import bronze, landing

STAGES = ['landing', 'bronze', 'transform']
OPS = {
    'landing': landing,
    'bronze': bronze,
    'transform': transform}

def run(from_stage: str = "landing", restart: bool = False) -> None:
    metadata.init()

    if restart:
        last = metadata.last_run()
        if last is None or last["status"] != "failed":
            raise SystemExit("nothing to restart: the last run did not fail")
        run_id = last["run_id"]
        from_stage = last["from_stage"]
        done = metadata.completed_jobs(run_id)
        print(f"restarting run {run_id}, skipping {len(done)} finished jobs")
    else:
        run_id = metadata.start_run(from_stage)
        done = set()

    try:
        for stage in STAGES[STAGES.index(from_stage):]:
            OPS[stage].run(run_id, done)
        metadata.finish_run(run_id, "success")
    except Exception as e:
        metadata.finish_run(run_id, "failed", str(e))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="from_stage", choices=STAGES, default="landing")
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()
    run(args.from_stage, args.restart)