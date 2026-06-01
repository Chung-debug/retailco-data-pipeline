select
    store_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_store_id,
    _raw_payload__team_id as team_id,
    _raw_payload__name as store_name,
    _raw_payload__city as city,
    _raw_payload__state as state,
    _raw_payload__address as address,
    _raw_payload__phone as phone,
    _raw_payload__manager_name as manager_name,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at,
    _raw_payload__opened_date as opened_date

from {{ source('retailco_raw', 'stores') }}