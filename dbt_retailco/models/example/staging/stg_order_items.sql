select
    order_item_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_order_item_id,
    _raw_payload__team_id as team_id,
    _raw_payload__order_id as order_id,
    _raw_payload__product_id as product_id,
    cast(_raw_payload__quantity as integer) as quantity,
    cast(_raw_payload__unit_price as numeric) as unit_price,
    cast(_raw_payload__discount_pct as numeric) as discount_pct,
    cast(_raw_payload__line_total as numeric) as line_total,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at

from {{ source('retailco_raw', 'order_items') }}