#!/usr/bin/env bash
# Smoke test script for verifying deployments in kind cluster
# Usage: ./scripts/smoke-test.sh [namespace] [timeout]
# Exit codes: 0 = success, 1 = failure

set -euo pipefail

NAMESPACE="${1:-microservices-cicd-platform}"
TIMEOUT="${2:-120}"
BACKEND_PORT="${3:-8000}"
FRONTEND_PORT="${4:-80}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

check_pass() { log_info "PASS: $1"; PASSED=$((PASSED + 1)); }
check_fail() { log_error "FAIL: $1"; FAILED=$((FAILED + 1)); }

# Wait for all pods to be ready with timeout
wait_for_pods() {
    log_info "Waiting for pods in namespace '$NAMESPACE' to be ready (timeout: ${TIMEOUT}s)..."
    local elapsed=0
    local interval=5

    while [ $elapsed -lt "$TIMEOUT" ]; do
        local not_ready
        not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v -E "Running|Completed" | wc -l | tr -d ' ')

        if [ "$not_ready" -eq 0 ]; then
            local total
            total=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l | tr -d ' ')
            if [ "$total" -gt 0 ]; then
                log_info "All $total pods are Running/Completed."
                return 0
            fi
        fi

        log_warn "Waiting... ($elapsed/${TIMEOUT}s) - $not_ready pod(s) not ready"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    log_error "Timeout waiting for pods to be ready"
    kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null || true
    return 1
}

# Test 1: Check all pods are Running
test_pods_running() {
    log_info "Test 1: Checking all pods are in Running state..."
    local failed_pods
    failed_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v -E "Running|Completed" || true)

    if [ -z "$failed_pods" ]; then
        check_pass "All pods are Running"
    else
        check_fail "Some pods are not Running:"
        echo "$failed_pods"
    fi
}

# Test 2: Check backend-api health endpoint
test_backend_health() {
    log_info "Test 2: Checking backend-api /health endpoint..."

    # Port-forward in background
    kubectl port-forward -n "$NAMESPACE" svc/backend-api "$BACKEND_PORT:$BACKEND_PORT" &
    local pf_pid=$!
    sleep 3

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${BACKEND_PORT}/health" 2>/dev/null || echo "000")

    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    if [ "$status_code" = "200" ]; then
        check_pass "Backend /health returned 200"
    else
        check_fail "Backend /health returned $status_code (expected 200)"
    fi
}

# Test 3: Check backend-api readiness endpoint
test_backend_ready() {
    log_info "Test 3: Checking backend-api /ready endpoint..."

    kubectl port-forward -n "$NAMESPACE" svc/backend-api "$BACKEND_PORT:$BACKEND_PORT" &
    local pf_pid=$!
    sleep 3

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${BACKEND_PORT}/ready" 2>/dev/null || echo "000")

    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    if [ "$status_code" = "200" ]; then
        check_pass "Backend /ready returned 200"
    else
        # Readiness may fail if DB/Redis not fully connected - warn but still check
        check_fail "Backend /ready returned $status_code (expected 200)"
    fi
}

# Test 4: Check backend-api serves API responses
test_backend_api() {
    log_info "Test 4: Checking backend-api /api/v1/ responds..."

    kubectl port-forward -n "$NAMESPACE" svc/backend-api "$BACKEND_PORT:$BACKEND_PORT" &
    local pf_pid=$!
    sleep 3

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${BACKEND_PORT}/api/v1/" 2>/dev/null || echo "000")

    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    # Accept 200, 404 (route exists but no handler), or 307 (redirect)
    if [[ "$status_code" =~ ^(200|307|404|422)$ ]]; then
        check_pass "Backend API responded with $status_code"
    else
        check_fail "Backend API returned $status_code (expected 2xx/3xx/4xx)"
    fi
}

# Test 5: Check frontend serves HTML
test_frontend() {
    log_info "Test 5: Checking frontend serves HTML..."

    kubectl port-forward -n "$NAMESPACE" svc/frontend "$FRONTEND_PORT:$FRONTEND_PORT" &
    local pf_pid=$!
    sleep 3

    local response
    response=$(curl -s "http://localhost:${FRONTEND_PORT}/" 2>/dev/null || echo "")

    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    if echo "$response" | grep -qi "html"; then
        check_pass "Frontend serves HTML content"
    else
        check_fail "Frontend did not return HTML content"
    fi
}

# Test 6: Check Kubernetes services exist
test_services_exist() {
    log_info "Test 6: Checking required services exist..."
    local services=("backend-api" "postgres" "redis" "frontend")
    local all_found=true

    for svc in "${services[@]}"; do
        if kubectl get svc "$svc" -n "$NAMESPACE" &>/dev/null; then
            log_info "  Service '$svc' exists"
        else
            log_warn "  Service '$svc' not found"
            all_found=false
        fi
    done

    if [ "$all_found" = true ]; then
        check_pass "All required services exist"
    else
        check_fail "Some required services are missing"
    fi
}

# Main execution
echo "============================================"
echo "  Smoke Tests - Microservices Platform"
echo "  Namespace: $NAMESPACE"
echo "  Timeout: ${TIMEOUT}s"
echo "============================================"
echo ""

# Wait for pods first
if ! wait_for_pods; then
    log_error "Pods did not become ready within timeout"
    echo ""
    echo "Pod status:"
    kubectl get pods -n "$NAMESPACE" 2>/dev/null || true
    echo ""
    echo "Events:"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' 2>/dev/null | tail -20 || true
    exit 1
fi

echo ""

# Run all tests
test_pods_running
test_services_exist
test_backend_health
test_backend_ready
test_backend_api
test_frontend

# Summary
echo ""
echo "============================================"
echo "  Results: $PASSED passed, $FAILED failed"
echo "============================================"

if [ $FAILED -gt 0 ]; then
    log_error "Smoke tests FAILED"
    exit 1
else
    log_info "All smoke tests PASSED"
    exit 0
fi
