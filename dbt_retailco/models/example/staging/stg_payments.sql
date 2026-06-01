select
    payment_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_payment_id,
    _raw_payload__team_id as team_id,
    _raw_payload__order_id as order_id,
    _raw_payload__customer_id as customer_id,
    _raw_payload__payment_method_id as payment_method_id,
    _raw_payload__status as payment_status,
    _raw_payload__payment_type as payment_type,
    _raw_payload__currency as currency,
    _raw_payload__reference as reference,
    cast(_raw_payload__amount_paid as numeric) as amount_paid,
    cast(_raw_payload__paid_at as timestamp) as paid_at,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at

from {{ source('retailco_raw', 'payments') }}