select
    id as product_id,
    trim(name) as product_name
from {{ source('raw', 'raw_products') }}