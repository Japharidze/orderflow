select source, reason, left(raw_row, 60) as example
from rejects
where run_id = (select max(run_id) from runs)
qualify row_number() over (partition by source, reason order by rejected_at) <= 2