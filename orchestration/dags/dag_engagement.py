from datetime import datetime
from dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_engagement",
    description="Domínio de engajamento: usercourseprogresses, summarizeds, eventprogresses, audittraffics.",
    schedule_interval="0 5 * * *",
    tags=["engagement"],
    start_date=datetime(2026, 5, 16),
)