import json
import logging
import os
from datetime import datetime

from google.cloud import bigquery, storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GCS_PROJECT      = os.environ.get("GCS_PROJECT", "edtech-lakehouse")
GCS_RAW_BUCKET   = os.environ.get("GCS_RAW_BUCKET", "edtech-raw-dev")
BQ_DATASET       = os.environ.get("BQ_DATASET", "raw_dev")
BQ_LOCATION      = os.environ.get("BQ_LOCATION", "us-east1")

COLLECTIONS = [
    "users", "userprofiles", "userplans", "courses", "events", "plans",
    "usercourseprogresses", "usercourseprogresssummarizeds",
    "newusereventprogresses", "audittraffics", "scores", "scoresummarizeds",
    "subscriptions", "bills", "consolidated_sales", "comments", "likes",
    "certificates", "specialization_graduates", "gateway_customers",
    "crm_contacts",
]


def get_latest_partition(storage_client: storage.Client, collection: str) -> str | None:
    source = "crm" if collection == "crm_contacts" else "mongodb"
    entity = "contacts" if collection == "crm_contacts" else collection
    prefix = f"{source}/{entity}/ingest_date="
    blobs = list(storage_client.list_blobs(GCS_RAW_BUCKET, prefix=prefix))
    if not blobs:
        return None
    latest = sorted(blobs, key=lambda b: b.name)[-1]
    return f"gs://{GCS_RAW_BUCKET}/{'/'.join(latest.name.split('/')[:4])}/*.ndjson"


def load_collection(bq_client: bigquery.Client, storage_client: storage.Client, collection: str) -> dict:
    gcs_uri = get_latest_partition(storage_client, collection)

    if not gcs_uri:
        logger.warning(f"No data found in GCS for collection: {collection}")
        return {"collection": collection, "status": "skipped"}

    table_id = f"{GCS_PROJECT}.{BQ_DATASET}.{collection}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
        ignore_unknown_values=True,
    )

    load_job = bq_client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()

    table = bq_client.get_table(table_id)

    log_entry = {
        "severity": "INFO",
        "service": "lakehouse-load",
        "collection": collection,
        "table": table_id,
        "rows_loaded": table.num_rows,
        "gcs_uri": gcs_uri,
        "status": "success",
    }
    logger.info(json.dumps(log_entry))
    return log_entry


def main():
    bq_client      = bigquery.Client(project=GCS_PROJECT, location=BQ_LOCATION)
    storage_client = storage.Client(project=GCS_PROJECT)

    results = []
    for collection in COLLECTIONS:
        result = load_collection(bq_client, storage_client, collection)
        results.append(result)

    total    = len(results)
    skipped  = sum(1 for r in results if r.get("status") == "skipped")
    loaded   = sum(r.get("rows_loaded", 0) for r in results)

    logger.info(json.dumps({
        "severity": "INFO",
        "service": "lakehouse-load",
        "summary": "load complete",
        "collections_loaded": total - skipped,
        "collections_skipped": skipped,
        "total_rows_loaded": loaded,
    }))


if __name__ == "__main__":
    main()