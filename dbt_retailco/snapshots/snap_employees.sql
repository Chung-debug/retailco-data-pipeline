{% snapshot snap_employees %}

{{
    config(
        target_schema='snapshots',
        unique_key='employee_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select
    employee_id,
    updated_at,
    ingested_at,
    run_id,
    logical_date,
    source_employee_id,
    team_id,
    store_id,
    first_name,
    last_name,
    email,
    role,
    hired_date,
    created_at,
    source_updated_at,
    is_deleted
from {{ ref('stg_employees') }}

{% endsnapshot %}