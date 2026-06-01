select
    product_id,
    source_product_id,
    team_id,
    sku,
    product_name,
    brand,
    category,
    sub_category,
    supplier,
    cost_price,
    selling_price,
    effective_from,
    created_at,
    updated_at,
    source_updated_at,
    is_deleted,

    dbt_valid_from,
    dbt_valid_to,
    dbt_scd_id,
    dbt_updated_at

from {{ ref('snap_products') }}
where dbt_valid_to is null