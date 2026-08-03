with
    most_popular_country as (
        select
            wr.country_name
        from
            {{ ref('fct_web_requests') }} wr
        group by
            wr.country_name
        order by
            count(*) desc, wr.country_name
        limit
            1
    )

select
    p.product_name,
    sum(ordl.quantity) as order_quantity
from
    {{ ref('fct_web_requests') }} wr
    join most_popular_country pc on wr.country_name = pc.country_name 
    join {{ ref('fct_order_lines') }} ordl on wr.company_id = ordl.company_id
    join {{ ref('dim_product') }} p on ordl.product_id = p.product_id
group by
    p.product_name
order by
    sum(ordl.quantity) desc
limit 5