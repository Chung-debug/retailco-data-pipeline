select
    store_id,
    source_store_id,
    team_id,
    store_name,
    city,
    state,
    address,
    phone,
    manager_name,
    opened_date,
    created_at,
    updated_at,
    source_updated_at,
    ingested_at,
    run_id,
    logical_date

from {{ ref('stg_stores') }}