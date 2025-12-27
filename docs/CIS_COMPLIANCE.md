# CIS Benchmark Compliance

Self-assessment of NIS2 Shield Infrastructure against CIS security benchmarks.

---

## CIS Docker Benchmark v1.6.0

### Section 1: Host Configuration

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 1.1.1 | Ensure a separate partition for containers | ℹ️ Host | Host responsibility |
| 1.1.2 | Ensure only trusted users control Docker | ℹ️ Host | Host responsibility |
| 1.2.1 | Ensure Docker is up to date | ✅ Pass | Image uses latest stable |

### Section 2: Docker Daemon Configuration

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 2.1 | Run Docker in rootless mode | ⚠️ Partial | Containers run non-root |
| 2.2 | Ensure network traffic is restricted | ✅ Pass | Isolated Docker networks |
| 2.3 | Ensure logging level is set to info | ✅ Pass | Fluent Bit collects all logs |
| 2.4 | Ensure Docker is allowed to make changes to iptables | ✅ Pass | Default allowed |
| 2.5 | Ensure insecure registries are not used | ✅ Pass | No insecure registries configured |
| 2.6 | Ensure aufs storage driver is not used | ✅ Pass | Using overlay2 |
| 2.7 | Ensure TLS authentication is configured | ✅ Pass | TLS for remote connections |
| 2.8 | Ensure default ulimit is configured | ✅ Pass | Default ulimits appropriate |

### Section 4: Container Images and Build File

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 4.1 | Ensure that a user for the container has been created | ✅ Pass | `user: 1000:1000` in compose |
| 4.2 | Ensure that containers use only trusted base images | ✅ Pass | Official images (python:slim, postgres:alpine) |
| 4.3 | Ensure that unnecessary packages are not installed | ✅ Pass | Multi-stage builds, minimal images |
| 4.4 | Ensure images are scanned and rebuilt | ⚠️ Manual | Recommend adding Trivy to CI |
| 4.5 | Ensure Content trust is enabled | ⚠️ Optional | Not enforced by default |
| 4.6 | Ensure HEALTHCHECK is added | ✅ Pass | All services have health checks |
| 4.7 | Ensure update instructions are not used alone | ✅ Pass | Multi-stage builds |
| 4.8 | Ensure setuid and setgid permissions are removed | ✅ Pass | `cap_drop: ALL` |
| 4.9 | Ensure COPY is used instead of ADD | ✅ Pass | All Dockerfiles use COPY |
| 4.10 | Ensure secrets are not stored in Dockerfiles | ✅ Pass | Secrets via env vars |
| 4.11 | Ensure verified packages are installed | ✅ Pass | APT/pip with hash verification |

### Section 5: Container Runtime

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 5.1 | Ensure AppArmor Profile is set | ⚠️ Host | Host dependent |
| 5.2 | Ensure SELinux security options are set | ⚠️ Host | Host dependent |
| 5.3 | Ensure Linux kernel capabilities are restricted | ✅ Pass | `cap_drop: ALL` |
| 5.4 | Ensure privileged containers are not used | ✅ Pass | No privileged containers |
| 5.5 | Ensure sensitive host system directories are not mounted | ✅ Pass | Only app volumes mounted |
| 5.6 | Ensure SSH is not running within containers | ✅ Pass | No SSH in any container |
| 5.7 | Ensure privileged ports are not mapped | ✅ Pass | Only 8000 exposed |
| 5.8 | Ensure only needed ports are open | ✅ Pass | Minimal port exposure |
| 5.9 | Ensure host's network namespace is not shared | ✅ Pass | Isolated networks |
| 5.10 | Ensure memory usage is limited | ⚠️ Optional | Add `mem_limit` for production |
| 5.11 | Ensure CPU priority is set appropriately | ⚠️ Optional | Add `cpu_quota` for production |
| 5.12 | Ensure container's root filesystem is read-only | ✅ Pass | `read_only: true` |
| 5.13 | Ensure incoming container traffic is bound to specific interface | ✅ Pass | Bound to 127.0.0.1 in prod |
| 5.14 | Ensure 'on-failure' restart policy is set | ✅ Pass | `restart: unless-stopped` |
| 5.15 | Ensure host's process namespace is not shared | ✅ Pass | Default isolation |
| 5.16 | Ensure host's IPC namespace is not shared | ✅ Pass | Default isolation |
| 5.17 | Ensure host devices are not directly exposed | ✅ Pass | No device mounts |
| 5.18 | Ensure default ulimit is overwritten at runtime if needed | ✅ Pass | Appropriate defaults |
| 5.19 | Ensure mount propagation is not shared | ✅ Pass | Default settings |
| 5.20 | Ensure host's UTS namespace is not shared | ✅ Pass | Default isolation |
| 5.21 | Ensure default seccomp profile is not disabled | ✅ Pass | Using RuntimeDefault |
| 5.22 | Ensure docker exec with privileged option is not used | ✅ Pass | Documented best practice |
| 5.23 | Ensure docker exec with user option is used | ✅ Pass | Default non-root user |
| 5.24 | Ensure cgroup usage is confirmed | ✅ Pass | Default cgroup settings |
| 5.25 | Ensure container is restricted from acquiring additional privileges | ✅ Pass | `no-new-privileges:true` |
| 5.26 | Ensure container health is checked at runtime | ✅ Pass | Health checks in compose |
| 5.27 | Ensure PIDs cgroup limit is used | ⚠️ Optional | Add `pids_limit` for production |
| 5.28 | Ensure Docker's default bridge is not used | ✅ Pass | Custom networks defined |

