# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-04

### Added
- **Crypto-Replicator**: Zero-trust cloud backup with AES-256-GCM + RSA-OAEP encryption
- **Helm Chart** (v1.0.0): Production-ready Kubernetes deployment with NetworkPolicies
- **Terraform Modules**: Multi-cloud support (AWS, Azure, GCP) with security best practices
- **VPC Flow Logs** (AWS): Network monitoring for NIS2 Art. 21.2.f compliance
- **S3 Access Logging** (AWS): Audit trail for backup bucket access
- **NIS2 Compliance Audit** workflow: Automated tfsec + gitleaks + Trivy scans

### Changed
- Restricted RDS security group egress to VPC CIDR (was 0.0.0.0/0)
- Updated SECURITY.md to v1.0.x

### Security
- All Terraform modules pass tfsec HIGH/CRITICAL checks
- Zero secrets in git history (gitleaks verified)
- Supply chain scanning with Trivy


## [0.1.0] - 2025-12-26

### Added
- Initial release of NIS2 Infrastructure Kit
- `docker-compose.yml` with 4 services:
  - `webapp` - Hardened Django container (non-root, read-only FS)
  - `log-collector` - Fluent Bit sidecar for SIEM integration
  - `db-backup` - Automated PostgreSQL backups
  - `db` - PostgreSQL database
- `docker-compose.prod.yml` - Production overrides with:
  - Docker secrets support
  - Health checks
  - Resource limits
  - Network isolation
- `monitoring/fluent-bit.conf` - Log collector configuration
- `monitoring/parsers.conf` - JSON/CEF parsers
- `examples/Dockerfile` - Sample multi-stage Django build
- `examples/requirements.txt` - Python dependencies template
- Full documentation (README, SECURITY, CONTRIBUTING, etc.)

### Security
- Non-root container execution
- Read-only filesystem with tmpfs for /tmp
- Log segregation via shared volumes
- Network isolation in production mode
