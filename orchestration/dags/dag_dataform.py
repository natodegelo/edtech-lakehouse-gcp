"""
dag_dataform.py
Dispara o workflow Dataform (silver → gold) após todos os domínios de ingestão concluírem.

Usa ExternalTaskSensor para aguardar a task lakehouse_load de cada domínio.
Só dispara o Dataform quando TODOS os domínios tiverem concluído com sucesso.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateWorkflowInvocationOperator,
)
from airflow.sensors.external_task import ExternalTaskSensor

GCP_PROJECT = "edtech-lakehouse"
GCP_REGION = "us-east1"
DATAFORM_REPOSITORY = "edtech-lakehouse"
GCP_CONN_ID = "google_cloud_default"

DOMAIN_DAGS = [
    "dag_users",
    "dag_content",
    "dag_engagement",
    "dag_scores",
    "dag_financial",
    "dag_social",
    "dag_certifications",
    "dag_crm",
]

DEFAULT_ARGS = {
    "owner": "lakehouse",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="dag_dataform",
    description="Aguarda todos os domínios de ingestão e dispara o workflow Dataform (silver → gold).",
    schedule_interval="0 6 * * *",
    start_date=datetime(2026, 5, 16),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["lakehouse", "gcp", "edtech", "dataform"],
    doc_md="""
## dag_dataform

Orquestra a camada de transformação ELT do lakehouse.

### Dependências upstream
Aguarda a task `lakehouse_load` de cada domínio via `ExternalTaskSensor`.
O Dataform só é invocado quando todos os 8 domínios concluírem com sucesso.

### Pipeline
```
[sensor_dag_users]
[sensor_dag_content]
[sensor_dag_engagement]        → dataform_workflow_invocation
[sensor_dag_scores]
[sensor_dag_financial]
[sensor_dag_social]
[sensor_dag_certifications]
[sensor_dag_crm]
```

### Dataform
- Repositório: `edtech-lakehouse`
- Região: `us-east1`
- Executa: sources → silver → gold (todas as tabelas e assertions)
    """,
) as dag:

    # ── Sensors: aguarda lakehouse_load de cada domínio ────────────────────────
    sensors = []
    for domain_dag_id in DOMAIN_DAGS:
        sensor = ExternalTaskSensor(
            task_id=f"wait_{domain_dag_id}",
            external_dag_id=domain_dag_id,
            external_task_id="lakehouse_load",
            mode="reschedule",
            timeout=3600,
            poke_interval=60,
            allowed_states=["success"],
            failed_states=["failed", "skipped"],
        )
        sensors.append(sensor)

    # ── Dataform workflow invocation ───────────────────────────────────────────
    dataform_run = DataformCreateWorkflowInvocationOperator(
        task_id="dataform_workflow_invocation",
        project_id=GCP_PROJECT,
        region=GCP_REGION,
        repository_id=DATAFORM_REPOSITORY,
        workflow_invocation={
            "compilation_result": None,
            "workflow_settings": {
                "timeout": "3600s",
                "transitive_dependencies_included": True,
                "transitive_dependents_included": False,
                "fully_refresh_incremental_tables_enabled": False,
            },
        },
        gcp_conn_id=GCP_CONN_ID,
        asynchronous=False,
    )

    # ── Dependências: todos os sensors → dataform_run ─────────────────────────
    sensors >> dataform_run