from datetime import datetime
from dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_financial",
    description="Domínio financeiro: subscriptions, bills, consolidated_sales.",
    schedule_interval="0 5 * * *",
    tags=["financial"],
    start_date=datetime(2026, 5, 16),
)