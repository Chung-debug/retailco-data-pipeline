# Checkpoint 4 — Model

## Purpose

Checkpoint 4 focused on building the dbt modelling layer on top of the warehouse raw schema. At this stage, the goal was transforming the raw warehouse tables into a clean, validated, analytics-ready model.

This checkpoint covered four major modelling responsibilities:

- staging raw warehouse tables into cleaned dbt models
- adding data quality and relationship tests to the staging layer
- creating snapshots for soft-delete and historical tracking use cases
- building the first core dimensions and facts for analytics consumption

The intention was to create a warehouse model that is structured enough for downstream reporting, while preserving auditability and history where needed.

---

## Warehouse Modelling Architecture

The modelling flow implemented in this checkpoint was:

`warehouse.raw.*`  
→ `dbt staging models`  
→ `dbt snapshots`  
→ `dbt dimensions and facts`  
→ `dbt tests`

This created a clean separation between:

- raw ingestion storage (`warehouse.raw`)
- transformed warehouse models (`warehouse.analytics`)
- historical SCD-style records (`warehouse.snapshots`)

That structure is appropriate for a modern warehouse project because it keeps source-like storage separate from semantic modelling.

---

## dbt Project Setup

A dbt PostgreSQL project was initialized under the project folder and connected to the `warehouse` database.

### Configuration used

- database: `warehouse`
- source schema: `raw`
- target analytics schema: `analytics`
- snapshot schema: `snapshots`
- adapter: `dbt-postgres`

The connection was validated successfully with `dbt debug`, confirming that dbt could read from the warehouse and build objects into the target schema.

---

## Source Registration

The warehouse raw tables were registered as dbt sources in `sources.yml` under a single source name:

```yaml
sources:
  - name: retailco_raw
    database: warehouse
    schema: raw
```

The following raw tables were made available as dbt sources:

- stores
- employees
- payment_methods
- customers
- products
- orders
- order_items
- payments
- inventory_movements

This created a clean and explicit source layer for all downstream staging models.

---

## Staging Layer

The staging layer cleaned the warehouse raw tables into dbt views under the `analytics` schema.

### Objectives of staging

The staging models were designed to:

- standardize naming into snake_case
- cast timestamps, dates, numeric fields, and boolean fields cleanly
- preserve ingestion lineage fields such as `ingested_at`, `run_id`, and `logical_date`
- expose flattened source attributes from the raw payload into clearer warehouse-ready columns
- carry forward `is_deleted` fields where relevant for later soft-delete logic

### Staging models created

- `stg_stores`
- `stg_employees`
- `stg_customers`
- `stg_products`
- `stg_payment_methods`
- `stg_orders`
- `stg_order_items`
- `stg_payments`
- `stg_inventory_movements`

### Validated staging row counts

The following row counts were validated successfully in the staging layer:

- `stg_stores` → **4**
- `stg_employees` → **50**
- `stg_customers` → **5,000**
- `stg_products` → **2,000**
- `stg_payment_methods` → **5**
- `stg_orders` → **80,000**
- `stg_order_items` → **359,221**
- `stg_payments` → **72,080**
- `stg_inventory_movements` → **354,564**

This confirmed that the dbt staging layer was correctly sourcing from the warehouse raw schema and preserving row-level parity.

---

## Staging Tests

Once the staging models were built, schema tests were added to validate structural soundness.

### Test categories used

- `not_null`
- `unique`
- `relationships`

### Examples of validated logic

- primary keys such as `store_id`, `employee_id`, `customer_id`, `product_id`, `order_id`, `order_item_id`, `payment_id`, and `inventory_movement_id` were all tested for `not_null` and `unique`
- foreign-key-style relationships were tested across the staging layer, for example:
  - employees → stores
  - orders → customers / employees / stores
  - order_items → orders / products
  - payments → orders / payment_methods
  - inventory_movements → stores / products

### Test result

The staging test execution returned:

- **28 tests run**
- **28 PASS**
- **0 WARN**
- **0 ERROR**

This confirmed that the staging layer was structurally trustworthy before downstream modelling began.

---

## Snapshot Layer and Soft-Delete Strategy

A key requirement of the checkpoint was to handle soft deletes in a way that preserves history for dimension-like entities while allowing later fact models to treat deleted records appropriately.

### Snapshot approach used

Snapshots were created for the three main dimension-style entities that carried `is_deleted` or similar historical importance:

- `snap_customers`
- `snap_products`
- `snap_employees`

### Snapshot configuration pattern

Each snapshot used:

- `strategy='timestamp'`
- `updated_at='updated_at'`
- the business key (`customer_id`, `product_id`, `employee_id`) as the `unique_key`
- target schema = `snapshots`

This means dbt now tracks historical versions whenever the source `updated_at` changes.

