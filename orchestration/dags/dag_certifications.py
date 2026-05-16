from datetime import datetime
from dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_certifications",
    description="Domínio de certificações: certificates, specialization_graduates.",
    schedule_interval="0 5 * * *",
    tags=["certifications"],
    start_date=datetime(2026, 5, 16),
)