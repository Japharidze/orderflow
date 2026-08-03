select
    wr.device_type,
    count(*) as log_quantity
from
    {{ ref('fct_web_requests') }} wr
    join {{ ref('dim_company') }} c on wr.company_id = c.company_id
where
    not c.is_supplier
group by
    wr.device_type
order by
    count(*) desc
limit
    5