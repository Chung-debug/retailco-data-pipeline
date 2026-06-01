select
    order_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_order_id,
    _raw_payload__team_id as team_id,
    _raw_payload__store_id as store_id,
    _raw_payload__customer_id as customer_id,
    _raw_payload__employee_id as employee_id,
    _raw_payload__status as order_status,
    cast(_raw_payload__ordered_at as timestamp) as ordered_at,
    cast(_raw_payload__paid_at as timestamp) as paid_at,
    cast(_raw_payload__shipped_at as timestamp) as shipped_at,
    cast(_raw_payload__delivered_at as timestamp) as delivered_at,
    cast(_raw_payload__cancelled_at as timestamp) as cancelled_at,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at,
    cast(_raw_payload__total_amount as numeric) as total_amount,
    cast(_raw_payload__discount_amount as numeric) as discount_amount,
    _raw_payload__discount_code as discount_code

from {{ source('retailco_raw', 'orders') }}