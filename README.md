# Retailco Data Pipeline

## What this project is about

This project builds a complete data pipeline for Retailco, from source extraction to warehouse modelling.

In simple terms, the pipeline does four things:

1. pulls raw data from the source API
2. stores that raw data in a PostgreSQL **lake** database
3. moves the raw data into a PostgreSQL **warehouse** database
4. transforms the warehouse data into analytics-ready models with **dbt**

An Airflow orchestration layer was also started so the full sequence can eventually run automatically instead of manually.

---

## What has been completed so far

### Checkpoint 2 — Extract
The extraction layer was completed successfully.

What it does:
- connects to the API
- handles pagination
- supports incremental extraction with watermarks
- retries API calls when needed
- writes raw records into the `lake` database

Main entities extracted:
- stores
- employees
- payment methods
- customers
- products
- orders
- order items
- payments
- inventory movements

Validated raw counts:
- stores → 4
- employees → 50
- payment methods → 5
- customers → 5,000
- products → 2,000
- orders → 80,000
- order items → 359,221
- payments → 72,080
- inventory movements → 354,564

---

### Checkpoint 3 — Load
The loading layer was completed successfully using `dlt`.

What it does:
- reads from `lake.raw.*`
- loads into `warehouse.raw.*`
- preserves row-level parity between lake and warehouse

This means the warehouse raw layer is a reliable copy of the lake raw layer.

---

### Checkpoint 4 — Model
The dbt modelling layer was completed successfully.

What it includes:

#### Staging models
- `stg_stores`
- `stg_employees`
- `stg_customers`
- `stg_products`
- `stg_payment_methods`
- `stg_orders`
- `stg_order_items`
- `stg_payments`
- `stg_inventory_movements`

#### Snapshots
- `snap_customers`
- `snap_products`
- `snap_employees`

#### Dimensions
- `dim_customers`
- `dim_products`
- `dim_employees`
- `dim_stores`
- `dim_payment_methods`

#### Facts
- `fct_orders`
- `fct_order_items`
- `fct_payments`

Validation achieved:
- staging tests: **28/28 passed**
- marts/facts tests: **24/24 passed**

This confirms the core analytical warehouse layer is structurally sound.

---

### Checkpoint 5 — Operate / Orchestrate
Checkpoint 5 has been started.

What has already been done:
- Airflow DAG created for the full pipeline sequence
- Docker-based Airflow setup created
- custom Airflow image built successfully
- Airflow initialization completed successfully
- Airflow UI opened successfully and the DAG became visible in the UI

What is still in progress:
- final runtime stabilization of the Airflow services
- confirmed end-to-end execution of the full DAG without interruptions

So Checkpoint 5 is **started and materially implemented**, but not yet fully closed.

---

## Project structure

```text
Retailco/
├── extractor/
│   └── app/
├── loader/
│   └── app/
├── dbt_retailco/
│   ├── models/
│   └── snapshots/
├── airflow/
│   └── dags/
├── airflow_docker/
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   ├── requirements-airflow.txt
│   ├── dags/
│   ├── config/
│   ├── logs/
│   └── plugins/
├── db_backups/
└── README.md
```

---

## Setup

### 1. Requirements
You should have:
- Python 3.11+
- PostgreSQL
- Docker Desktop
- WSL2 (recommended for Docker on Windows)
- Git

---

### 2. Databases
The pipeline expects two PostgreSQL databases:
- `lake`
- `warehouse`

Expected schemas:

#### Lake
- `raw`
- `meta`

#### Warehouse
- `raw`
- `analytics`
- `snapshots`

---

### 3. Environment file
Create a root `.env` file in the project folder.

Example:

```env
RETAILCO_API_KEY=YOUR_REAL_API_KEY

LAKE_DB_HOST=localhost
LAKE_DB_PORT=5432
LAKE_DB_NAME=lake
LAKE_DB_USER=postgres
LAKE_DB_PASSWORD=YOUR_PASSWORD

WAREHOUSE_DB_HOST=localhost
WAREHOUSE_DB_PORT=5432
WAREHOUSE_DB_NAME=warehouse
WAREHOUSE_DB_USER=postgres
WAREHOUSE_DB_PASSWORD=YOUR_PASSWORD
```

