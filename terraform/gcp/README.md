# NIS2 Shield - GCP Terraform Module

Terraform module for deploying NIS2 Shield on Google Cloud with GKE.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         VPC                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Subnet                             │    │
│  │   ┌─────────────────────────────────────────────┐   │    │
│  │   │              GKE Cluster                     │   │    │
│  │   │        ┌───────────────────────┐            │   │    │
│  │   │        │     NIS2 Shield       │            │   │    │
│  │   │        │    (Helm Chart)       │            │   │    │
│  │   │        └───────────────────────┘            │   │    │
│  │   └─────────────────────────────────────────────┘   │    │
│  │   ┌─────────────────────────────────────────────┐   │    │
│  │   │           Cloud SQL (PostgreSQL)             │   │    │
│  │   └─────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ Cloud Storage │
                   │   (Backups)   │
                   └───────────────┘
```

## Quick Start

```bash
cd terraform/gcp
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Configure kubectl
gcloud container clusters get-credentials $(terraform output -raw cluster_name) --region $(terraform output -raw region)

# Install Helm chart
helm install nis2shield ../charts/nis2shield -f values-gcp.yaml
```

## Prerequisites

- gcloud CLI configured
- Terraform 1.5+
- kubectl
- Helm 3.10+

## Resources Created

| Resource | Description |
|----------|-------------|
| VPC | Custom VPC with private Google access |
| GKE | Autopilot or Standard cluster |
| Cloud SQL | PostgreSQL 15 with encryption |
| Cloud Storage | Encrypted bucket for backups |
| Cloud KMS | Customer-managed encryption keys |
| IAM | Service accounts with least privilege |

## Inputs

See [variables.tf](variables.tf) for all options.

## Security Features

- Private GKE cluster (optional)
- Cloud SQL with private IP only
- CMEK encryption for all data
- Workload Identity for pods
- VPC Service Controls ready
