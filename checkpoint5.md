# Checkpoint 5 — Operate / Orchestrate

## What Checkpoint 5 was meant to do

Checkpoint 5 focused on turning the earlier stages of the project into a coordinated pipeline that can run in the correct order instead of being executed manually one step at a time.

By this point, the project already had:
- a working extractor
- a working loader
- a validated dbt modelling layer

So the purpose of Checkpoint 5 was to connect these working pieces into one orchestrated workflow.

The intended execution order was:

```text
extract_all_entities
→ load_to_warehouse
→ dbt_run_models
→ dbt_test_models
```

This order is important because each step depends on the success of the one before it.

---

## What was implemented

### 1. Airflow DAG
A full Airflow DAG was created to orchestrate the pipeline.

The DAG included the following tasks:
- `extract_all_entities`
- `load_to_warehouse`
- `dbt_run_models`
- `dbt_test_models`

It was designed so that if one task fails, downstream tasks do not continue.

---

### 2. Docker-based Airflow setup
Since native Airflow execution on Windows is unreliable, Docker was used as the preferred runtime path.

A dedicated `airflow_docker` setup was created with:
- `docker-compose.yaml`
- `Dockerfile`
- `requirements-airflow.txt`
- local Airflow `.env`
- `config/profiles.yml`
- a Docker-compatible DAG file

This made it possible to run Airflow inside containers instead of depending on a fragile native Windows runtime.

---

### 3. Custom Airflow image
A custom Airflow image was built so the container environment could run the actual project code.

The image included support for:
- pandas
- SQLAlchemy
- psycopg2
- python-dotenv
- dlt
- dbt-core
- dbt-postgres

Without that custom image, the DAG would not have been able to execute the extractor, loader, or dbt tasks correctly.

---

## Operational logic

The orchestration logic used a strict dependency order:
- extraction must finish before loading starts
- loading must finish before dbt begins
- dbt run must finish before dbt tests run

This protects the pipeline against partial execution and avoids downstream tasks running on incomplete upstream results.

Retry-aware task configuration was also included so Airflow can re-attempt failed tasks where appropriate.

---

## Validation achieved so far

Checkpoint 5 reached several important milestones:

- Docker Compose configuration was validated successfully
- custom Airflow images were built successfully
- `airflow-init` completed successfully
- the Airflow web UI opened successfully
- the DAG became visible in the Airflow UI
- a manual DAG run was created successfully
- the worker process was started so queued tasks could begin execution

These are important proof points that the orchestration layer is not just theoretical — it was materially implemented.

---

## Issues encountered

The main issues during Checkpoint 5 were operational rather than architectural.

### 1. Native Windows Airflow limitations
Airflow on native Windows was not viable because of POSIX-oriented runtime dependencies.

### 2. Docker Desktop instability
Docker Desktop sometimes lost connection to the Linux engine, which interrupted Airflow startup and Compose commands.

### 3. Port conflicts
At one stage, the Airflow API server could not bind to the host port because the port was already in use.

### 4. Worker/runtime stabilization
Even after Airflow services came up, the worker and some services needed additional stabilization before queued tasks could begin running reliably.

These issues slowed down final runtime validation, but they did not invalidate the orchestration design itself.

---

## Current status

Checkpoint 5 has been **started and substantially implemented**, but it is not yet fully closed.

### Already completed
- full DAG design
- Docker Airflow setup
- custom image build
- Airflow initialization
- Airflow UI access
- DAG discovery in the UI
- first DAG run creation

### Still in progress
- final stable execution of the full DAG from start to finish
- clean confirmation that all orchestration tasks complete successfully in sequence
- runtime hardening of the Docker Airflow environment

---

## Final note

Checkpoint 5 has successfully established the orchestration layer for the Retailco pipeline in a meaningful way. The DAG structure exists, the Docker Airflow environment has been created, Airflow initialization has completed successfully, the UI is accessible, and the workflow is now visible inside Airflow.

The remaining work is mainly around runtime stabilization and confirming that the DAG executes end to end without interruption. That means Checkpoint 5 is no longer at the design-only stage — it is actively implemented, but still being finalized operationally.
