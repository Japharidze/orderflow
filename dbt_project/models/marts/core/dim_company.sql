select
    company_id,
    username,
    is_supplier
from
    {{ ref('stg_companies') }}