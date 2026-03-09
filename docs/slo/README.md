# Service Level Objectives (SLO)

## Overview

This document defines the SLOs for the Medical Appointments microservices platform.
SLOs are based on Google SRE best practices with multi-window, multi-burn-rate alerting.

## SLO Definitions

| SLO | SLI | Target | Window |
|-----|-----|--------|--------|
| Availability | Percentage of non-5xx requests | 99.9% | 30 days |
| Latency | Percentage of requests completing under 500ms | 95% | 30 days |

## SLI Calculation Formulas

### Availability SLI

```promql
1 - (
  sum(rate(http_requests_total{status_code=~"5.."}[window]))
  / sum(rate(http_requests_total[window]))
)
```

- **Numerator**: Total successful requests (non-5xx)
- **Denominator**: Total requests
- A value of 99.9% means at most 1 in 1000 requests returns a server error

### Latency SLI

```promql
sum(rate(http_request_duration_seconds_bucket{le="0.5"}[window]))
/ sum(rate(http_request_duration_seconds_count[window]))
```

- **Numerator**: Requests completing in under 500ms (using histogram bucket)
- **Denominator**: Total requests
- A value of 95% means at most 5 in 100 requests take longer than 500ms

## Error Budget

### What is an Error Budget?

The error budget is the inverse of the SLO target. For 99.9% availability:

- **Error budget** = 100% - 99.9% = 0.1%
- Over a 30-day window, this allows approximately **43.2 minutes** of total downtime
- Or equivalently, 1 in every 1000 requests can fail

### Error Budget Remaining

```promql
1 - (
  sum(increase(http_requests_total{status_code=~"5.."}[30d]))
  / (sum(increase(http_requests_total[30d])) * 0.001)
)
```

When the error budget reaches 0%, the SLO has been violated for the current window.

### Error Budget Policy

| Budget Remaining | Action |
|-----------------|--------|
| > 75% | Normal operations. Teams can deploy freely. |
| 50% - 75% | Caution. Reduce risky deployments. |
| 25% - 50% | Warning. Only critical fixes deployed. Investigate error sources. |
| < 25% | Critical. Freeze all non-essential changes. Full incident response. |
| 0% (exhausted) | SLO violated. Post-mortem required. No deploys until budget recovers. |

## Burn Rate Alerts

Burn rate measures how quickly the error budget is being consumed relative to the 30-day window.
A burn rate of 1x means the budget will be exactly exhausted at the end of the window.

### Multi-Window Burn Rate Strategy (Google SRE)

| Alert | Window | Burn Rate Threshold | Budget Consumed | Time to Exhaustion | Severity |
|-------|--------|--------------------:|----------------:|-------------------:|----------|
| SLOHighBurnRate1h | 1 hour | 14.4x | 2% in 1h | ~2 days | Critical |
| SLOHighBurnRate6h | 6 hours | 6x | 5% in 6h | ~5 days | Warning |

### Why Multi-Window?

- **Short window (1h)**: Catches sudden spikes in errors that would rapidly exhaust the budget
- **Long window (6h)**: Catches sustained elevated error rates that are less obvious but still dangerous
- Both must fire before paging to reduce false positives

### Latency Budget Alert

| Alert | Condition | Severity |
|-------|-----------|----------|
| SLOLatencyBudgetBurn | < 95% of requests under 500ms (1h window) | Warning |

## Alert Escalation

1. **Warning alerts** (6h burn rate, latency): Notify team via Slack/email
2. **Critical alerts** (1h burn rate): Page on-call engineer immediately
3. **If budget < 25%**: Escalate to team lead, freeze deployments
4. **If budget exhausted**: Trigger incident response process

## Grafana Dashboard

The SLO dashboard (`monitoring/grafana/dashboards/slo-dashboard.json`) provides:

- **Row 1 - SLO Overview**: Current availability SLI, latency SLI, error budget gauge, budget status
- **Row 2 - SLI Trends**: Time series for availability, latency percentiles, and error rate
- **Row 3 - Error Budget**: Burn rate chart, budget consumption by window, time until exhaustion
- **Row 4 - SLO Compliance**: Summary table with pass/fail status, request volume for context

## References

- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook - Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Prometheus - Recording Rules for SLOs](https://prometheus.io/docs/practices/rules/)
