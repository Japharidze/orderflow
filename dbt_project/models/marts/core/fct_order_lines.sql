select
    o.order_id,
    ol.orderline_id,
    o.date_key,
    o.company_id,
    ol.product_id,
    ol.quantity,
    ol.unit_price * ol.quantity as line_amount
from
    {{ ref('stg_orders') }} o
    join {{ ref('stg_order_lines') }} ol on o.order_id = ol.order_id