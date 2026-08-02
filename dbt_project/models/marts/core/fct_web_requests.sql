select
    wl.date_key,
    c.company_id,
    wl.country_name,
    wl.device_type
from
    {{ ref('stg_weblog' )}} wl
    left join {{ ref('stg_companies') }} c on wl.username = c.username