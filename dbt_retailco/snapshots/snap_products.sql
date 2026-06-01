{% snapshot snap_products %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select
    product_id,
    updated_at,
    ingested_at,
    run_id,
    logical_date,
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
    source_updated_at,
    is_deleted
from {{ ref('stg_products') }}

{% endsnapshot %}