import uuid
import psycopg2
from psycopg2.extras import Json
from pathlib import Path
import sys

# Allow imports from the same folder
sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def upsert_rows(
    table_name: str,
    primary_key: str,
    source_key: str,
    source_updated_field: str,
    rows: list,
    run_id: str,
    logical_date: str,
) -> int:
    """
    Upsert rows into a raw table using the mapped source key.
    """
    if not rows:
        return 0

    conn = get_connection()
    rows_loaded = 0

    try:
        with conn.cursor() as cur:
            for row in rows:
                if source_key not in row:
                    raise ValueError(
                        f"Source key '{source_key}' missing in row for table {table_name}: {row}"
                    )

                pk_value = row.get(source_key)
                updated_at = row.get(source_updated_field)

                query = f"""
                    INSERT INTO {table_name} (
                        {primary_key},
                        updated_at,
                        _run_id,
                        _logical_date,
                        _raw_payload
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ({primary_key})
                    DO UPDATE SET
                        updated_at = EXCLUDED.updated_at,
                        _run_id = EXCLUDED._run_id,
                        _logical_date = EXCLUDED._logical_date,
                        _ingested_at = NOW(),
                        _raw_payload = EXCLUDED._raw_payload;
                """

                cur.execute(
                    query,
                    (
                        pk_value,
                        updated_at,
                        run_id,
                        logical_date,
                        Json(row),
                    ),
                )
                rows_loaded += 1

        conn.commit()
        return rows_loaded

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


