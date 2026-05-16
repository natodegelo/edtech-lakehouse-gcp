import json
import logging
import os
from datetime import datetime, timezone

from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GCS_PROJECT           = os.environ.get("GCS_PROJECT",           "edtech-lakehouse")
GCS_GENERATOR_BUCKET  = os.environ.get("GCS_GENERATOR_BUCKET",  "edtech-generator-dev")
GCS_RAW_BUCKET        = os.environ.get("GCS_RAW_BUCKET",        "edtech-raw-dev")
GCS_QUARANTINE_BUCKET = os.environ.get("GCS_QUARANTINE_BUCKET", "edtech-quarantine-dev")

SCHEMA_REQUIRED_FIELDS = {
    "users":                         ["userId", "email", "createdAt"],
    "userprofiles":                  ["userId"],
    "userplans":                     ["userId", "planId"],
    "courses":                       ["courseId", "name"],
    "events":                        ["eventId", "title"],
    "plans":                         ["planId", "name"],
    "usercourseprogresses":          ["userCourseProgressId", "userId", "courseId"],
    "usercourseprogresssummarizeds": ["userId"],
    "newusereventprogresses":        ["userId", "eventId"],
    "audittraffics":                 ["userId", "tag", "createdAt"],
    "scores":                        ["scoreId", "userId", "score"],
    "scoresummarizeds":              ["userId", "score"],
    "subscriptions":                 ["subscriptionId", "userId", "status"],
    "bills":                         ["billId", "userId", "amount", "status"],
    "consolidated_sales":            ["UserId", "bill_id"],
    "comments":                      ["commentId", "userId"],
    "likes":                         ["likeId", "userId"],
    "certificates":                  ["certificateId", "userId", "courseId"],
    "specialization_graduates":      ["userId", "eventId"],
    "gateway_customers":             ["customerId", "userId"],
    "crm_contacts":                  ["hubspot_id", "email"],
}

INGEST_STRATEGY = {
    "users":                         "snapshot",
    "userprofiles":                  "snapshot",
    "courses":                       "snapshot",
    "events":                        "snapshot",
    "plans":                         "snapshot",
    "gateway_customers":             "snapshot",
    "consolidated_sales":            "snapshot",
    "usercourseprogresssummarizeds": "snapshot",
    "scoresummarizeds":              "snapshot",
    "bills":                         "snapshot",
    "userplans":                     "scd2",
    "subscriptions":                 "scd2",
    "usercourseprogresses":          "merge",
    "crm_contacts":                  "checkpoint",
    "audittraffics":                 "append",
    "scores":                        "append",
    "comments":                      "append",
    "likes":                         "append",
    "certificates":                  "append",
    "newusereventprogresses":        "append",
    "specialization_graduates":      "append",
}


def validate_record(record: dict, collection: str) -> tuple[bool, str]:
    required = SCHEMA_REQUIRED_FIELDS.get(collection, [])
    for field in required:
        if field not in record or record[field] is None:
            return False, f"missing required field: {field}"
    return True, ""


def add_metadata(record: dict, collection: str, ingest_date: str, ingest_time: str) -> dict:
    record["_ingest_timestamp"] = datetime.now(tz=timezone.utc).isoformat()
    record["_ingest_date"] = ingest_date
    record["_ingest_time"] = ingest_time
    record["_source"] = "mongodb"
    record["_collection"] = collection
    record["_ingest_strategy"] = INGEST_STRATEGY.get(collection, "snapshot")
    return record


def upload_to_gcs(client: storage.Client, bucket_name: str, blob_path: str, content: str) -> None:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content, content_type="application/x-ndjson")


def read_latest_from_generator(client: storage.Client, collection: str) -> list[dict] | None:
    """Lê o arquivo JSON mais recente do bucket generator para a collection."""
    bucket = client.bucket(GCS_GENERATOR_BUCKET)
    blobs = list(bucket.list_blobs(prefix=f"{collection}/"))

    if not blobs:
        return None

    # Ordena por nome — ingest_date e ingest_time no path garantem ordem lexicográfica correta
    latest_blob = sorted(blobs, key=lambda b: b.name)[-1]
    content = latest_blob.download_as_text(encoding="utf-8")
    return json.loads(content)


def ingest_collection(client: storage.Client, collection: str, ingest_date: str, ingest_time: str) -> dict:
    records = read_latest_from_generator(client, collection)

    if records is None:
        logger.warning(f"Collection not found in generator bucket: {collection}")
        return {"collection": collection, "status": "skipped"}

    valid_lines      = []
    quarantine_lines = []

    for record in records:
        is_valid, reason = validate_record(record, collection)
        if is_valid:
            record = add_metadata(record, collection, ingest_date, ingest_time)
            valid_lines.append(json.dumps(record, ensure_ascii=False))
        else:
            record["_quarantine_reason"] = reason
            record["_ingest_date"]       = ingest_date
            quarantine_lines.append(json.dumps(record, ensure_ascii=False))

    source  = "crm"      if collection == "crm_contacts" else "mongodb"
    entity  = "contacts" if collection == "crm_contacts" else collection
    blob_path = f"{source}/{entity}/ingest_date={ingest_date}/ingest_time={ingest_time}/part-00000.ndjson"

    if valid_lines:
        upload_to_gcs(client, GCS_RAW_BUCKET, blob_path, "\n".join(valid_lines))

    if quarantine_lines:
        upload_to_gcs(client, GCS_QUARANTINE_BUCKET, blob_path, "\n".join(quarantine_lines))

    log_entry = {
        "severity":            "INFO",
        "service":             "lakehouse-ingest",
        "collection":          collection,
        "strategy":            INGEST_STRATEGY.get(collection, "snapshot"),
        "records_processed":   len(records),
        "records_valid":       len(valid_lines),
        "records_quarantined": len(quarantine_lines),
        "ingest_date":         ingest_date,
        "ingest_time":         ingest_time,
        "gcs_path":            f"gs://{GCS_RAW_BUCKET}/{blob_path}",
    }
    logger.info(json.dumps(log_entry))

    return log_entry


def main():
    now = datetime.now(tz=timezone.utc)
    ingest_date = now.strftime("%Y-%m-%d")
    ingest_time = now.strftime("%H%M%S")

    client = storage.Client(project=GCS_PROJECT)

    results = []
    for collection in SCHEMA_REQUIRED_FIELDS.keys():
        result = ingest_collection(client, collection, ingest_date, ingest_time)
        results.append(result)

    total      = len(results)
    skipped    = sum(1 for r in results if r.get("status") == "skipped")
    quarantined = sum(r.get("records_quarantined", 0) for r in results)

    logger.info(json.dumps({
        "severity":                  "INFO",
        "service":                   "lakehouse-ingest",
        "summary":                   "ingestion complete",
        "collections_processed":     total - skipped,
        "collections_skipped":       skipped,
        "total_records_quarantined": quarantined,
        "ingest_date":               ingest_date,
        "ingest_time":               ingest_time,
    }))


if __name__ == "__main__":
    main()