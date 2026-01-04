# ============================================================================
# NIS2 Shield - Azure Terraform Variables
# ============================================================================

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

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# -------------------------------------------------------------------------
# Virtual Network
# -------------------------------------------------------------------------
variable "vnet_address_space" {
  description = "Virtual network address space"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aks_subnet_cidr" {
  description = "AKS subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "db_subnet_cidr" {
  description = "Database subnet CIDR"
  type        = string
  default     = "10.0.2.0/24"
}

# -------------------------------------------------------------------------
# AKS
# -------------------------------------------------------------------------
variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.29"
}

variable "node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
  default     = 2
}

variable "max_node_count" {
  description = "Maximum nodes for autoscaling"
  type        = number
  default     = 5
}

variable "enable_azure_rbac" {
  description = "Enable Azure RBAC for Kubernetes"
  type        = bool
  default     = true
}

# -------------------------------------------------------------------------
# PostgreSQL
# -------------------------------------------------------------------------
variable "db_sku_name" {
  description = "PostgreSQL SKU"
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "db_storage_mb" {
  description = "Database storage in MB"
  type        = number
  default     = 32768
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nis2_app"
}

variable "db_admin_login" {
  description = "Database admin username"
  type        = string
  default     = "nis2admin"
}

variable "db_ha_enabled" {
  description = "Enable zone-redundant HA"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

# -------------------------------------------------------------------------
# Storage
# -------------------------------------------------------------------------
variable "backup_storage_tier" {
  description = "Storage tier for backups"
  type        = string
  default     = "Hot"
}

# ============================================================================
# NIS2 COMPLIANCE TOGGLES
# ============================================================================
# These variables control optional services that may incur additional costs.
# For FULL NIS2 COMPLIANCE (Art. 21), all should be set to 'true'.
# For development/testing, you may disable some to reduce costs.
#
# Cost Impact Reference (approximate):
#   - Log Analytics: ~$2.30/GB ingested (first 5GB/month free)
#   - Key Vault: ~$0.03 per 10,000 operations (minimal for most use cases)
#   - Geo-Redundant Backup: ~2x backup storage cost
#
# NIS2 Article 21 Requirements:
#   - 21.2(a) Risk Management: Requires monitoring (enable_log_analytics)
#   - 21.2(c) Business Continuity: Requires geo-redundant backup
#   - 21.2(d) Access Control: Requires secrets management (enable_key_vault)
# ============================================================================

variable "enable_log_analytics" {
  description = "Enable Log Analytics workspace for centralized logging and monitoring (NIS2 Art. 21.2.a)"
  type        = bool
  default     = true
}

variable "enable_key_vault" {
  description = "Enable Azure Key Vault for secrets management (NIS2 Art. 21.2.d)"
  type        = bool
  default     = true
}

variable "db_geo_redundant_backup" {
  description = "Enable geo-redundant backup for PostgreSQL disaster recovery (NIS2 Art. 21.2.c)"
  type        = bool
  default     = true
}

# For convenience, a single toggle to enable all NIS2 compliance features
variable "full_nis2_compliance" {
  description = "Enable ALL NIS2 compliance features (overrides individual toggles when true)"
  type        = bool
  default     = false
}

