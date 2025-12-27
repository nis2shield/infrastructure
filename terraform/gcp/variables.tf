# ============================================================================
# NIS2 Shield - GCP Terraform Variables
# ============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP zone for zonal resources"
  type        = string
  default     = "europe-west1-b"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "nis2shield"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# -------------------------------------------------------------------------
# VPC
# -------------------------------------------------------------------------
variable "network_cidr" {
  description = "CIDR for the VPC subnet"
  type        = string
  default     = "10.0.0.0/16"
}

variable "pods_cidr" {
  description = "Secondary CIDR for GKE pods"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr" {
  description = "Secondary CIDR for GKE services"
  type        = string
  default     = "10.2.0.0/16"
}

# -------------------------------------------------------------------------
# GKE
# -------------------------------------------------------------------------
variable "gke_version" {
  description = "GKE Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "gke_autopilot" {
  description = "Enable GKE Autopilot mode"
  type        = bool
  default     = false
}

variable "node_machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
  default     = "e2-medium"
}

variable "node_count" {
  description = "Number of nodes per zone"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum nodes for autoscaling"
  type        = number
  default     = 5
}

variable "enable_private_cluster" {
  description = "Enable private GKE cluster"
  type        = bool
  default     = true
}

variable "master_ipv4_cidr_block" {
  description = "CIDR for GKE master"
  type        = string
  default     = "172.16.0.0/28"
}

# -------------------------------------------------------------------------
# Cloud SQL
# -------------------------------------------------------------------------
variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-1-3840"
}

variable "db_disk_size" {
  description = "Database disk size in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nis2_app"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "nis2admin"
}

variable "db_ha_enabled" {
  description = "Enable high availability"
  type        = bool
  default     = true
}

variable "db_backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# -------------------------------------------------------------------------
# Cloud Storage
# -------------------------------------------------------------------------
variable "backup_storage_class" {
  description = "Storage class for backup bucket"
  type        = string
  default     = "STANDARD"
}

variable "backup_lifecycle_days" {
  description = "Days before transitioning to Nearline"
  type        = number
  default     = 30
}

# -------------------------------------------------------------------------
# Encryption
# -------------------------------------------------------------------------
variable "enable_cmek" {
  description = "Enable Customer Managed Encryption Keys"
  type        = bool
  default     = true
}
