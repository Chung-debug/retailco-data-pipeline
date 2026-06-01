from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# Docker-mounted project paths
PROJECT_ROOT = Path("/opt/airflow/project")
EXTRACTOR_APP_DIR = PROJECT_ROOT / "extractor" / "app"
LOADER_APP_DIR = PROJECT_ROOT / "loader" / "app"
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_retailco"

# Allow extractor import
sys.path.append(str(EXTRACTOR_APP_DIR))

from extractor import extract_all_entities


default_args = {
    "owner": "retailco",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


PYTHON_EXE = "/usr/local/bin/python"
DBT_EXE = "/home/airflow/.local/bin/dbt"


def run_extract(**context):
    logical_date = context["ds"]  # YYYY-MM-DD
    results = extract_all_entities(logical_date=logical_date)

    print("Extraction results:")
    for result in results:
        print(result)


def run_loader():
    loader_script = LOADER_APP_DIR / "pipeline.py"
    subprocess.run(
        [PYTHON_EXE, str(loader_script)],
        check=True
    )


def run_dbt_models():
    subprocess.run(
        [DBT_EXE, "run"],
        cwd=str(DBT_PROJECT_DIR),
        check=True
    )


def run_dbt_tests():
    subprocess.run(
        [DBT_EXE, "test"],
        cwd=str(DBT_PROJECT_DIR),
        check=True
    )


with DAG(
    dag_id="checkpoint2_dag",
    description="Retailco full pipeline: extract -> load -> dbt run -> dbt test",
    default_args=default_args,
    start_date=datetime(2026, 5, 31),
    schedule="@daily",
    catchup=False,
    tags=["retailco", "extract", "load", "dbt"],
) as dag:

    start = EmptyOperator(task_id="start")

    extract_all_entities_task = PythonOperator(
        task_id="extract_all_entities",
        python_callable=run_extract,
    )

    load_to_warehouse_task = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=run_loader,
    )

    dbt_run_models_task = PythonOperator(
        task_id="dbt_run_models",
        python_callable=run_dbt_models,
    )

    dbt_test_models_task = PythonOperator(
        task_id="dbt_test_models",
        python_callable=run_dbt_tests,
    )

    end = EmptyOperator(task_id="end")

    start >> extract_all_entities_task >> load_to_warehouse_task >> dbt_run_models_task >> dbt_test_models_task >> end