"""
dag_factory.py
Fábrica de DAGs de ingestão do EdTech Lakehouse.

Cada domínio instancia esta factory com suas collections.
O pipeline por domínio é sempre:
    generator → ingest → load

O dag_dataform dispara após todos os domínios concluírem.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator

GCP_PROJECT = "edtech-lakehouse"
GCP_REGION = "us-east1"
GCP_CONN_ID = "google_cloud_default"

DEFAULT_ARGS = {
    "owner": "lakehouse",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "email_on_failure": False,
    "email_on_retry": False,
}


def make_cloud_run_operator(task_id: str, job_name: str, dag: DAG) -> CloudRunExecuteJobOperator:
    """Cria um CloudRunExecuteJobOperator padronizado."""
    return CloudRunExecuteJobOperator(
        task_id=task_id,
        project_id=GCP_PROJECT,
        region=GCP_REGION,
        job_name=job_name,
        gcp_conn_id=GCP_CONN_ID,
        deferrable=False,
        dag=dag,
    )


def build_domain_dag(
    dag_id: str,
    description: str,
    schedule_interval: str,
    tags: list[str],
    start_date: datetime,
) -> DAG:
    """
    Constrói uma DAG de domínio com pipeline padrão:
        lakehouse-generator → lakehouse-ingest → lakehouse-load

    Todos os domínios compartilham o mesmo pipeline de jobs Cloud Run.
    O isolamento de falhas é garantido pelo DAG separado por domínio —
    se dag_financial falha, dag_engagement continua rodando normalmente.

    Args:
        dag_id: Identificador único da DAG.
        description: Descrição do domínio.
        schedule_interval: Cron expression do agendamento.
        tags: Tags para filtro na UI do Airflow.
        start_date: Data de início da DAG.

    Returns:
        DAG configurada e pronta para uso.
    """
    dag = DAG(
        dag_id=dag_id,
        description=description,
        schedule_interval=schedule_interval,
        start_date=start_date,
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["lakehouse", "gcp", "edtech"] + tags,
        doc_md=f"""
## {dag_id}

{description}

### Pipeline
```
lakehouse-generator → lakehouse-ingest → lakehouse-load
```

### Dependência downstream
Esta DAG é monitorada pelo `dag_dataform` via `ExternalTaskSensor`.
O Dataform só dispara quando todos os domínios concluírem com sucesso.
        """,
    )

    with dag:
        generator = make_cloud_run_operator(
            task_id="lakehouse_generator",
            job_name="lakehouse-generator",
            dag=dag,
        )

        ingest = make_cloud_run_operator(
            task_id="lakehouse_ingest",
            job_name="lakehouse-ingest",
            dag=dag,
        )

        load = make_cloud_run_operator(
            task_id="lakehouse_load",
            job_name="lakehouse-load",
            dag=dag,
        )

        generator >> ingest >> load

    return dag