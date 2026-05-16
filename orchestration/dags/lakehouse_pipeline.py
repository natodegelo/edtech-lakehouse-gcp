from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="lakehouse_pipeline",
    description="Pipeline completo: ingest → load → dataform",
    schedule_interval="0 6 * * *",
    start_date=datetime(2026, 5, 16),
    catchup=False,
    default_args=default_args,
    tags=["lakehouse", "gcp", "edtech"],
) as dag:

    ingest = CloudRunExecuteJobOperator(
        task_id="lakehouse_ingest",
        project_id="edtech-lakehouse",
        region="us-east1",
        job_name="lakehouse-ingest",
        deferrable=False,
    )

    load = CloudRunExecuteJobOperator(
        task_id="lakehouse_load",
        project_id="edtech-lakehouse",
        region="us-east1",
        job_name="lakehouse-load",
        deferrable=False,
    )

    dataform = CloudRunExecuteJobOperator(
        task_id="dataform_run",
        project_id="edtech-lakehouse",
        region="us-east1",
        job_name="dataform-run",
        deferrable=False,
    )

    ingest >> load >> dataform