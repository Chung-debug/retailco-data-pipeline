# Checkpoint 2 — Extract

## Purpose

Checkpoint 2 focused on building the source ingestion layer for the RetailCo data platform. The goal at this stage was to connect to the ERP API, extract source data reliably, and land it into the **lake PostgreSQL database** under the `raw` schema.

This checkpoint was intentionally limited to **ingestion**, not downstream modelling. The extractor was designed to handle:

- authenticated API access
- cursor-based pagination
- incremental extraction with watermarks
- retry and backoff for unstable requests
- idempotent raw-table loading

It did **not** yet perform analytical transformation tasks such as snake_case standardisation, business casting, SCD2 logic, or mart construction. Those responsibilities belong to later checkpoints.

---

## Scope of Extraction

The ERP API exposed nine list endpoints, and the extractor was configured to ingest all nine:

- `stores`
- `employees`
- `payment_methods`
- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `inventory_movements`

Each endpoint landed into a matching raw table inside the **lake** database.

---

## Extraction Architecture

The extraction flow was implemented as:

`ERP REST API`  
→ `Python extractor`  
→ `lake.raw.* tables`  
→ `meta.watermarks`

The extractor was kept narrowly focused on operational ingestion. Its responsibilities were to:

- call the API safely
- handle pagination
- recover from transient request failures
- write rows into raw Postgres tables
- update extractor control state only after successful completion

This separation kept extraction reliable and traceable while deferring modelling to later checkpoints.

---

## Raw Landing Strategy

Each source entity landed into its own raw table under the `raw` schema. Example targets included:

- `raw.stores`
- `raw.customers`
- `raw.orders`
- `raw.payments`
- `raw.inventory_movements`

The raw layer was intentionally lightweight and operational rather than analytical. In addition to the target primary key and `updated_at`, each table stored ingestion metadata such as:

- `_ingested_at`
- `_run_id`
- `_logical_date`
- `_raw_payload`

The `_raw_payload` column preserved the source record in raw form, which was especially useful because the API used generic IDs and camelCase field names.

---

## Source-to-Raw Mapping

A key implementation detail discovered during testing was that the API did **not** return entity-specific keys such as `store_id` or `customer_id`. Instead, the payload used fields such as:

- `id`
- `updatedAt`
- `createdAt`
- `teamId`

To keep Checkpoint 2 focused on ingestion, the extractor applied only the minimum technical mapping needed for storage:

- source `id` → target raw primary key column
- source `updatedAt` → target `updated_at`
- full row → `_raw_payload`

This avoided pushing modelling logic into the extractor and left full standardisation for dbt staging later.

---

## Watermark Strategy

Incremental extraction was controlled through the `meta.watermarks` table.

Each entity had one control row containing:

- `last_successful_updated_at`
- `last_run_started_at`
- `last_run_completed_at`
- `last_run_status`
- `rows_extracted`
- `rows_loaded`

### Watermark behaviour

For each entity run, the extractor followed this sequence:

1. read the current watermark
2. decide whether the run was full or incremental
3. extract the entity page by page
4. load rows into the raw table
5. track the maximum `updatedAt` seen
6. update the watermark **only after full success**

This design prevents partial-run gaps. If a run fails midway, the watermark does **not** advance, so the next run can safely revisit earlier pages.

---

## Incremental Loading Logic

The extractor supported two modes:

### First run
If an entity had no successful watermark, the extractor performed a **full extract**.

### Subsequent runs
If an entity already had a watermark, the extractor passed:

```text
updated_after=<last_successful_updated_at>
```

to the API.

### Observed behaviour
In practice, some reruns returned the boundary row again immediately after a previous successful run. This suggests the API applies an inclusive incremental boundary (`updatedAt >= watermark`). Because raw loading used **upsert**, that behaviour remained safe and did not create duplicate primary keys.

---

## Pagination Strategy

All list endpoints were cursor-paginated.

The extractor followed pagination using:

- `meta.cursor`
- `meta.has_more`

The initial version fetched all pages into memory before loading them, which worked for lighter entities but became less practical for larger endpoints such as `orders`.

