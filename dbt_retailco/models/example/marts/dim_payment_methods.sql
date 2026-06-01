select
    payment_method_id,
    source_payment_method_id,
    team_id,
    payment_method_name,
    provider,
    is_digital,
    created_at,
    updated_at,
    source_updated_at,
    ingested_at,
    run_id,
    logical_date

from {{ ref('stg_payment_methods') }}