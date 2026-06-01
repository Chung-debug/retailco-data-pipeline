select
    customer_id,
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
    updated_at,
    source_updated_at,
    is_deleted,

    dbt_valid_from,
    dbt_valid_to,
    dbt_scd_id,
    dbt_updated_at

from {{ ref('snap_customers') }}
where dbt_valid_to is null