resource "google_storage_bucket" "raw" {
  name          = "edtech-raw-${var.env}"
  project       = var.project_id
  location      = var.region
  force_destroy = var.env == "dev" ? true : false

  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.raw_retention_days
    }
  }

  labels = {
    env   = var.env
    layer = "raw"
  }
}

resource "google_storage_bucket" "quarantine" {
  name          = "edtech-quarantine-${var.env}"
  project       = var.project_id
  location      = var.region
  force_destroy = var.env == "dev" ? true : false

  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.quarantine_retention_days
    }
  }

  labels = {
    env   = var.env
    layer = "quarantine"
  }
}