import dlt
import pandas as pd
from sqlalchemy import create_engine

from config import (
    LAKE_DB_HOST,
    LAKE_DB_PORT,
    LAKE_DB_NAME,
    LAKE_DB_USER,
    LAKE_DB_PASSWORD,
    WAREHOUSE_DB_HOST,
    WAREHOUSE_DB_PORT,
    WAREHOUSE_DB_NAME,
    WAREHOUSE_DB_USER,
    WAREHOUSE_DB_PASSWORD,
)

ENTITIES = [
    "stores",
    "employees",
    "payment_methods",
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "inventory_movements",
]


def lake_engine():
    return create_engine(
        f"postgresql://{LAKE_DB_USER}:{LAKE_DB_PASSWORD}@{LAKE_DB_HOST}:{LAKE_DB_PORT}/{LAKE_DB_NAME}"
    )


def warehouse_destination():
    return dlt.destinations.postgres(
        credentials=f"postgresql://{WAREHOUSE_DB_USER}:{WAREHOUSE_DB_PASSWORD}@{WAREHOUSE_DB_HOST}:{WAREHOUSE_DB_PORT}/{WAREHOUSE_DB_NAME}"
    )


def load_entity(entity_name: str):
    engine = lake_engine()
    query = f"select * from raw.{entity_name}"
    df = pd.read_sql(query, engine)

    pipeline = dlt.pipeline(
        pipeline_name="retailco_checkpoint3",
        destination=warehouse_destination(),
        dataset_name="raw",
    )

    load_info = pipeline.run(
        df.to_dict(orient="records"),
        table_name=entity_name,
        write_disposition="replace",
    )

    return load_info


def load_all_entities():
    results = {}
    for entity in ENTITIES:
        print(f"Loading {entity}...")
        results[entity] = load_entity(entity)
    return results


if __name__ == "__main__":
    results = load_all_entities()
    print(results)