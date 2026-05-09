variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-east1"
}

variable "env" {
  description = "Environment: dev or prod"
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env must be dev or prod."
  }
}

variable "raw_retention_days" {
  description = "Retention in days for raw GCS bucket"
  type        = number
  default     = 30
}

variable "quarantine_retention_days" {
  description = "Retention in days for quarantine GCS bucket"
  type        = number
  default     = 7
}