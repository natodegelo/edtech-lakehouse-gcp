# EdTech Lakehouse GCP

> Production-grade Data Lakehouse on GCP for an EdTech platform — Medallion Architecture with BigQuery, Dataform, Airflow, Cloud Run, and Terraform.

This project reconstructs a real production lakehouse built at a Brazilian EdTech company using synthetic data, applying senior-level engineering practices that the original system couldn't implement due to time and cost constraints. Every architectural decision here is justified, documented, and testable.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│   MongoDB (21 collections) · HubSpot CRM · Vindi Gateway       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                             │
│   lakehouse-generator  →  GCS (edtech-generator-dev)           │
│   lakehouse-ingest     →  GCS raw (NDJSON + quarantine)        │
│   lakehouse-load       →  BigQuery raw_dev                     │
│                                                                 │
│   Cloud Run Jobs · Partitioned by ingest_date / ingest_time    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAW LAYER (GCS)                            │
│   gs://edtech-raw-dev/mongodb/{collection}/                     │
│     ingest_date=YYYY-MM-DD/ingest_time=HHMMSS/part-00000.ndjson│
│   gs://edtech-quarantine-dev/  ← invalid records               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SILVER LAYER (BigQuery)                       │
│   15 tables · SCD Type 2 · MERGE · WRITE_APPEND · Lineage      │
│   Dataform ELT · Assertions as quality gates                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GOLD LAYER (BigQuery)                        │
│   gold_user_360 · gold_user_adherence · gold_churn_risk_signals │
│   gold_user_content_engagement · gold_trial_funnel              │
│   gold_trial_daily_journey                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                     Looker Studio
```

**Orchestration:** Apache Airflow (Docker · LocalExecutor) — 9 domain DAGs + ExternalTaskSensor  
**Infrastructure:** Terraform — GCS, BigQuery, IAM, APIs, Cloud Run  
**CI/CD:** GitHub Actions — lint (flake8 + black), format check, tests

---

## Stack

| Layer | Technology | Rationale |
|---|---|---|
| Data Generation | Python + Faker (pt_BR) | Realistic synthetic data with full schema control |
| Ingestion | Python + Cloud Run Jobs | Containerized, idempotent, scalable |
| Storage (raw) | GCS + NDJSON | Native BigQuery format, append-friendly, partitioned |
| Transformation | Dataform (SQLX) | ELT native to GCP — transformations inside BigQuery, not outside |
| Warehouse | BigQuery | Partitioning + clustering per table, columnar storage |
| Orchestration | Apache Airflow (Docker) | Domain-isolated DAGs, ExternalTaskSensor, retry logic |
| Infrastructure | Terraform | 100% IaC — no manual resource creation |
| CI/CD | GitHub Actions | Lint + format + test on every PR |
| Quality | Dataform Assertions | Quality gates that block promotion to gold on failure |

---

## Project Structure

```
edtech-lakehouse-gcp/
├── .github/
│   └── workflows/
│       ├── ci.yml              # lint + test on every PR
│       └── cd.yml              # build + deploy on merge to main
├── data_generator/
│   ├── generate.py             # 21 entities with Faker pt_BR → GCS
│   ├── Dockerfile
│   └── requirements.txt
├── ingestion/
│   ├── ingest.py               # GCS generator → GCS raw (NDJSON + quarantine)
│   ├── Dockerfile
│   └── requirements.txt
├── load/
│   ├── load.py                 # GCS raw → BigQuery raw_dev
│   ├── Dockerfile
│   └── requirements.txt
├── definitions/                # Dataform workspace (root)
│   ├── sources/                # 20+ src_*.sqlx declarations
│   ├── silver/                 # 15 silver tables
│   ├── gold/                   # 6 gold tables
│   └── assertions/             # quality tests
├── orchestration/
│   ├── dags/
│   │   ├── dag_users.py
│   │   ├── dag_content.py
│   │   ├── dag_engagement.py
│   │   ├── dag_scores.py
│   │   ├── dag_financial.py
│   │   ├── dag_social.py
│   │   ├── dag_certifications.py
│   │   ├── dag_crm.py
│   │   └── dag_dataform.py
│   ├── plugins/
│   │   └── _dag_factory.py     # reusable DAG builder
│   └── docker-compose.yml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── environments/
│   │   ├── dev.tfvars
│   │   └── prod.tfvars
│   └── modules/
│       ├── bigquery/
│       ├── gcs/
│       └── iam/
├── tests/
└── workflow_settings.yaml      # Dataform config (root)
```

---

## Data Model — 21 Entities

### Ingestion Strategies

| Collection | Nature | Strategy | Rationale |
|---|---|---|---|
| `users` | Persistent entity | WRITE_TRUNCATE | Daily snapshot of current state |
| `userprofiles` | Persistent entity | WRITE_TRUNCATE | Mutable profile, no history needed |
| `courses` | Catalog | WRITE_TRUNCATE | Content catalog, rarely changes |
| `events` | Catalog | WRITE_TRUNCATE | Live event catalog |
| `plans` | Catalog | WRITE_TRUNCATE | Small reference table |
| `gateway_customers` | Persistent entity | WRITE_TRUNCATE | Mirror of users in payment gateway |
| `consolidated_sales` | Denormalized view | WRITE_TRUNCATE | Recalculated daily |
| `usercourseprogresssummarizeds` | Computed summary | WRITE_TRUNCATE | Materialized progress, recalculated |
| `scoresummarizeds` | Computed summary | WRITE_TRUNCATE | Total score, recalculated daily |
| `bills` | Financial record | WRITE_TRUNCATE | Status changes over time |
| `userplans` | Critical mutable entity | **SCD Type 2** | Plan changes are business events |
| `subscriptions` | Critical mutable entity | **SCD Type 2** | Full subscription lifecycle history |
| `crm_contacts` | CRM incremental | **Checkpoint** | Incremental ingestion by `lastmodifieddate` |
| `usercourseprogresses` | Granular progress | **MERGE (Upsert)** | Key: `userCourseProgressId` |
| `audittraffics` | Event log | WRITE_APPEND | Immutable. Each access is an event |
| `scores` | Event log | WRITE_APPEND | Score events are immutable facts |
| `comments` | Event log | WRITE_APPEND | Posted comment is a historical event |
| `likes` | Event log | WRITE_APPEND | Like is an immutable event |
| `certificates` | Event log | WRITE_APPEND | Certificate issued is a completion event |
| `newusereventprogresses` | Event log | WRITE_APPEND | Live event attendance is a fact |
| `specialization_graduates` | Event log | WRITE_APPEND | Graduation is a unique event |

---

## Medallion Architecture

### Raw Layer
Every ingestion writes a new partition — idempotent by design.

```
gs://edtech-raw-{env}/
├── mongodb/
│   └── {collection}/
│       └── ingest_date=YYYY-MM-DD/
│           └── ingest_time=HHMMSS/
│               └── part-00000.ndjson
└── crm/
    └── contacts/
        └── ingest_date=YYYY-MM-DD/
            └── ingest_time=HHMMSS/
                └── part-00000.ndjson
