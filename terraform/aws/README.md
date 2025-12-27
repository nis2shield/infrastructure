# NIS2 Shield - AWS Terraform Module

Terraform module for deploying NIS2 Shield on AWS with EKS.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          VPC                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │   Public Subnets    │  │      Private Subnets        │   │
│  │   ┌─────────────┐   │  │   ┌─────────────────────┐   │   │
│  │   │ NAT Gateway │   │  │   │       EKS           │   │   │
│  │   │     ALB     │   │  │   │  ┌───────────────┐  │   │   │
│  │   └─────────────┘   │  │   │  │ NIS2 Shield   │  │   │   │
│  └─────────────────────┘  │   │  │ (Helm Chart)  │  │   │   │
│                           │   │  └───────────────┘  │   │   │
│                           │   └─────────────────────┘   │   │
│                           │   ┌─────────────────────┐   │   │
│                           │   │        RDS          │   │   │
│                           │   │    (PostgreSQL)     │   │   │
│                           │   └─────────────────────┘   │   │
│                           └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     S3       │
                    │  (Backups)   │
                    └──────────────┘
```

## Quick Start

```bash
# Initialize
cd terraform/aws
terraform init

# Review plan
terraform plan -var-file="prod.tfvars"

# Apply
terraform apply -var-file="prod.tfvars"

# Get kubeconfig
aws eks update-kubeconfig --name $(terraform output -raw cluster_name) --region $(terraform output -raw region)

# Install Helm chart
helm install nis2shield ../charts/nis2shield -f values-aws.yaml
```

## Prerequisites

- AWS CLI configured
- Terraform 1.5+
- kubectl
- Helm 3.10+

## Resources Created

| Resource | Description |
|----------|-------------|
| VPC | Isolated network with public/private subnets |
| EKS | Managed Kubernetes cluster |
| RDS | PostgreSQL 15 with encryption |
| S3 | Encrypted bucket for backups |
| KMS | Customer-managed encryption keys |
| IAM | Least-privilege roles and policies |

## Inputs

See [variables.tf](variables.tf) for all configurable options.

## Outputs

| Name | Description |
|------|-------------|
| cluster_name | EKS cluster name |
| cluster_endpoint | Kubernetes API URL |
| database_endpoint | RDS connection string |
| backup_bucket | S3 bucket name |

## Security Features

- VPC with private subnets only for workloads
- RDS encryption at rest with KMS
- S3 bucket encryption and versioning
- EKS with private API endpoint option
- Security groups with minimal ingress
