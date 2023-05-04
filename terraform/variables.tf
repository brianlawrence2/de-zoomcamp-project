locals {
  data_lake_bucket = "reddit-data-lake"
}

variable "project" {
    description = "de-zoomcamp-project-384603"
    type = string
}

variable "region" {
    default = "us-central1"
    type = string
}

variable "zone" {
    default = "us-central1-a"
    type = string
}

variable "storage_class" {
    default = "STANDARD"
}

variable "email" {
    default = "de-zoomcamp-project@de-zoomcamp-project-384603.iam.gserviceaccount.com"
    type = string
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type        = string
  default     = "subreddit_posts"
}