with most_popular_country as (
    select country_name
    from {{ ref('fct_web_requests') }}
    group by country_name
    order by count(*) desc, country_name
    limit 1
),

companies_in_country as (
    select distinct wr.company_id
    from {{ ref('fct_web_requests') }} wr
        join most_popular_country pc on wr.country_name = pc.country_name
    where wr.company_id is not null
)

select
    p.product_name,
    sum(ordl.quantity) as order_quantity
from {{ ref('fct_order_lines') }} ordl
    join companies_in_country c on ordl.company_id = c.company_id
    join {{ ref('dim_product') }} p on ordl.product_id = p.product_id
group by p.product_name
order by order_quantity desc
limit 5