from datetime import datetime
from dag_factory import build_domain_dag

dag = build_domain_dag(
    dag_id="dag_users",
    description="Domínio de usuários: users, userprofiles, userplans.",
    schedule_interval="0 5 * * *",
    tags=["users"],
    start_date=datetime(2026, 5, 16),
)