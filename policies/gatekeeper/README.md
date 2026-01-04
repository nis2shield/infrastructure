# OPA Gatekeeper - NIS2 Compliance Policies
# ============================================================================

This directory contains Open Policy Agent (OPA) Gatekeeper policies to enforce
NIS2 compliance requirements at the Kubernetes admission control level.

## What is Gatekeeper?

OPA Gatekeeper is a customizable admission webhook for Kubernetes that enforces
policies executed by the Open Policy Agent. It allows you to define "what can
and cannot be deployed" in your cluster.

## NIS2 Compliance Coverage

| Policy | NIS2 Article | Description |
|--------|-------------|-------------|
| `require-non-root` | Art. 21.2(d) | Prevents containers from running as root |
| `require-resource-limits` | Art. 21.2(a) | Ensures all pods have CPU/memory limits |
| `require-security-labels` | Art. 21.2(e) | Enforces compliance tracking labels |
| `block-privileged-containers` | Art. 21.2(d) | Prevents privilege escalation |
| `require-readonly-rootfs` | Art. 21.2(d) | Enforces read-only root filesystems |

## Installation

### 1. Install Gatekeeper

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update
helm install gatekeeper/gatekeeper --name-template=gatekeeper \
  --namespace gatekeeper-system --create-namespace
```

### 2. Apply Constraint Templates

```bash
kubectl apply -f constraint-templates/
```

### 3. Apply Constraints

```bash
kubectl apply -f constraints/
```

## Directory Structure

```
gatekeeper/
├── constraint-templates/     # ConstraintTemplate CRDs (define the policy logic)
│   ├── k8srequiredlabels.yaml
│   ├── k8snonrootcontainer.yaml
│   ├── k8sresourcelimits.yaml
│   └── k8sprivilegedcontainer.yaml
├── constraints/              # Constraint CRDs (apply policies to namespaces)
│   ├── require-nis2-labels.yaml
│   ├── require-nonroot.yaml
│   ├── require-limits.yaml
│   └── block-privileged.yaml
└── README.md
```

## Testing Policies

Test that policies are working:

```bash
# This should be DENIED (no resource limits)
kubectl run test-denied --image=nginx --restart=Never

# This should be ALLOWED (with proper config)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-allowed
  labels:
    nis2-compliance: "true"
    data-classification: "internal"
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
    - name: nginx
      image: nginx
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
      resources:
        limits:
          memory: "128Mi"
          cpu: "500m"
        requests:
          memory: "64Mi"
          cpu: "250m"
EOF
```

## Enforcement Modes

Gatekeeper supports multiple enforcement modes:

- **deny**: Block non-compliant resources (Production)
- **dryrun**: Log violations without blocking (Testing)
- **warn**: Allow but show warning (Gradual rollout)

Adjust the `enforcementAction` in each constraint YAML to change modes.
