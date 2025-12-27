# ============================================================================
# NIS2 Shield - AWS Terraform Variables
# ============================================================================

# -------------------------------------------------------------------------
# General
# -------------------------------------------------------------------------
variable "project" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "nis2shield"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

# -------------------------------------------------------------------------
# VPC
# -------------------------------------------------------------------------
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# -------------------------------------------------------------------------
# EKS
# -------------------------------------------------------------------------
variable "cluster_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.29"
}

variable "node_instance_types" {
  description = "Instance types for EKS node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 5
}

variable "enable_private_endpoint" {
  description = "Enable private API endpoint for EKS"
  type        = bool
  default     = true
}

variable "enable_public_endpoint" {
  description = "Enable public API endpoint for EKS"
  type        = bool
  default     = true
}

# -------------------------------------------------------------------------
# RDS (PostgreSQL)
# -------------------------------------------------------------------------
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nis2_app"
}

variable "db_username" {
  description = "Master username for database"
  type        = string
  default     = "nis2admin"
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "db_backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "db_deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

# -------------------------------------------------------------------------
# S3 (Backups)
# -------------------------------------------------------------------------
variable "backup_bucket_versioning" {
  description = "Enable versioning for backup bucket"
  type        = bool
  default     = true
}

variable "backup_lifecycle_days" {
  description = "Days before transitioning backups to Glacier"
  type        = number
  default     = 30
}

# -------------------------------------------------------------------------
# Encryption
# -------------------------------------------------------------------------
variable "enable_kms_encryption" {
  description = "Use customer-managed KMS keys"
  type        = bool
  default     = true
}
