from datetime import datetime
from _dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_content",
    description="Domínio de conteúdo: courses, events, plans.",
    schedule_interval="0 5 * * *",
    tags=["content"],
    start_date=datetime(2026, 5, 16),
)

globals()["dag_content"] = dag