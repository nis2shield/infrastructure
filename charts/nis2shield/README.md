# NIS2 Shield Helm Chart

Enterprise-ready Kubernetes deployment for NIS2 compliance.

## Quick Start

```bash
# Add the repository (when published)
helm repo add nis2shield https://charts.nis2shield.com

# Install with default values
helm install my-nis2 nis2shield/nis2shield

# Or install from local directory
helm install my-nis2 ./charts/nis2shield
```

## Prerequisites

- Kubernetes 1.25+
- Helm 3.10+
- PV provisioner (if using persistence)

## Features

- **Security Hardening**: Non-root containers, read-only filesystem, PSS restricted
- **Modular Components**: Enable/disable replicator, monitoring via values
- **SIEM Integration**: Fluent Bit sidecar with ES/Splunk/HTTP support
- **Business Continuity**: Encrypted cloud backup via Crypto-Replicator

## Configuration

### Minimal Production Setup

```yaml
# values-prod.yaml
webapp:
  image:
    repository: your-registry/nis2-app
    tag: v1.0.0
  replicaCount: 3
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: app.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: app-tls
        hosts:
          - app.example.com

database:
  persistence:
    size: 20Gi

replicator:
  enabled: true
  cloud:
    apiUrl: https://backup.example.com/api
    tokenSecret: cloud-backup-token
  encryption:
    publicKeySecret: encryption-keys
    keyId: prod-2024

networkPolicies:
  enabled: true
```

```bash
helm install nis2 ./charts/nis2shield -f values-prod.yaml
```

### Enable Crypto-Replicator

```yaml
replicator:
  enabled: true
  dryRun: false
  cloud:
    apiUrl: https://your-backup-api.com
    tokenSecret: my-cloud-token
  encryption:
    publicKeySecret: my-encryption-keys
```

### Use External Database

```yaml
database:
  enabled: true
  external:
    enabled: true
    host: rds.example.com
    port: 5432
    database: nis2_app
    username: nis2user
    existingSecret: rds-credentials
```

## Security

All containers run with:
- `runAsNonRoot: true`
- `readOnlyRootFilesystem: true`
- `allowPrivilegeEscalation: false`
- `capabilities: drop: ALL`

Network policies isolate database access to internal pods only.

## Upgrading

```bash
helm upgrade my-nis2 ./charts/nis2shield -f values-prod.yaml
```

## Uninstalling

```bash
helm uninstall my-nis2
```

**Note**: PVCs are not deleted automatically. Remove manually if needed.
