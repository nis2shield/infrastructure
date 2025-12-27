# NIS2 Shield - Azure Terraform Module

Terraform module for deploying NIS2 Shield on Azure with AKS.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Virtual Network                        │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │  AKS Subnet         │  │      Database Subnet        │   │
│  │   ┌─────────────┐   │  │   ┌─────────────────────┐   │   │
│  │   │    AKS      │   │  │   │ Azure Database for  │   │   │
│  │   │  Cluster    │   │  │   │    PostgreSQL       │   │   │
│  │   │             │   │  │   │ (Flexible Server)   │   │   │
│  │   │ NIS2 Shield │   │  │   └─────────────────────┘   │   │
│  │   └─────────────┘   │  │                             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Blob Storage │
                   │   (Backups)   │
                   └───────────────┘
```

## Quick Start

```bash
cd terraform/azure
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Configure kubectl
az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw cluster_name)

# Install Helm chart
helm install nis2shield ../charts/nis2shield -f values-azure.yaml
```

## Prerequisites

- Azure CLI configured
- Terraform 1.5+
- kubectl
- Helm 3.10+

## Resources Created

| Resource | Description |
|----------|-------------|
| Resource Group | Container for all resources |
| Virtual Network | Isolated network with subnets |
| AKS | Managed Kubernetes cluster |
| PostgreSQL Flexible Server | Managed database with encryption |
| Storage Account | Encrypted blob storage for backups |
| Key Vault | Secrets and encryption keys |

## Inputs

See [variables.tf](variables.tf) for all options.

## Security Features

- AKS with Azure RBAC and AD integration
- PostgreSQL with private endpoint
- Storage account with encryption
- Key Vault for secrets management
- Network security groups
