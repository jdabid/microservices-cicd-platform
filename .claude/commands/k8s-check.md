Validate all Kubernetes manifests in kubernetes/ directory.

Check: namespace, labels, resource limits, liveness/readiness probes, securityContext, NetworkPolicies, PDB, RBAC, TLS in ingress, no real secrets.

Run kubectl dry-run if available. Present results as: | Resource | Check | Status | Fix Needed |
