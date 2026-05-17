from datetime import datetime
from _dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_scores",
    description="Domínio de scores: scores, scoresummarizeds.",
    schedule_interval="0 5 * * *",
    tags=["scores"],
    start_date=datetime(2026, 5, 16),
)

globals()["dag_scores"] = dag