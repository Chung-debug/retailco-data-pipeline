{% snapshot snap_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select
    customer_id,
    updated_at,
    ingested_at,
    run_id,
    logical_date,
    source_customer_id,
    team_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    state,
    segment,
    tier,
    registered_at,
    effective_from,
    created_at,
    source_updated_at,
    is_deleted
from {{ ref('stg_customers') }}

{% endsnapshot %}