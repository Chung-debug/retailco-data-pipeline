select
    product_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_product_id,
    _raw_payload__team_id as team_id,
    _raw_payload__sku as sku,
    _raw_payload__name as product_name,
    _raw_payload__brand as brand,
    _raw_payload__category as category,
    _raw_payload__sub_category as sub_category,
    _raw_payload__supplier as supplier,
    cast(_raw_payload__cost_price as numeric) as cost_price,
    cast(_raw_payload__selling_price as numeric) as selling_price,
    cast(_raw_payload__effective_from as timestamp) as effective_from,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at,
    cast(_raw_payload__is_deleted as boolean) as is_deleted

from {{ source('retailco_raw', 'products') }}