```

Each record carries ingestion metadata:
```json
{
  "_ingest_timestamp": "2026-05-16T00:00:00Z",
  "_ingest_date": "2026-05-16",
  "_ingest_time": "000000",
  "_source": "mongodb",
  "_collection": "users",
  "_ingest_strategy": "snapshot"
}
```

Invalid records are quarantined with `_quarantine_reason` instead of being dropped or crashing the pipeline.

### Silver Layer
15 tables transformed via Dataform ELT inside BigQuery.

Key patterns applied:
- **SCD Type 2** on `userplans` and `subscriptions` — `valid_from`, `valid_to`, `is_current`
- **MERGE** on `usercourseprogresses` — upsert by `userCourseProgressId`
- **WRITE_APPEND** on all event tables — historical log preserved forever
- **Data lineage** — `_transformed_at`, `_pipeline_version` on every silver table
- **Partitioning + Clustering** tailored per table access pattern

### Gold Layer
6 analytical tables, each serving a specific business domain:

| Table | Grain | Description |
|---|---|---|
| `gold_user_360` | 1 row per user | Full user profile: score, termômetro, lifetime, content, trial conversion, revenue |
| `gold_user_adherence` | userId × month | Monthly platform adherence score — 13 month history |
| `gold_churn_risk_signals` | 1 row per user | Churn risk signals: recency, engagement drop, billing issues |
| `gold_user_content_engagement` | userId × contentId | Content engagement with status (not_started / in_progress / completed) |
| `gold_trial_funnel` | 1 row per trial user | Trial → paid conversion funnel with cancel reasons from CRM |
| `gold_trial_daily_journey` | userId × trial_day | Day-by-day trial journey: logins, content, scores, cumulative progress |

---

## Orchestration

9 Airflow DAGs running on Docker with LocalExecutor.

**Domain DAGs (05:00 UTC daily)** — all run in parallel:

```
dag_users          → users, userprofiles, userplans
dag_content        → courses, events, plans
dag_engagement     → usercourseprogresses, summarizeds, eventprogresses, audittraffics
dag_scores         → scores, scoresummarizeds
dag_financial      → subscriptions, bills, consolidated_sales
dag_social         → comments, likes
dag_certifications → certificates, specialization_graduates
dag_crm            → gateway_customers, crm_contacts
```

Each domain DAG follows the same pipeline:
```
lakehouse-generator → lakehouse-ingest → lakehouse-load
```

**dag_dataform (06:00 UTC)** — waits for all 8 domains via `ExternalTaskSensor`, then triggers the Dataform workflow invocation (sources → silver → gold + assertions).

```
[sensor_dag_users]
[sensor_dag_content]
[sensor_dag_engagement]     ─┐
[sensor_dag_scores]          ├→ DataformCreateWorkflowInvocationOperator
[sensor_dag_financial]       │     silver → gold + assertions
[sensor_dag_social]          │
[sensor_dag_certifications] ─┘
[sensor_dag_crm]
```

Failure isolation: if `dag_financial` fails, all other domain DAGs continue unaffected.

---

## Infrastructure — Terraform

All resources managed as code. Zero manual resource creation.

```hcl
# Environments: dev and prod
# Resources provisioned:
# - GCS: edtech-raw-{env}, edtech-quarantine-{env}, edtech-generator-{env}
# - BigQuery: raw_{env}, silver_{env}, gold_{env}
# - IAM: lakehouse-sa with storage.objectAdmin, bigquery.dataEditor, bigquery.jobUser, run.invoker
# - APIs: storage, bigquery, run, dataform, cloudresourcemanager, iam
```

| Resource | Dev | Prod |
|---|---|---|
| Raw retention | 30 days | 365 days |
| Quarantine retention | 7 days | 90 days |

---

## Key Technical Decisions

**Why ELT with Dataform instead of ETL in Python?**
Transformations run inside BigQuery where the data already lives. No data movement, no serialization overhead, full SQL expressiveness, native lineage visualization, and quality assertions as first-class citizens.

**Why SCD Type 2 for `userplans` and `subscriptions`?**
Plan changes and subscription lifecycle events are critical business facts. Overwriting them destroys the ability to answer questions like "what plan did this user have when they churned?"

**Why WRITE_APPEND for event tables?**
Events are immutable facts. A login happened, a comment was posted, a certificate was earned — these facts don't change. Truncating and reloading them daily loses history and breaks time-series analysis.

**Why domain-isolated DAGs instead of one monolithic DAG?**
Failure isolation. If the financial domain fails, engagement data still lands on time. Each domain has its own retry policy, schedule, and ownership. This is the pattern used at scale in production Airflow deployments.

**Why quarantine instead of dropping invalid records?**
Silent data loss is worse than a visible error. Quarantined records are preserved with their rejection reason, making root cause analysis possible. The pipeline continues processing valid records without interruption.

**Why idempotent partitioning by `ingest_date/ingest_time`?**
Each job execution writes to a unique path. Re-running the same job never corrupts existing data — it creates a new partition. This makes backfills and reruns safe by default.

---

## Running Locally

### Prerequisites
- Python 3.11+
- Docker Desktop
- gcloud CLI authenticated (`gcloud auth application-default login`)
- GCP project with Terraform-provisioned infrastructure

### 1. Provision Infrastructure
```bash
cd terraform
terraform init
terraform apply -var-file="environments/dev.tfvars"
```

### 2. Generate Synthetic Data
```bash
cd data_generator
pip install -r requirements.txt
python generate.py --bucket edtech-generator-dev --users 1000 --courses 100 --events 50
```

### 3. Run Ingestion Pipeline
```bash
# Ingest: GCS generator → GCS raw
gcloud run jobs execute lakehouse-ingest --region us-east1 --wait

