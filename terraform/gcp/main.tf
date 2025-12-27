# ============================================================================
# NIS2 Shield - GCP Infrastructure
# ============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Uncomment for remote state
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "nis2shield"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  labels = {
    project     = var.project_name
    environment = var.environment
    managed-by  = "terraform"
  }
}

# -------------------------------------------------------------------------
# Enable Required APIs
# -------------------------------------------------------------------------
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudkms.googleapis.com",
    "secretmanager.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# -------------------------------------------------------------------------
# VPC Network
# -------------------------------------------------------------------------
resource "google_compute_network" "main" {
  name                    = "${local.name_prefix}-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.apis]
}

resource "google_compute_subnetwork" "main" {
  name          = "${local.name_prefix}-subnet"
  ip_cidr_range = var.network_cidr
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }
}

# Cloud NAT for private GKE nodes
resource "google_compute_router" "main" {
  name    = "${local.name_prefix}-router"
  region  = var.region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  name                               = "${local.name_prefix}-nat"
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# -------------------------------------------------------------------------
# Cloud KMS (if enabled)
# -------------------------------------------------------------------------
resource "google_kms_key_ring" "main" {
  count = var.enable_cmek ? 1 : 0

  name     = "${local.name_prefix}-keyring"
  location = var.region
  project  = var.project_id

  depends_on = [google_project_service.apis]
}

resource "google_kms_crypto_key" "main" {
  count = var.enable_cmek ? 1 : 0

  name            = "${local.name_prefix}-key"
  key_ring        = google_kms_key_ring.main[0].id
  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }
}

# -------------------------------------------------------------------------
# GKE Cluster
# -------------------------------------------------------------------------
resource "google_container_cluster" "main" {
  name     = local.name_prefix
  location = var.region
  project  = var.project_id

  # Use Autopilot or Standard
  dynamic "cluster_autoscaling" {
    for_each = var.gke_autopilot ? [] : [1]
    content {
      enabled = true
      resource_limits {
        resource_type = "cpu"
        minimum       = 2
        maximum       = 20
      }
      resource_limits {
        resource_type = "memory"
        minimum       = 4
        maximum       = 80
      }
    }
  }

  # Enable Autopilot
  enable_autopilot = var.gke_autopilot

  # Network
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Private cluster
  private_cluster_config {
    enable_private_nodes    = var.enable_private_cluster
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  # Security
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Remove default node pool (we'll create our own)
  dynamic "node_pool" {
    for_each = var.gke_autopilot ? [] : [1]
    content {
      name       = "default-pool"
      node_count = var.node_count

      node_config {
        machine_type = var.node_machine_type
        disk_size_gb = 50
        disk_type    = "pd-standard"

        oauth_scopes = [
          "https://www.googleapis.com/auth/cloud-platform"
        ]

        workload_metadata_config {
          mode = "GKE_METADATA"
        }

        shielded_instance_config {
          enable_secure_boot = true
        }

        labels = local.labels
      }

      autoscaling {
        min_node_count = 1
        max_node_count = var.max_node_count
      }
    }
  }

  resource_labels = local.labels

  depends_on = [google_project_service.apis]
}

# -------------------------------------------------------------------------
# Cloud SQL
# -------------------------------------------------------------------------
resource "google_compute_global_address" "sql_private_ip" {
  name          = "${local.name_prefix}-sql-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
  project       = var.project_id
}

resource "google_service_networking_connection" "sql_private" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.sql_private_ip.name]
}

resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "google_sql_database_instance" "main" {
  name             = "${local.name_prefix}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  settings {
    tier              = var.db_tier
    disk_size         = var.db_disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    availability_type = var.db_ha_enabled ? "REGIONAL" : "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }

    backup_configuration {
      enabled            = var.db_backup_enabled
      start_time         = "03:00"
      binary_log_enabled = false
      backup_retention_settings {
        retained_backups = 7
      }
    }

    insights_config {
      query_insights_enabled  = true
      record_client_address   = false
      record_application_tags = false
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    user_labels = local.labels
  }

  deletion_protection = true

  depends_on = [google_service_networking_connection.sql_private]
}

resource "google_sql_database" "main" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

resource "google_sql_user" "main" {
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
  project  = var.project_id
}

# Store password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.name_prefix}-db-password"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = local.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# -------------------------------------------------------------------------
# Cloud Storage for Backups
# -------------------------------------------------------------------------
resource "google_storage_bucket" "backups" {
  name          = "${local.name_prefix}-backups-${var.project_id}"
  location      = var.region
  project       = var.project_id
  storage_class = var.backup_storage_class

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.backup_lifecycle_days
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  dynamic "encryption" {
    for_each = var.enable_cmek ? [1] : []
    content {
      default_kms_key_name = google_kms_crypto_key.main[0].id
    }
  }

  labels = local.labels
}

# -------------------------------------------------------------------------
# Outputs
# -------------------------------------------------------------------------
output "region" {
  value = var.region
}

output "cluster_name" {
  value = google_container_cluster.main.name
}

output "cluster_endpoint" {
  value = google_container_cluster.main.endpoint
}

output "database_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "database_private_ip" {
  value = google_sql_database_instance.main.private_ip_address
}

output "backup_bucket" {
  value = google_storage_bucket.backups.name
}

output "db_secret_name" {
  value = google_secret_manager_secret.db_password.secret_id
}
