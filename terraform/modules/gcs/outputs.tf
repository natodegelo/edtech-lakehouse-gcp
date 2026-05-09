output "raw_bucket_name" {
  value = google_storage_bucket.raw.name
}

output "quarantine_bucket_name" {
  value = google_storage_bucket.quarantine.name
}