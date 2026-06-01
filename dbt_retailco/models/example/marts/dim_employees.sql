select
    employee_id,
    source_employee_id,
    team_id,
    store_id,
    first_name,
    last_name,
    email,
    role,
    hired_date,
    created_at,
    updated_at,
    source_updated_at,
    is_deleted,

    dbt_valid_from,
    dbt_valid_to,
    dbt_scd_id,
    dbt_updated_at

from {{ ref('snap_employees') }}
where dbt_valid_to is null