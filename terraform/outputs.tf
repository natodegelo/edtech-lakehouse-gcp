output "raw_bucket_name" {
  description = "GCS raw bucket name"
  value       = module.gcs.raw_bucket_name
}

output "quarantine_bucket_name" {
  description = "GCS quarantine bucket name"
  value       = module.gcs.quarantine_bucket_name
}

output "raw_dataset_id" {
  description = "BigQuery raw dataset ID"
  value       = module.bigquery.raw_dataset_id
}

output "silver_dataset_id" {
  description = "BigQuery silver dataset ID"
  value       = module.bigquery.silver_dataset_id
}

output "gold_dataset_id" {
  description = "BigQuery gold dataset ID"
  value       = module.bigquery.gold_dataset_id
}

output "service_account_email" {
  description = "Service account email"
  value       = module.iam.service_account_email
}