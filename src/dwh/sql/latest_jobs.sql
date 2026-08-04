select stage, job_name,
        case status when 'success' then '[green]success[/]'
                    else '[red]' || status || '[/]' end as status,
        rows_read, rows_written, rows_rejected,
        datediff('millisecond', started_at, finished_at) as ms
from job_runs
where run_id = (select max(run_id) from runs)
order by job_run_id