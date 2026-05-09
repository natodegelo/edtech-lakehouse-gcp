terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "gcs" {
  source      = "./modules/gcs"
  project_id  = var.project_id
  env         = var.env
  region      = var.region
  raw_retention_days          = var.raw_retention_days
  quarantine_retention_days   = var.quarantine_retention_days
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  env        = var.env
  region     = var.region
}

module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  env        = var.env
}