### Snapshot validation results

Initial snapshot row counts were validated successfully:

- `snap_customers` → **5,000**
- `snap_products` → **2,000**
- `snap_employees` → **50**

On the initial run, this produced one current version per business entity, which is expected for a first snapshot execution.

### Why this matters

The snapshot layer now provides the foundation for SCD-style historical tracking.

That means later dimension models can distinguish:

- current rows → `dbt_valid_to is null`
- historical rows → `dbt_valid_to is not null`

and deleted entities can remain historically visible instead of being lost.

---

## Dimension Layer

After snapshots were in place, current-state dimensions were created.

### Dimension design approach

Two design patterns were used:

#### Snapshot-backed dimensions
Used for entities requiring historical retention and soft-delete awareness:

- `dim_customers`
- `dim_products`
- `dim_employees`

These dimensions were built from snapshot tables and filtered to:

```sql
where dbt_valid_to is null
```

which produces the **current version** of each entity while preserving the ability to inspect history in the snapshot layer.

#### Staging-backed dimensions
Used for lookup-style or relatively static entities that did not yet require snapshot logic:

- `dim_stores`
- `dim_payment_methods`

These were built directly from staging models.

### Dimensions created

- `dim_customers`
- `dim_products`
- `dim_employees`
- `dim_stores`
- `dim_payment_methods`

### Validated dimension row counts

- `dim_customers` → **5,000**
- `dim_products` → **2,000**
- `dim_employees` → **50**
- `dim_stores` → **4**
- `dim_payment_methods` → **5**

These counts matched the expected current-state populations.

---

## Fact Layer

The first core transaction-oriented fact models were then created from staging.

### Facts created

- `fct_orders`
- `fct_order_items`
- `fct_payments`

### Fact design approach

The first versions of the fact models were clean and traceable. They preserved:

- the business keys
- the main timestamps
- the main numeric measures
- the pipeline traceability columns (`ingested_at`, `run_id`, `logical_date`)

This kept the first mart layer understandable and easy to validate.

### Validated fact row counts

- `fct_orders` → **80,000**
- `fct_order_items` → **359,221**
- `fct_payments` → **72,080**

The counts matched the staging sources exactly, confirming that the fact models were built correctly.

---

## Dimension and Fact Tests

After the dimensions and facts were created, a second round of dbt tests was added to validate the final analytical layer.

### Dimension tests covered

- `not_null` and `unique` on dimension primary keys
- relationship check between employees and stores

### Fact tests covered

- `not_null` and `unique` on fact primary keys
- relationships from facts to dimensions/facts, including:
  - orders → customers / employees / stores
  - order_items → orders / products
  - payments → orders / payment_methods

### Test result

The marts/facts test execution returned:

- **24 tests run**
- **24 PASS**
- **0 WARN**
- **0 ERROR**

This confirmed that the final dimension and fact layer was structurally sound and that business keys and relationships were valid.

---

## Soft-Delete Handling Outcome

The implemented design now supports the required soft-delete treatment in a defensible way.

### Current design behaviour

- **Historical retention** is preserved in the snapshot layer for customers, products, and employees
- **Current-state dimensions** are built from the snapshot layer using `dbt_valid_to is null`
- `is_deleted` is retained in the dimensions rather than discarded immediately, so downstream marts or reporting layers can choose whether to include or exclude deleted current rows

### Why this is appropriate

This keeps the warehouse honest and flexible:

- deleted entities remain historically visible
- current business-facing models can later choose to filter `is_deleted = false`
- facts are not forced to lose lineage to previously valid dimension members

This is a strong starting point for more advanced SCD and business-rule handling.

---

## Final Model Inventory

By the end of Checkpoint 4, the warehouse contained the following core dbt models:

### Staging models
- `stg_stores`
- `stg_employees`
- `stg_customers`
- `stg_products`
- `stg_payment_methods`
- `stg_orders`
- `stg_order_items`
- `stg_payments`
- `stg_inventory_movements`

### Snapshots
- `snap_customers`
- `snap_products`
- `snap_employees`

### Dimensions
- `dim_customers`
- `dim_products`
- `dim_employees`
- `dim_stores`
- `dim_payment_methods`

### Facts
- `fct_orders`
- `fct_order_items`
- `fct_payments`

This is already a strong warehouse core for downstream analytics use.


---

## Outcome

Checkpoint 4 successfully established the dbt modelling layer on top of the warehouse raw schema. All major raw entities were staged and validated, snapshots were introduced for key dimension-style entities, current dimensions were created, and the first core fact models were built. Final dbt tests confirmed that the dimension and fact layer is structurally sound. The warehouse is now in a strong position for documentation, orchestration, and any additional business-specific marts that may be required in later steps.
