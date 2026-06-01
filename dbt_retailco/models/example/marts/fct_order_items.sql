select
    order_item_id,
    source_order_item_id,
    team_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct,
    line_total,
    created_at,
    updated_at,
    source_updated_at,
    ingested_at,
    run_id,
    logical_date

from {{ ref('stg_order_items') }}