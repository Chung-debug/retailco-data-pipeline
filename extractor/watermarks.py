import psycopg2
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    META_SCHEMA,
    WATERMARK_TABLE,
)


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_watermark(entity_name: str):
    query = f"""
        select last_successful_updated_at
        from {META_SCHEMA}.{WATERMARK_TABLE}
        where entity_name = %s;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (entity_name,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def mark_run_started(entity_name: str):
    query = f"""
        update {META_SCHEMA}.{WATERMARK_TABLE}
        set
            last_run_started_at = now(),
            last_run_status = 'running'
        where entity_name = %s;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (entity_name,))
        conn.commit()
    finally:
        conn.close()


def mark_run_success(entity_name: str, max_updated_at, rows_extracted: int, rows_loaded: int):
    query = f"""
        update {META_SCHEMA}.{WATERMARK_TABLE}
        set
            last_successful_updated_at = %s,
            last_run_completed_at = now(),
            last_run_status = 'success',
            rows_extracted = %s,
            rows_loaded = %s
        where entity_name = %s;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (max_updated_at, rows_extracted, rows_loaded, entity_name)
            )
        conn.commit()
    finally:
        conn.close()


def mark_run_failed(entity_name: str):
    query = f"""
        update {META_SCHEMA}.{WATERMARK_TABLE}
        set
            last_run_completed_at = now(),
            last_run_status = 'failed'
        where entity_name = %s;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (entity_name,))
        conn.commit()
    finally:
        conn.close()