# Load: GCS raw → BigQuery
gcloud run jobs execute lakehouse-load --region us-east1 --wait
```

### 4. Run Airflow
```bash
cd orchestration
docker-compose up airflow-init
docker-compose up -d
# Access at http://localhost:8080 (admin/admin)
```

### 5. Trigger Dataform
Dataform runs automatically via `dag_dataform` after all domain DAGs complete, or manually from the GCP Console → BigQuery → Dataform → `edtech-lakehouse` repository.

---

## CI/CD

Every pull request triggers:
- **flake8** — PEP8 lint with project-specific ignores
- **black** — format check
- **pytest** — unit tests for ingestion and load logic

Every merge to `main` triggers:
- Docker build + push to Artifact Registry
- Cloud Run Job update

---

## GCP Resources

| Resource | Name |
|---|---|
| Project | `edtech-lakehouse` |
| Region | `us-east1` |
| Generator bucket | `edtech-generator-dev` |
| Raw bucket | `edtech-raw-dev` |
| Quarantine bucket | `edtech-quarantine-dev` |
| BQ raw dataset | `raw_dev` |
| BQ silver dataset | `silver_dev` |
| BQ gold dataset | `gold_dev` |
| Dataform repository | `edtech-lakehouse` |
| Service account | `lakehouse-sa@edtech-lakehouse.iam.gserviceaccount.com` |

---

## Author

**Renato Degelo**  
Data Engineer · CS Academy  
MBA in Data Science & Analytics — USP/Esalq  
[linkedin.com/in/renatodegelo-49792322a](https://linkedin.com/in/renatodegelo-49792322a) · [github.com/natodegelo](https://github.com/natodegelo)

---

*Built with production patterns. Documented with production standards.*