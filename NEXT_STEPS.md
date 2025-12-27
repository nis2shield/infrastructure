# 🚀 Next Steps - NIS2 Infrastructure Kit

Roadmap for the infrastructure component of the NIS2 Shield ecosystem.

---

## ✅ Completed (v0.1.0)

- [x] Core docker-compose.yml with 4 services
- [x] Fluent Bit log collector with SIEM support
- [x] Automated PostgreSQL backups
- [x] Non-root, read-only container hardening
- [x] Production overrides (docker-compose.prod.yml)
- [x] CI/CD pipeline for validation

---

## ✅ Completed (v0.2.0) - Observability & Testing

- [x] `scripts/restore-test.sh` - Disaster recovery testing (GPG support)
- [x] ELK Stack (`docker-compose.elk.yml`) - Elasticsearch + Kibana
- [x] Prometheus + Grafana monitoring with NIS2 dashboard
- [x] End-to-end tutorial at nis2shield.com/getting-started/

---

## ✅ Completed (v0.2.5) - Encrypted Twin

- [x] **Crypto-Replicator** - Python service for encrypted cloud backup
- [x] PostgreSQL LISTEN/NOTIFY CDC integration
- [x] Hybrid encryption (AES-256-GCM + RSA-OAEP)
- [x] Key rotation support (`KeyRotationManager`)
- [x] OpenAPI 3.0 spec and API documentation
- [x] CI workflow (unit + docker + integration tests)
- [x] Website compliance matrix (Art. 21c, 21f, 21g)

---

## 📈 v0.3.0 - Enterprise Deployment (Helm Chart)

> **Focus**: Un Helm Chart "production-grade" per deployment enterprise.
> Ospedali, comuni, aziende usano Kubernetes (OpenShift, EKS, RKE2).
> `helm install nis2shield ./chart` deve essere l'esperienza utente target.

### Phase 1: Helm Chart Core
- [ ] `charts/nis2shield/` - Chart structure
- [ ] Unified deployment: webapp + replicator + log-collector
- [ ] `values.yaml` with toggles:
  - `replicator.enabled: true/false`
  - `monitoring.enabled: true/false`  
  - `elk.enabled: true/false`
- [ ] ConfigMaps for Fluent Bit, Prometheus configs
- [ ] Secrets management (native + Vault annotations)

### Phase 2: Kubernetes Hardening
- [ ] SecurityContext (runAsNonRoot, readOnlyRootFilesystem)
- [ ] PodSecurityStandards (Restricted profile)
- [ ] NetworkPolicies for service isolation
- [ ] ResourceQuotas and LimitRanges

### Phase 3: Production Features
- [ ] Health checks (liveness, readiness, startup probes)
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] PodDisruptionBudget for HA
- [ ] Ingress template (nginx/traefik)

### Phase 4: Documentation
- [ ] Enterprise Deployment Guide (K3s/Minikube demo)
- [ ] Upgrade guide (rolling updates)
- [ ] Troubleshooting guide

---

## 📚 v0.4.0 - Infrastructure as Code

> **Priority**: Media - per chi sceglie Scenario A (Pure Cloud)

### Terraform Modules
- [ ] `terraform/aws/` - VPC, RDS, S3, EKS
- [ ] `terraform/gcp/` - VPC, Cloud SQL, GKE
- [ ] `terraform/azure/` - VNet, PostgreSQL, AKS
- [ ] State management (S3/GCS backend)

### GitOps (Optional)
- [ ] ArgoCD Application manifest
- [ ] Flux CD example
- [ ] GitHub Actions CD workflow

---

## 🏆 v1.0.0 - Production Certified

- [ ] Security audit documentation
- [ ] CIS benchmark compliance
- [ ] Performance benchmarks
- [ ] Video walkthrough
- [ ] Official NIS2 compliance certification guide

---

## 🔗 Related Projects

| Project | Version | Status |
|---------|---------|--------|
| [django-nis2-shield](https://github.com/nis2shield/django-nis2-shield) | v0.3.0 | ✅ |
| [@nis2shield/react-guard](https://github.com/nis2shield/react-guard) | v0.2.0 | ✅ |
| [infrastructure](https://github.com/nis2shield/infrastructure) | v0.2.5 | ✅ |
| [nis2shield.com](https://nis2shield.com) | - | Live ✅ |
