select
    id as company_id,
    cuit,
    trim(name) as company_name,
    user_name as username,
    is_supplier
from {{ source('raw', 'raw_companies') }}