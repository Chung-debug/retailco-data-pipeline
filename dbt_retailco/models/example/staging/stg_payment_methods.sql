select
    payment_method_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_payment_method_id,
    _raw_payload__team_id as team_id,
    _raw_payload__name as payment_method_name,
    _raw_payload__provider as provider,
    cast(_raw_payload__is_digital as boolean) as is_digital,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at

from {{ source('retailco_raw', 'payment_methods') }}