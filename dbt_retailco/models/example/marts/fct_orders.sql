select
    order_id,
    source_order_id,
    team_id,
    store_id,
    customer_id,
    employee_id,
    order_status,
    ordered_at,
    paid_at,
    shipped_at,
    delivered_at,
    cancelled_at,
    created_at,
    updated_at,
    source_updated_at,
    total_amount,
    discount_amount,
    discount_code,
    ingested_at,
    run_id,
    logical_date

from {{ ref('stg_orders') }}