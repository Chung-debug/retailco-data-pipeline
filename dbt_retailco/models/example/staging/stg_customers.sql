select
    customer_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_customer_id,
    _raw_payload__team_id as team_id,
    _raw_payload__first_name as first_name,
    _raw_payload__last_name as last_name,
    _raw_payload__email as email,
    _raw_payload__phone as phone,
    _raw_payload__address as address,
    _raw_payload__city as city,
    _raw_payload__state as state,
    _raw_payload__segment as segment,
    _raw_payload__tier as tier,
    cast(_raw_payload__registered_at as timestamp) as registered_at,
    cast(_raw_payload__effective_from as timestamp) as effective_from,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at,
    cast(_raw_payload__is_deleted as boolean) as is_deleted

from {{ source('retailco_raw', 'customers') }}