Do not commit real secrets to GitHub.

---

## How to run the pipeline manually

### Step 1 — Run extraction
From the project root:

```powershell
python extractor/app/extractor.py
```

This loads raw source data into the `lake` database.

---

### Step 2 — Run the loader
From the project root:

```powershell
python loader/app/pipeline.py
```

This loads the lake raw data into the warehouse raw schema.

---

### Step 3 — Run dbt
Move into the dbt project:

```powershell
cd dbt_retailco
```

Then run:

```powershell
dbt debug
dbt run
dbt test
dbt snapshot
```

This builds and validates the warehouse model layer.

---

## How to run the DAG with Airflow

Airflow is configured inside the `airflow_docker` folder.

### Airflow task sequence
The DAG was designed to run this order:

```text
extract_all_entities
→ load_to_warehouse
→ dbt_run_models
→ dbt_test_models
```

### Start Airflow with Docker
From the project root:

```powershell
cd airflow_docker
```

Then run:

```powershell
docker compose config
docker compose build
docker compose up airflow-init
docker compose up -d
```

If the `airflow-worker` does not come up automatically, start it explicitly with:

```powershell
docker compose up -d airflow-worker
```

### Open the Airflow UI
In the browser, open:

```text
http://localhost:8080
```

Login credentials:
- username: `admin`
- password: `admin`

### Trigger the DAG
In the Airflow UI:
1. open **Dags**
2. find `checkpoint2_dag`
3. turn it on
4. trigger a manual run

---

## How to query the warehouse

Use pgAdmin, DBeaver or psql and connect to the `warehouse` database.

### Important schemas
- `raw`
- `analytics`
- `snapshots`

### Useful example queries

#### Check staging counts
```sql
select count(*) as stores_rows from analytics.stg_stores;
select count(*) as customers_rows from analytics.stg_customers;
select count(*) as orders_rows from analytics.stg_orders;
select count(*) as payments_rows from analytics.stg_payments;
```

#### Check dimensions
```sql
select count(*) as dim_customers_rows from analytics.dim_customers;
select count(*) as dim_products_rows from analytics.dim_products;
select count(*) as dim_employees_rows from analytics.dim_employees;
select count(*) as dim_stores_rows from analytics.dim_stores;
select count(*) as dim_payment_methods_rows from analytics.dim_payment_methods;
```

#### Check facts
```sql
select count(*) as fct_orders_rows from analytics.fct_orders;
select count(*) as fct_order_items_rows from analytics.fct_order_items;
select count(*) as fct_payments_rows from analytics.fct_payments;
```

#### Check snapshots
```sql
select count(*) as snap_customers_rows from snapshots.snap_customers;
select count(*) as snap_products_rows from snapshots.snap_products;
select count(*) as snap_employees_rows from snapshots.snap_employees;
```

#### Look at final fact data
```sql
select * from analytics.fct_orders limit 10;
select * from analytics.fct_order_items limit 10;
select * from analytics.fct_payments limit 10;
```

---

## Current project status

### Fully completed
- Checkpoint 2 — Extract
- Checkpoint 3 — Load
- Checkpoint 4 — Model

### Started and in progress
- Checkpoint 5 — Operate / Orchestrate

---

## Final note

The core pipeline is complete through extraction, loading, and warehouse modelling. The orchestration layer has also been set up substantially with Airflow and Docker, and the DAG is now visible in the Airflow UI. The remaining work is mainly around stabilizing full runtime execution for the complete orchestrated flow.
## Project Demo Video

You can watch the full project walkthrough and demonstration here:
**[Watch the Demo Video on Google Drive](https://drive.google.com/file/d/137LwiOwBIF-h9-mJrtKdJI4FaPDOC2hk/view?usp=sharing)**
