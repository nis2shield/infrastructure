# NIS2 Self-Assessment Checklist

Compliance verification for NIS2 Directive Article 21 requirements.

Use this checklist for internal audits and procurement documentation.

---

## Instructions

For each requirement:
1. Review the **Implementation** column
2. Check the **Evidence** location
3. Mark status: ✅ Compliant | ⚠️ Partial | ❌ Gap
4. Document any remediation needed

---

## Article 21(a) - Risk Analysis and Information System Security

> "Policies on risk analysis and information system security"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21a.1 | Risk analysis performed | Threat model documented | [SECURITY.md](../SECURITY.md) | ✅ |
| 21a.2 | Security policies defined | Hardening standards | [CIS_COMPLIANCE.md](CIS_COMPLIANCE.md) | ✅ |
| 21a.3 | Attack surface minimized | Read-only containers, dropped caps | `docker-compose.yml` | ✅ |
| 21a.4 | Configuration hardening | Non-root, no-new-privileges | `docker-compose.yml` | ✅ |
| 21a.5 | Vulnerability management | CI pipeline with linting | `.github/workflows/` | ✅ |

---

## Article 21(b) - Incident Handling

> "Incident handling"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21b.1 | Incident detection | SIEM-ready logging (Fluent Bit) | `monitoring/fluent-bit.conf` | ✅ |
| 21b.2 | Structured audit logs | JSON/CEF format with HMAC | `django-nis2-shield` | ✅ |
| 21b.3 | Log integrity | HMAC signing of log entries | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |
| 21b.4 | Incident response plan | Vulnerability disclosure process | [SECURITY.md](../SECURITY.md) | ✅ |
| 21b.5 | 24h notification capability | SIEM integration, webhooks | `django-nis2-shield` config | ✅ |

---

## Article 21(c) - Business Continuity and Crisis Management

> "Business continuity, such as backup management and disaster recovery"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21c.1 | Automated backups | Every 6 hours, 7-day retention | `docker-compose.yml` (db-backup) | ✅ |
| 21c.2 | Backup encryption | <!--status-21.2.c-->✅ PASS<!--end--> | <!--evidence-21.2.c-->Backup Workflow verified (log_analyzer) (Last Check: 2025-12-27)<!--end--> | ✅ |
| 21c.3 | Offsite backup | Crypto-Replicator to cloud | `crypto-replicator/` | ✅ |
| 21c.4 | Zero-trust cloud | AES-256-GCM + RSA-OAEP | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |
| 21c.5 | DR testing | Automated restore test script | `scripts/restore-test.sh` | ✅ |
| 21c.6 | DR documentation | Recovery procedures documented | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |
| 21c.7 | Key rotation | KeyRotationManager | `crypto-replicator/key_manager.py` | ✅ |

---

## Article 21(d) - Supply Chain Security

> "Supply chain security, including security-related aspects concerning relationships between each entity and its direct suppliers or service providers"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21d.1 | Verified base images | Official images (python, postgres) | Dockerfiles | ✅ |
| 21d.2 | Dependency pinning | requirements.txt with versions | `crypto-replicator/requirements.txt` | ✅ |
| 21d.3 | Open source transparency | MIT license, public repository | GitHub | ✅ |
| 21d.4 | SBOM generation | Recommended in CI | Add Syft to CI | ⚠️ |
| 21d.5 | Vulnerability scanning | Hadolint in CI | `.github/workflows/` | ✅ |

---

## Article 21(e) - Security in Network and Systems Acquisition

> "Security in network and information systems acquisition, development and maintenance, including vulnerability handling and disclosure"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21e.1 | Secure development | Code review, CI/CD | GitHub PRs, Actions | ✅ |
| 21e.2 | Vulnerability disclosure | security@nis2shield.com | [SECURITY.md](../SECURITY.md) | ✅ |
| 21e.3 | Response timelines | Defined SLAs by severity | [SECURITY.md](../SECURITY.md) | ✅ |
| 21e.4 | Patch management | Regular image updates | Monthly schedule recommended | ⚠️ |

