select
    payment_id,
    source_payment_id,
    team_id,
    order_id,
    customer_id,
    payment_method_id,
    payment_status,
    payment_type,
    currency,
    reference,
    amount_paid,
    paid_at,
    created_at,
    updated_at,
    source_updated_at,
    ingested_at,
    run_id,
    logical_date

from {{ ref('stg_payments') }}