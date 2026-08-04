select run_id, from_stage, status, started_at, finished_at
from runs
order by run_id desc
limit 5