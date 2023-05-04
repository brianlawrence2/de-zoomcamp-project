terraform {
  required_version = ">= 1.0"
  backend "local" {}
  required_providers {
    google = {
        source = "hashicorp/google"
    }
  }
}

provider "google" {
    project = var.project
    region = var.region
}

resource "google_storage_bucket" "data-lake-bucket" {
    name = "${local.data_lake_bucket}-${var.project}"
    location = var.region

    storage_class = var.storage_class
    uniform_bucket_level_access = true

    versioning {
      enabled = true
    }

    lifecycle_rule {
      action {
        type = "Delete"
      }
      condition {
        age = 30
      }
    }

    force_destroy = true
}

resource "google_compute_instance" "subreddit_stream" {
  boot_disk {
    auto_delete = true
    device_name = "subreddit-stream"

    initialize_params {
      image = "projects/cos-cloud/global/images/cos-stable-105-17412-1-66"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    container-vm = "cos-stable-105-17412-1-66"
    ec-src       = "vm_add-tf"
  }

  machine_type = "e2-micro"

  metadata = {
    gce-container-declaration = "spec:\n  containers:\n  - name: test-4\n    image: gcr.io/de-zoomcamp-project-384603/subreddit_stream:v005\n    stdin: false\n    tty: false\n  restartPolicy: Always\n# This container declaration format is not public API and may change without notice. Please\n# use gcloud command-line tool or Google Cloud Console to run Containers on Google Compute Engine."
  }

  name = "subreddit-stream"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    subnetwork = "projects/${var.project}/regions/${var.region}/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = var.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  zone = "us-central1-a"
}

resource "google_compute_instance" "prefect" {
  boot_disk {
    auto_delete = true
    device_name = "prefect"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-11-bullseye-v20230411"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    ec-src = "vm_add-tf"
  }

  machine_type = "e2-micro"
  name         = "prefect"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    subnetwork = "projects/de-zoomcamp-project-384603/regions/us-central1/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = var.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  tags = ["http-server", "https-server"]
  zone = "us-central1-a"
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset
  project    = var.project
  location   = var.region
}