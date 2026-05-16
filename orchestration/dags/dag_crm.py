from datetime import datetime
from dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_crm",
    description="Domínio de CRM: gateway_customers, crm_contacts (HubSpot checkpoint).",
    schedule_interval="0 5 * * *",
    tags=["crm"],
    start_date=datetime(2026, 5, 16),
)