select
    wl.requested_at,
    cast(strftime(wl.requested_at, '%Y%m%d') as integer) as date_key,
    wl.username,
    wl.ip,
    cb.country_name,
    wl.user_agent,
    case
        when regexp_matches(wl.user_agent, '(?i)bot|crawler|spider|slurp') then 'bot'
        when regexp_matches(wl.user_agent, '(?i)ipad|tablet')             then 'tablet'
        when wl.user_agent like '%Android%'
            and wl.user_agent not like '%Mobile%'                        then 'tablet'
        when regexp_matches(wl.user_agent, '(?i)mobile|iphone|android')   then 'mobile'
        else 'desktop'
    end as device_type

from {{ source('raw', 'raw_weblog') }} wl
    left join {{ ref('country_blocks') }} cb
     on split_part(wl.ip, '.', 1) || '.' || split_part(wl.ip, '.', 2) = cb.ip_prefix