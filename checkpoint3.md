# Checkpoint 3 — Load

## Purpose

Checkpoint 3 focused on moving the raw data already captured in the **lake** database into the **warehouse** database using `dlt`.

At this stage, the intent was to establish a clean and validated raw-to-raw handoff:

`lake.raw.*`  
→ `dlt pipeline`  
→ `warehouse.raw.*`

This created a separate warehouse landing area that could be used safely by downstream dbt modelling without depending directly on the extraction database.

---

## Objective

The goal of this checkpoint was to replicate all extracted raw entities from the `lake` database into the `warehouse` database, while preserving raw fidelity and validating that the transferred row counts matched.

That meant:

- reading from `lake.raw.*`
- loading into `warehouse.raw.*`
- confirming that warehouse row counts matched the lake-side baseline

---

## Architecture

The loading flow for Checkpoint 3 was:

`lake.raw.*`  
→ `Python loader` using `dlt`  
→ `warehouse.raw.*`

This stage sat between extraction and modelling.

## Warehouse Setup

A separate PostgreSQL database was prepared for the warehouse layer.

### Warehouse configuration

- database: `warehouse`
- schema: `raw`
- user: `postgres`
- host: `localhost`
- port: `5432`

The `raw` schema was explicitly created and later confirmed to contain the loaded tables.

---

## Loader Project Structure

A separate loader module was created to keep the loading logic distinct from the extractor.

### Key files

- `loader/app/config.py`
- `loader/app/source.py`
- `loader/app/pipeline.py`
- `loader/requirements.txt`

This separation made the architecture clearer:

- extractor logic remained responsible for API → lake
- loader logic became responsible for lake → warehouse

---

## Configuration Strategy

The loader reused `.env` configuration so both lake and warehouse connections could be managed centrally.

### Loader-side variables used

#### Lake connection
- `LAKE_DB_HOST`
- `LAKE_DB_PORT`
- `LAKE_DB_NAME`
- `LAKE_DB_USER`
- `LAKE_DB_PASSWORD`

#### Warehouse connection
- `WAREHOUSE_DB_HOST`
- `WAREHOUSE_DB_PORT`
- `WAREHOUSE_DB_NAME`
- `WAREHOUSE_DB_USER`
- `WAREHOUSE_DB_PASSWORD`

This made it possible to switch or retarget the warehouse cleanly without rewriting code.

---

## Loading Strategy

The loader used `dlt` with PostgreSQL as the destination.

For each entity:

1. read the full raw table from `lake.raw.<entity>` into a pandas DataFrame
2. create a `dlt` pipeline targeting the warehouse database
3. load the entity into `warehouse.raw.<entity>`
4. use `write_disposition="replace"` for the first clean validation run

### Why `replace` was used

For the first validated run, `replace` was the simplest way to ensure that the warehouse raw tables were rebuilt cleanly from the current lake raw state. That made row-count validation straightforward and removed ambiguity about partial prior loads.

---

## dlt Behaviour Observed

During the successful run, `dlt` created both the raw entity tables and its own metadata tables inside the warehouse `raw` schema.

### dlt metadata tables created

- `_dlt_loads`
- `_dlt_pipeline_state`
- `_dlt_version`

These are expected and indicate that the pipeline state and schema history are being tracked by `dlt`.

### Flattening behaviour

`dlt` also expanded structured content from `_raw_payload` into additional warehouse raw columns such as:

- `_raw_payload__id`
- `_raw_payload__updated_at`
- `_raw_payload__team_id`
- other flattened source fields

This behaviour is useful because it makes the warehouse raw layer easier to consume in downstream staging than a single opaque JSON payload would.

---

## Implementation Notes

### `loader/app/config.py`
Loaded both lake and warehouse database settings from `.env`.

### `loader/app/source.py`
Prepared the lake-side connection string helper.

### `loader/app/pipeline.py`
Coordinated the full loading process:
- define entity list
- open lake connection
- read each raw table
- send records through `dlt`
- write to the warehouse destination

The loader was designed and tested manually before any orchestration layer was expected to run it.

---

## Issues Encountered During Implementation

Several practical issues appeared during Checkpoint 3, all of which were resolved.

### Missing Python packages
The first load attempt failed because `pandas` was not installed in the active environment. Installing `pandas` and `sqlalchemy` resolved that issue.

### Warehouse authentication mismatch
A later run failed because the loader configuration was still picking up the default warehouse password rather than the actual PostgreSQL password. Direct Python connection tests revealed the discrepancy, and fixing the `.env` value resolved the destination authentication problem.

### pgAdmin visibility inconsistency
After the `dlt` load completed, Python could clearly see the warehouse raw tables, but pgAdmin initially failed to show them in the Query Tool results. This turned out to be a pgAdmin session/visibility issue rather than a failed load. The actual warehouse state was validated first from Python and then later became visible in pgAdmin as well.

These issues were operational rather than architectural, and resolving them improved confidence in the loading layer.

---

## Final Warehouse Validation

The final warehouse raw row counts matched the lake raw row counts exactly.

### Validated warehouse counts

- `stores` → **4**
- `employees` → **50**
- `payment_methods` → **5**
- `products` → **2,000**
- `customers` → **5,000**
- `payments` → **72,080**
- `orders` → **80,000**
- `inventory_movements` → **354,564**
- `order_items` → **359,221**

This confirmed that the raw-to-raw load succeeded across all nine entities and that no row-count drift occurred between lake and warehouse.

---

## Why This Matters

Checkpoint 3 is the bridge between ingestion and modelling.

By successfully loading `lake.raw.*` into `warehouse.raw.*`, the project now has:

- an extraction layer isolated from the warehouse
- a warehouse raw layer ready for dbt staging
- validated parity between lake and warehouse row counts
- a repeatable load process managed through code rather than manual exports

That is exactly what this checkpoint was supposed to establish.

---

## Limitations at This Stage

Checkpoint 3 still stops at raw replication.

The loader does **not** yet:

- model staging tables
- rename all columns to snake_case for analysis
- apply business type casting beyond what `dlt` inferred
- build marts, facts, or dimensions
- apply dbt snapshots or soft-delete logic

Those tasks belong to the modelling checkpoint.

-

## Outcome

Checkpoint 3 successfully established the lake-to-warehouse raw loading layer. The loader read all extracted raw entities from the lake database and loaded them into the warehouse database using `dlt`. Final validation confirmed that warehouse row counts matched lake row counts across all nine entities, which means the project is ready to proceed to dbt modelling in the next checkpoint.
