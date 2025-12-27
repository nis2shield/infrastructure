# Security Advisories

This document describes how NIS2 Shield handles security vulnerabilities and provides guidance for organizations deploying the software.

---

## Subscribing to Security Notifications

### GitHub Security Advisories

We publish security advisories through GitHub's built-in security advisory feature:

📢 **Watch this repository** with "Security alerts" enabled:
https://github.com/nis2shield/infrastructure/security/advisories

### Mailing List

For organizations requiring email notifications, subscribe to our security mailing list:
- **Email**: security-announce@nis2shield.com

---

## Vulnerability Disclosure Timeline

| Day | Action |
|-----|--------|
| 0 | Vulnerability reported to security@nis2shield.com |
| 1-2 | Triage and severity assessment (CVSS v3.1) |
| 7 | Patch development for Critical/High |
| 14 | Patch development for Medium/Low |
| 30 | Public disclosure (coordinated) |

For vulnerabilities actively exploited in the wild, we may accelerate this timeline.

---

## Current Advisories

| ID | Severity | Component | Status | Published |
|----|----------|-----------|--------|-----------|
| - | - | - | No active advisories | - |

*Last checked: 2025-12-27*

---

## Dependency Monitoring

We actively monitor security advisories for our key dependencies:

### Core Dependencies

| Component | Source | Subscribe |
|-----------|--------|-----------|
| Python | python.org/security | [RSS](https://www.python.org/dev/pep-0101/) |
| Django | djangoproject.com | [Mailing List](https://groups.google.com/g/django-announce) |
| PostgreSQL | postgresql.org | [Mailing List](https://www.postgresql.org/support/security/) |
| Fluent Bit | fluentbit.io | [GitHub Releases](https://github.com/fluent/fluent-bit/releases) |
| cryptography | pypi.org | [GitHub Security](https://github.com/pyca/cryptography/security) |

### Container Base Images

| Image | Source | Monitor |
|-------|--------|---------|
| python:3.11-slim | Docker Hub | [Security Scanning](https://hub.docker.com/_/python) |
| postgres:15-alpine | Docker Hub | [Security Scanning](https://hub.docker.com/_/postgres) |
| fluent/fluent-bit | Docker Hub | [Releases](https://github.com/fluent/fluent-bit/releases) |

### Kubernetes/Cloud

| Component | Source |
|-----------|--------|
| Helm | [Security](https://github.com/helm/helm/security/advisories) |
| AWS EKS | [AWS Security Bulletins](https://aws.amazon.com/security/security-bulletins/) |
| GCP GKE | [GCP Security Bulletins](https://cloud.google.com/kubernetes-engine/docs/security-bulletins) |
| Azure AKS | [Azure Updates](https://azure.microsoft.com/en-us/updates/?category=security) |

---

## Severity Ratings

We use CVSS v3.1 for severity classification:

| Rating | CVSS Score | Response Time | Example |
|--------|------------|---------------|---------|
| Critical | 9.0 - 10.0 | 24-48 hours | RCE, data breach, container escape |
| High | 7.0 - 8.9 | 7 days | Auth bypass, privilege escalation |
| Medium | 4.0 - 6.9 | 14 days | Information disclosure, DoS |
| Low | 0.1 - 3.9 | 30 days | Minor config issues |

---

## Affected Version Matrix

When an advisory is published, we provide clear version guidance:

```markdown
## Affected Versions
- v1.0.0 - v1.0.2: Vulnerable
- v1.0.3+: Patched

## Upgrade Path
docker pull nis2shield/crypto-replicator:v1.0.3
helm upgrade nis2shield ./charts/nis2shield --set image.tag=v1.0.3
```

---

## Security Hardening Recommendations

### For New Deployments

1. Always use the **latest patch version**
2. Enable **NetworkPolicies** in Kubernetes
3. Use **external secrets** (Vault, AWS Secrets Manager)
4. Configure **TLS** for all connections
5. Enable **audit logging** to SIEM

### For Existing Deployments

1. Subscribe to security notifications
2. Run `docker pull` monthly to get base image patches
3. Review `CIS_COMPLIANCE.md` quarterly
4. Test disaster recovery monthly

---

## Coordinated Disclosure

We follow responsible disclosure practices:

1. **Private Report**: Vulnerabilities reported privately
2. **Acknowledgment**: We confirm receipt within 48 hours
3. **Assessment**: We assess severity and impact
4. **Patch Development**: We develop and test a fix
5. **Coordinated Release**: Advisory and patch released together
6. **Credit**: Researchers credited (if desired)

### Hall of Fame

We thank security researchers who have helped improve NIS2 Shield:

| Researcher | Date | Advisory |
|------------|------|----------|
| - | - | None yet - be the first! |

---

## Emergency Contact

For actively exploited vulnerabilities or imminent threats:

📧 **security@nis2shield.com** (response within 24 hours)

For general security questions, use GitHub Discussions.

---

*Last updated: 2025-12-27*
