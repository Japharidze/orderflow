select
    d.year,
    d.month_name,
    sum(o.line_amount) as sales
from {{ ref('fct_order_lines') }} o
    join {{ ref('dim_date') }} d on o.date_key = d.date_key
where
    d.date >= date_trunc('month', today()) - interval 12 month and
    d.date < date_trunc('month', today())
group by
    d.year, d.month, d.month_name
order by
    d.year, d.month asc