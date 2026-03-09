#!/usr/bin/env bash
# Rollback script for Helm deployments
# Usage: ./scripts/rollback.sh [release-name] [namespace] [revision]
# Exit codes: 0 = success, 1 = failure

set -euo pipefail

RELEASE_NAME="${1:-microservices-platform}"
NAMESPACE="${2:-microservices-cicd-platform}"
REVISION="${3:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "============================================"
echo "  Helm Rollback"
echo "  Release: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo "============================================"
echo ""

# Check current release status
log_info "Current release status:"
helm status "$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || {
    log_error "Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
    exit 1
}

echo ""

# Show release history
log_info "Release history:"
helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 5 2>/dev/null || true

echo ""

# Perform rollback
if [ -n "$REVISION" ]; then
    log_info "Rolling back to revision $REVISION..."
    helm rollback "$RELEASE_NAME" "$REVISION" -n "$NAMESPACE" --wait --timeout 120s
else
    log_info "Rolling back to previous revision..."
    helm rollback "$RELEASE_NAME" -n "$NAMESPACE" --wait --timeout 120s
fi

echo ""

# Verify rollback
log_info "Verifying rollback..."
ROLLBACK_STATUS=$(helm status "$RELEASE_NAME" -n "$NAMESPACE" -o json 2>/dev/null | grep -o '"status":"[^"]*"' | head -1 || echo "unknown")

log_info "Post-rollback status: $ROLLBACK_STATUS"

# Check pods after rollback
log_info "Pod status after rollback:"
kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null || true

echo ""

# Wait for rollout
log_info "Waiting for deployments to stabilize..."
DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" --no-headers -o custom-columns=":metadata.name" 2>/dev/null || true)

ROLLBACK_SUCCESS=true
for deploy in $DEPLOYMENTS; do
    log_info "  Checking deployment: $deploy"
    if kubectl rollout status deployment/"$deploy" -n "$NAMESPACE" --timeout=60s 2>/dev/null; then
        log_info "  Deployment '$deploy' is stable"
    else
        log_error "  Deployment '$deploy' failed to stabilize"
        ROLLBACK_SUCCESS=false
    fi
done

echo ""

if [ "$ROLLBACK_SUCCESS" = true ]; then
    log_info "Rollback completed successfully"
    echo ""
    log_info "Updated release history:"
    helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 5 2>/dev/null || true
    exit 0
else
    log_error "Rollback completed but some deployments are not stable"
    exit 1
fi