### Section 6: Docker Security Operations

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 6.1 | Ensure image vulnerability scanning is done | ⚠️ Manual | Recommend Trivy in CI |
| 6.2 | Ensure containers' sprawl is avoided | ✅ Pass | Compose manages lifecycle |

---

## CIS Kubernetes Benchmark v1.8.0

*Applicable when using Helm chart deployment*

### Section 4: Worker Node Security Configuration

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 4.2.1 | Ensure kubelet anonymous auth is disabled | ℹ️ Cluster | Cluster admin responsibility |
| 4.2.2 | Ensure kubelet authn/authz | ℹ️ Cluster | Cluster admin responsibility |

### Section 5: Policies

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 5.1.1 | Ensure cluster-admin role is only used where required | ✅ Pass | ServiceAccount per release |
| 5.1.2 | Minimize access to secrets | ✅ Pass | RBAC limits secret access |
| 5.1.3 | Minimize wildcard use in Roles | ✅ Pass | No wildcards in chart |
| 5.1.4 | Minimize access to create pods | ✅ Pass | Deployment only |
| 5.1.5 | Ensure default service account is not used | ✅ Pass | Custom ServiceAccount |
| 5.1.6 | Ensure service account tokens are not auto-mounted | ✅ Pass | `automountServiceAccountToken: false` |
| 5.2.1 | Minimize privileged containers | ✅ Pass | No privileged pods |
| 5.2.2 | Minimize hostPID and hostIPC | ✅ Pass | Not used |
| 5.2.3 | Minimize hostNetwork and hostPorts | ✅ Pass | Not used |
| 5.2.4 | Minimize allowPrivilegeEscalation | ✅ Pass | `allowPrivilegeEscalation: false` |
| 5.2.5 | Minimize root containers | ✅ Pass | `runAsNonRoot: true` |
| 5.2.6 | Minimize NET_RAW capability | ✅ Pass | `capabilities: drop: ALL` |
| 5.2.7 | Minimize added capabilities | ✅ Pass | No capabilities added |
| 5.2.8 | Ensure read-only root filesystem | ✅ Pass | `readOnlyRootFilesystem: true` |
| 5.2.9 | Minimize the hostPath volumes | ✅ Pass | No hostPath volumes |
| 5.3.1 | Ensure NetworkPolicies are defined | ✅ Pass | NetworkPolicies in chart |
| 5.3.2 | Ensure default deny ingress policy | ✅ Pass | Default deny included |
| 5.4.1 | Use Secrets instead of environment variables | ✅ Pass | Secrets for credentials |
| 5.4.2 | Consider external secret storage | ✅ Pass | Vault annotations ready |
| 5.5.1 | Use ImagePolicyWebhook admission controller | ℹ️ Cluster | Cluster admin responsibility |

### Section 6: Security Context

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 6.1 | Ensure seccomp profile is set | ✅ Pass | `seccompProfile: RuntimeDefault` |
| 6.2 | Ensure AppArmor profile is set | ⚠️ Optional | Not set by default |

---

## Summary

### Docker Benchmark

| Category | Pass | Partial | N/A |
|----------|------|---------|-----|
| Host Configuration | - | - | 2 |
| Daemon Configuration | 7 | 1 | - |
| Container Images | 8 | 2 | - |
| Container Runtime | 22 | 4 | - |
| Security Operations | 1 | 1 | - |
| **Total** | **38** | **8** | **2** |

### Kubernetes Benchmark

| Category | Pass | Partial | N/A |
|----------|------|---------|-----|
| Policies | 17 | 1 | - |
| Security Context | 1 | 1 | - |
| **Total** | **18** | **2** | **0** |

---

## Remediation Notes

### Recommended Additions for Production

1. **Container Image Scanning**
   ```yaml
   # Add to CI pipeline
   - name: Trivy Scan
     run: trivy image --exit-code 1 --severity HIGH,CRITICAL your-image
   ```

2. **Resource Limits**
   ```yaml
   # Add to docker-compose.prod.yml
   services:
     webapp:
       mem_limit: 512m
       cpu_quota: 50000
       pids_limit: 100
   ```

3. **AppArmor Profile** (Kubernetes)
   ```yaml
   annotations:
     container.apparmor.security.beta.kubernetes.io/webapp: runtime/default
   ```

---

*Assessment date: 2025-12-27*
*Assessor: NIS2Shield Team*
