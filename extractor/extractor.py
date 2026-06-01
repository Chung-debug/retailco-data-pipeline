import uuid
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from entities import ENTITIES
from client import ERPClient
from loaders import upsert_rows
from watermarks import (
    get_watermark,
    mark_run_started,
    mark_run_success,
    mark_run_failed,
)


def parse_updated_at(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def extract_entity(entity: dict, logical_date: str) -> dict:
    entity_name = entity["name"]
    endpoint = entity["endpoint"]
    table_name = entity["table"]
    primary_key = entity["primary_key"]
    source_key = entity["source_key"]
    source_updated_field = entity["source_updated_field"]

    print(f"\n--- Extracting {entity_name} ---")

    client = ERPClient()
    run_id = str(uuid.uuid4())

    current_watermark = get_watermark(entity_name)
    updated_after = current_watermark.isoformat() if current_watermark else None

    print(f"Current watermark: {current_watermark}")
    print(f"Updated after: {updated_after}")

    mark_run_started(entity_name)

    total_rows_extracted = 0
    total_rows_loaded = 0
    max_updated_at = current_watermark
    cursor = None
    page_num = 1

    try:
        while True:
            request_updated_after = updated_after if cursor is None else None

            payload = client.get_page(
                endpoint=endpoint,
                cursor=cursor,
                updated_after=request_updated_after,
                page_num=page_num,
            )

            data = payload.get("data", [])
            meta = payload.get("meta", {})

            page_rows = len(data)
            total_rows_extracted += page_rows

            print(
                f"Page {page_num}: fetched {page_rows} rows | total extracted: {total_rows_extracted}"
            )

            page_rows_loaded = upsert_rows(
                table_name=table_name,
                primary_key=primary_key,
                source_key=source_key,
                source_updated_field=source_updated_field,
                rows=data,
                run_id=run_id,
                logical_date=logical_date,
            )

            total_rows_loaded += page_rows_loaded

            page_updated_values = [
                parse_updated_at(row.get(source_updated_field))
                for row in data
                if row.get(source_updated_field)
            ]

            if page_updated_values:
                page_max = max(page_updated_values)
                if max_updated_at is None or page_max > max_updated_at:
                    max_updated_at = page_max

            has_more = meta.get("has_more", False)
            cursor = meta.get("cursor")

            if not has_more:
                print(f"Completed pagination | total extracted: {total_rows_extracted}")
                break

            page_num += 1

        mark_run_success(
            entity_name=entity_name,
            max_updated_at=max_updated_at,
            rows_extracted=total_rows_extracted,
            rows_loaded=total_rows_loaded,
        )

        print(f"Rows extracted: {total_rows_extracted}")
        print(f"Rows loaded: {total_rows_loaded}")
        print(f"New watermark: {max_updated_at}")

        return {
            "entity_name": entity_name,
            "status": "success",
            "rows_extracted": total_rows_extracted,
            "rows_loaded": total_rows_loaded,
            "watermark": max_updated_at,
        }

    except Exception as e:
        mark_run_failed(entity_name)
        print(f"Extraction failed for {entity_name}: {e}")
        raise


def extract_all_entities(logical_date: str):
    results = []
    for entity in ENTITIES:
        result = extract_entity(entity, logical_date=logical_date)
        results.append(result)
    return results


if __name__ == "__main__":
    logical_date = datetime.now(timezone.utc).date().isoformat()
    results = extract_all_entities(logical_date=logical_date)
    print("\nAll extraction results:")
    for result in results:
        print(result)
