select
    id as order_id,
    ordered_at,
    cast(strftime(ordered_at, '%Y%m%d') as integer) as date_key,
    company_id
from {{ source('raw', 'raw_orders') }}