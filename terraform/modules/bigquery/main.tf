resource "google_bigquery_dataset" "raw" {
  dataset_id  = "raw_${var.env}"
  project     = var.project_id
  location    = var.region
  description = "Raw layer — espelho do GCS sem transformação"

  labels = {
    env   = var.env
    layer = "raw"
  }
}

resource "google_bigquery_dataset" "silver" {
  dataset_id  = "silver_${var.env}"
  project     = var.project_id
  location    = var.region
  description = "Silver layer — dados limpos, normalizados e com data lineage"

  labels = {
    env   = var.env
    layer = "silver"
  }
}

resource "google_bigquery_dataset" "gold" {
  dataset_id  = "gold_${var.env}"
  project     = var.project_id
  location    = var.region
  description = "Gold layer — tabelas analíticas prontas para consumo"

  labels = {
    env   = var.env
    layer = "gold"
  }
}