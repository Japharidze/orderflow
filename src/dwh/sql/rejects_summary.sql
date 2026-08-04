select source, reason, count(*) as rows
from rejects
where run_id = (select max(run_id) from runs)
group by source, reason
order by rows desc