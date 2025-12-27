# Security Policy

## Overview

NIS2 Shield Infrastructure is designed with **security-by-default** principles to support NIS2 directive compliance for critical infrastructure sectors including healthcare, energy, and public administration.

This document describes our security posture, threat model, and vulnerability handling process.

---

## Supported Versions

| Version | Supported | Security Updates |
|---------|-----------|------------------|
| 0.3.x   | ✅ Active  | Yes |
| 0.2.x   | ⚠️ Limited | Critical only |
| 0.1.x   | ❌ EOL     | No |

---

## Threat Model

### Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│  TRUSTED ZONE (Internal Network)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   webapp    │  │  database   │  │    crypto-replicator    │  │
│  │  (Django)   │  │ (PostgreSQL)│  │  (encrypted backup)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                │                      │               │
│         ▼                ▼                      ▼               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Internal Docker Network                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌─────────────────┐                    ┌──────────────────────────┐
│  UNTRUSTED ZONE │                    │  SEMI-TRUSTED ZONE       │
│  (Internet)     │                    │  (Cloud Storage)         │
│  - End users    │                    │  - Encrypted data only   │
│  - Attackers    │                    │  - No private keys       │
└─────────────────┘                    └──────────────────────────┘
```

### Assets and Sensitivity

| Asset | Sensitivity | Protection |
|-------|-------------|------------|
| User PII | HIGH | Encrypted in logs (Fernet), DB encryption |
| Database credentials | CRITICAL | Environment variables, Secrets Manager |
| RSA private key | CRITICAL | Offline storage, never in container |
| Audit logs | HIGH | Immutable, HMAC signed |
| Session tokens | HIGH | Secure cookies, fingerprint validation |

### Attack Vectors Considered

| Vector | Mitigation |
|--------|------------|
| Container escape | Non-root user, read-only filesystem, dropped capabilities |
| Log injection | JSON structured logging, sanitized inputs |
| Database compromise | Encrypted backups, separate credentials per service |
| Cloud provider breach | Zero-trust encryption (cloud cannot decrypt) |
| Supply chain attack | Verified base images, SBOM generation |
| Insider threat | Audit logging, principle of least privilege |

---

## Container Hardening

All containers implement defense-in-depth:

### Security Controls

```yaml
# Applied to all services
security_opt:
  - no-new-privileges:true
user: "1000:1000"           # Non-root
read_only: true             # Immutable filesystem
cap_drop:
  - ALL                      # Drop all capabilities
```

### Kubernetes Pod Security Standards

The Helm chart enforces **Restricted** PSS profile:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop: ["ALL"]
```

---

## Cryptographic Specifications

### Encryption at Rest

| Component | Algorithm | Key Size | Mode |
|-----------|-----------|----------|------|
| Log field encryption | AES | 256-bit | Fernet (CBC+HMAC) |
| Cloud backup payload | AES | 256-bit | GCM |
| Cloud backup key wrap | RSA | 2048-bit | OAEP-SHA256 |
| Database (RDS/Cloud SQL) | AES | 256-bit | Provider managed |

### Encryption in Transit

| Connection | Protocol | Minimum Version |
|------------|----------|-----------------|
| HTTPS (Ingress) | TLS | 1.2 |
| Database | TLS | 1.2 |
| SIEM forwarding | TLS | 1.2 |
| Cloud backup API | TLS | 1.2 |

### Key Management

- **RSA Key Pair**: Generated offline, private key never enters container
- **Session Keys**: Unique per-message, derived from CSPRNG
- **Key Rotation**: Supported via `KeyRotationManager`, historic keys retained for decryption
- **Key Storage**: Kubernetes Secrets or cloud-native (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

See [CRYPTOGRAPHY.md](docs/CRYPTOGRAPHY.md) for detailed specifications.

---

## Network Security

### Docker Compose

Services communicate via isolated Docker networks:
- `app-network`: webapp ↔ database ↔ replicator
- No service exposes ports to host except webapp (8000)

### Kubernetes NetworkPolicies

```yaml
# Database accessible only from webapp/replicator pods
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: database
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/instance: nis2shield
```

---

## Secrets Management

### Development
- `.env` files (gitignored)
- Environment variables

### Production (Kubernetes)
- Kubernetes Secrets
- External Secrets Operator integration
- HashiCorp Vault annotations ready

### Cloud (Terraform)
- AWS Secrets Manager (auto-generated)
- GCP Secret Manager
- Azure Key Vault

**Never store secrets in:**
- Container images
- Git repositories
- ConfigMaps

---

## Vulnerability Disclosure

### Reporting Process

**Do not report security vulnerabilities through public GitHub issues.**

Report via email: **security@nis2shield.com**

Include:
1. Vulnerability type (e.g., container escape, credential exposure)
2. Affected component and version
3. Steps to reproduce
4. Potential impact assessment
5. Any suggested remediation

### Response Timeline

| Severity | Initial Response | Fix Target |
|----------|------------------|------------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 14 days |
| Medium | 7 days | 30 days |
| Low | 14 days | Next release |

### Severity Classification (CVSS v3.1)

| Rating | CVSS Score | Example |
|--------|------------|---------|
| Critical | 9.0-10.0 | RCE, data exfiltration |
| High | 7.0-8.9 | Container escape, auth bypass |
| Medium | 4.0-6.9 | Information disclosure |
| Low | 0.1-3.9 | Minor misconfiguration |

---

## Security Best Practices for Deployment

### Pre-Deployment Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate unique RSA key pair for Crypto-Replicator
- [ ] Configure TLS for Ingress
- [ ] Enable NetworkPolicies (Kubernetes)
- [ ] Set up log forwarding to SIEM
- [ ] Configure backup encryption
- [ ] Document recovery procedures

### Operational Security

1. **Secret Rotation**: Rotate database passwords quarterly
2. **Key Rotation**: Rotate RSA keys annually (use `KeyRotationManager`)
3. **Image Updates**: Pull base images monthly
4. **Access Control**: Use RBAC, audit admin actions
5. **DR Testing**: Run `restore-test.sh` monthly

### Monitoring Alerts

Configure alerts for:
- Failed authentication attempts (>10/minute)
- Container restarts (>3/hour)
- Backup age (>24 hours)
- Certificate expiration (<30 days)

---

## Compliance Mapping

| Standard | Relevance | Documentation |
|----------|-----------|---------------|
| NIS2 Directive | Primary target | [NIS2_SELF_ASSESSMENT.md](docs/NIS2_SELF_ASSESSMENT.md) |
| CIS Docker Benchmark | Container hardening | [CIS_COMPLIANCE.md](docs/CIS_COMPLIANCE.md) |
| CIS Kubernetes Benchmark | K8s hardening | [CIS_COMPLIANCE.md](docs/CIS_COMPLIANCE.md) |
| GDPR | Data protection | PII encryption, audit logs |
| ISO 27001 | Information security | Partial coverage |

---

## Contact

- **Security issues**: security@nis2shield.com
- **General questions**: https://github.com/nis2shield/infrastructure/discussions
- **Documentation**: https://nis2shield.com

---

*Last updated: 2025-12-27*
