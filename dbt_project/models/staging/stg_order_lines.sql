select
    id as orderline_id,
    order_id,
    product_id,
    unit_price,
    quantity
from {{ source('raw', 'raw_order_lines') }}
