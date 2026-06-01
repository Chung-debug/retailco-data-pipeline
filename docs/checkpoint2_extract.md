# Checkpoint 2 — Extraction Documentation

## Purpose

Checkpoint 2 implements the source ingestion layer for RetailCo's modern data platform. The extractor authenticates against the ERP API, handles cursor pagination, supports incremental extraction with watermarks, retries transient failures, and lands raw data into PostgreSQL under the `raw` schema.

## Scope

The extractor is configured for all nine API entities:

- stores
- employees
- payment_methods
- customers
- products
- orders
- order_items
- payments
- inventory_movements

Each endpoint lands into a matching raw table in the lake database.

## Design Summary

The extractor keeps ingestion and modelling separate.

Flow:

`ERP API` → `Python extractor` → `lake.raw.*` → `meta.watermarks`

It does not apply business transformation. The raw layer preserves source rows with minimal technical mapping, while downstream standardisation is deferred to dbt staging in Checkpoint 4.

## Raw Landing Strategy

Each entity lands into its own table under `raw`, with:

- entity primary key
- `updated_at`
- `_run_id`
- `_logical_date`
- `_raw_payload`

The API uses generic and camelCase fields such as `id` and `updatedAt`. The extractor maps only the minimum required fields for raw ingestion while preserving the original source payload in `_raw_payload`.

## Watermark Strategy

Watermarks are stored in `meta.watermarks` with one row per entity. For each run, the extractor:

1. reads the current watermark
2. decides full vs incremental mode
3. extracts all pages for that entity
4. loads rows into the raw table
5. tracks the maximum `updatedAt`
6. updates the watermark only after the full entity succeeds

This prevents partial-run gaps and keeps incremental reruns safe.

## Pagination and Retry

All list endpoints are cursor paginated. The extractor follows `meta.cursor` until `has_more = false`.

The client retries on:

- 429 rate limits
- 500+ server errors
- timeouts
- connection resets / connection errors
- SSL-related transient failures

Exponential backoff is used across retries.

## Idempotency

Raw loading uses upsert-based writes keyed by the source primary key. This ensures:

- no duplicate primary keys
- safe reruns
- safe inclusive watermark boundaries
- recovery after partial failures

## Implementation Components

- `entities.py` — endpoint and key configuration
- `config.py` — API, DB, and pipeline settings loaded from `.env`
- `watermarks.py` — control-table helpers
- `client.py` — authenticated API requests with retry logic
- `loaders.py` — raw upsert logic
- `extractor.py` — page-by-page extraction workflow

## Validation Notes

The extractor was validated across small and large entities. In development runs, it successfully landed large transactional entities such as `orders`, `payments`, and `order_items`, while preserving incremental state through `meta.watermarks`.
