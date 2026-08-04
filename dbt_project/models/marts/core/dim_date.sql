with days as (
    select unnest(generate_series(
        make_date(year(today()) - 1, 1, 1),
        make_date(year(today()) + 1, 1, 1),
        interval 1 day
    ))::date as d
)
select
    cast(strftime(d, '%Y%m%d') as integer) as date_key,
    d as date,
    year(d)::varchar as year,
    month(d) as month,
    monthname(d) as month_name,
    day(d) as day
from days