To improve resilience, the extractor was upgraded to a **page-by-page loading pattern**:

1. request one page
2. load that page immediately
3. request the next page
4. repeat until `has_more = false`

This made large-entity extraction safer, reduced memory pressure, and provided clearer progress visibility during long-running loads.

---

## Retry and Backoff Handling

The client included explicit retry handling for unstable API behaviour.

### Retries were applied to:

- `429` rate limits
- `500+` server errors
- timeouts
- connection resets / connection errors
- SSL-related transient failures

### Backoff behaviour

The extractor used exponential backoff with a small base delay, increasing the wait time by retry attempt.

This became especially important for heavy transactional endpoints such as `orders` and `inventory_movements`, where intermittent `500` responses appeared during long pagination runs. The retry behaviour allowed extraction to continue page by page rather than aborting the entire entity immediately.

---

## Idempotency Design

Idempotency was a core requirement of Checkpoint 2.

The extractor achieved this through **upsert-based loading** into raw tables.

### Why this mattered

Upsert logic ensured that:

- duplicate primary keys were not created
- reruns did not inflate row counts
- inclusive incremental boundaries remained safe
- late-arriving or revisited rows could overwrite prior raw state cleanly

This was especially important once the extractor moved to page-by-page loading. If a long-running entity failed before the watermark was committed, rerunning it could revisit earlier pages, but the raw layer would remain consistent.

---

## Implementation Components

The extraction logic was split into small reusable modules:

### `entities.py`
Stored endpoint configuration for all nine entities:
- endpoint
- target raw table
- target primary key
- source key
- source updated field

### `config.py`
Stored shared configuration:
- API base URL
- retry limits
- request timeout
- database connection settings
- schema/table names

Configuration values were loaded from `.env`.

### `watermarks.py`
Handled:
- reading watermarks
- marking run started
- marking run success
- marking run failure

### `client.py`
Handled:
- authenticated API requests
- retry/backoff
- pagination requests
- page-level progress logging

### `loaders.py`
Handled:
- raw-table upserts
- JSON payload storage
- idempotent writes into PostgreSQL

### `extractor.py`
Orchestrated the full flow for each entity:
- read watermark
- fetch page(s)
- load rows
- update watermark state

---

## Final Validation Results

After iterative debugging and rerun handling, the final lake raw counts were:

- `stores` → **4**
- `employees` → **50**
- `payment_methods` → **5**
- `products` → **2,000**
- `customers` → **5,000**
- `payments` → **72,080**
- `orders` → **80,000**
- `inventory_movements` → **354,564**
- `order_items` → **359,221**

The `meta.watermarks` table also showed `success` for **all 9 entities**, with populated `last_successful_updated_at` values.

That outcome confirmed that the extractor could handle both lightweight reference entities and very large transactional or event-style entities.

---

## Operational Observations

A few important behaviours were observed during implementation:

### Inclusive boundary behaviour
Some reruns extracted a single row immediately after a previous success. This aligned with an inclusive incremental boundary and remained safe because of upsert loading.

### Large endpoint duration
`orders` and `inventory_movements` took significantly longer than smaller endpoints due to row volume. That turned out to be a data-volume issue rather than a pagination loop issue.

### Intermittent page failures
Larger endpoints occasionally returned isolated `500` responses during pagination. Because retries were handled per page, these failures did not necessarily interrupt the full entity run.

### Control-state cleanup during interrupted runs
At one stage, entities such as `payments` and `inventory_movements` had already loaded rows into the raw tables while their watermark rows still showed `failed` or `running`. This was a natural consequence of page-by-page loading combined with interrupted execution. Because the raw layer used upsert, rerunning those entities safely closed the control state without corrupting row counts.



## Outcome

Checkpoint 2 successfully established the source ingestion layer for RetailCo’s ERP data. The extractor now supports authenticated API access, cursor pagination, incremental extraction with watermarks, retry/backoff for unstable requests, and idempotent raw landing into PostgreSQL. Final validation across all nine entities confirmed that the extraction layer is ready for downstream loading and modelling stages.
