select
    inventory_movement_id,
    cast(updated_at as timestamp) as updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    _run_id as run_id,
    cast(_logical_date as date) as logical_date,

    _raw_payload__id as source_inventory_movement_id,
    _raw_payload__team_id as team_id,
    _raw_payload__store_id as store_id,
    _raw_payload__product_id as product_id,
    _raw_payload__movement_type as movement_type,
    _raw_payload__reference_type as reference_type,
    _raw_payload__reference_id as reference_id,
    cast(_raw_payload__quantity as integer) as quantity,
    cast(_raw_payload__moved_at as timestamp) as moved_at,
    cast(_raw_payload__created_at as timestamp) as created_at,
    cast(_raw_payload__updated_at as timestamp) as source_updated_at,
    _raw_payload__notes as notes

from {{ source('retailco_raw', 'inventory_movements') }}