---

## Article 21(f) - Policies on Cryptography

> "Policies and procedures regarding the use of cryptography and, where appropriate, encryption"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21f.1 | Encryption at rest | <!--status-21.2.f-->❌ FAIL<!--end--> | <!--evidence-21.2.f-->Found 1 unencrypted resources (Last Check: 2025-12-27)<!--end--> | ✅ |
| 21f.2 | Encryption in transit | TLS 1.2+ required | [SECURITY.md](../SECURITY.md) | ✅ |
| 21f.3 | Key management | Rotation, separation, offline storage | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |
| 21f.4 | Algorithm selection | NIST-approved (AES, RSA, SHA-256) | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |
| 21f.5 | PII protection | Fernet encryption in logs | `django-nis2-shield` | ✅ |

---

## Article 21(g) - Human Resources Security

> "Human resources security, access control policies and asset management"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21g.1 | Access control | RBAC (Kubernetes), DB user separation | Helm chart, compose | ✅ |
| 21g.2 | Principle of least privilege | Minimal container capabilities | `docker-compose.yml` | ✅ |
| 21g.3 | Secrets management | External secrets, Vault ready | Values.yaml annotations | ✅ |
| 21g.4 | Audit logging | All access logged | `django-nis2-shield` | ✅ |

---

## Article 21(h) - Multi-Factor Authentication

> "The use of multi-factor authentication or continuous authentication solutions"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 21h.1 | MFA support | MFAEnforcer middleware | `django-nis2-shield` | ✅ |
| 21h.2 | Session security | SessionGuard, fingerprinting | `react-guard` | ✅ |
| 21h.3 | Device validation | Device fingerprint in telemetry | `react-guard` | ✅ |

---

## Article 23 - Reporting Obligations

> "Reporting obligations"

| # | Requirement | Implementation | Evidence | Status |
|---|-------------|----------------|----------|--------|
| 23.1 | Early warning (24h) | Incident logging with timestamp | Audit logs | ✅ |
| 23.2 | Structured reports | JSON/CEF format | `django-nis2-shield` | ✅ |
| 23.3 | CSIRT integration | SIEM forwarding | `monitoring/fluent-bit.conf` | ✅ |
| 23.4 | Evidence preservation | Immutable logs, HMAC signed | [CRYPTOGRAPHY.md](CRYPTOGRAPHY.md) | ✅ |

---

## Summary

| Article | Requirements | Compliant | Partial | Gaps |
|---------|--------------|-----------|---------|------|
| 21(a) Risk Analysis | 5 | 5 | 0 | 0 |
| 21(b) Incident Handling | 5 | 5 | 0 | 0 |
| 21(c) Business Continuity | 7 | 7 | 0 | 0 |
| 21(d) Supply Chain | 5 | 4 | 1 | 0 |
| 21(e) Vulnerability Handling | 4 | 3 | 1 | 0 |
| 21(f) Cryptography | 5 | 5 | 0 | 0 |
| 21(g) Access Control | 4 | 4 | 0 | 0 |
| 21(h) MFA | 3 | 3 | 0 | 0 |
| 23 Reporting | 4 | 4 | 0 | 0 |
| **TOTAL** | **42** | **40** | **2** | **0** |

### Compliance Score: **95%**

---

## Remediation Plan

### 21d.4 - SBOM Generation

**Gap**: Software Bill of Materials not automatically generated.

**Remediation**:
```yaml
# Add to CI workflow
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE }}
    artifact-name: sbom.spdx.json
```

### 21e.4 - Patch Management

**Gap**: No automated monthly update schedule.

**Remediation**: Document and implement monthly base image update procedure.

---

## Certification Statement

This self-assessment was conducted by:

- **Organization**: _______________________
- **Assessor**: _______________________
- **Date**: _______________________
- **Next Review**: _______________________

Signature: _______________________

---

*Template version: 1.0*
*Last updated: 2025-12-27*
