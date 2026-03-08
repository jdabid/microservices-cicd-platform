# ADR-003: Prometheus + Grafana Monitoring Stack

## Status
Accepted

## Date
2026-03-10

## Context
Running microservices in production without observability is operating blind. The platform needs:

- **Metrics collection**: CPU, memory, request latency, error rates, queue depths for all services.
- **Visualization**: Dashboards for real-time and historical analysis of system health.
- **Alerting**: Automated notifications when services degrade or thresholds are breached.
- **Logging**: Structured, searchable logs with correlation IDs to trace requests across services.

The monitoring solution must:
- Run inside the same Kubernetes cluster to minimize latency and network costs.
- Be open-source to avoid vendor lock-in and licensing costs.
- Support the existing stack (FastAPI, PostgreSQL, Redis, Celery).
- Scale with the number of services and metrics without significant cost increases.

## Decision
Adopt a monitoring stack composed of Prometheus, Grafana, and Alertmanager, combined with structured JSON logging and correlation IDs at the application level.

### Components

| Component    | Role                              | Deployment          |
|-------------|-----------------------------------|---------------------|
| Prometheus  | Metrics scraping and storage      | Kubernetes StatefulSet |
| Grafana     | Dashboards and visualization      | Kubernetes Deployment  |
| Alertmanager| Alert routing and notification    | Kubernetes Deployment  |
| FastAPI app | Structured JSON logs + /metrics   | Application pods       |

### Metrics Pipeline

```
FastAPI (/metrics) ──► Prometheus (scrape) ──► Grafana (query + display)
                                            ──► Alertmanager (rules + notify)
```

### Application-Level Observability
- **Structured logging**: All application logs are emitted as JSON with fields: `timestamp`, `level`, `message`, `correlation_id`, `service`, `endpoint`.
- **Correlation IDs**: A middleware generates a unique ID per request and propagates it through all log entries and downstream calls, enabling end-to-end request tracing.
- **Prometheus client**: The FastAPI application exposes a `/metrics` endpoint using `prometheus-client` with custom metrics: request count, request duration histogram, active connections, and Celery task metrics.

### Grafana Dashboards
- **API Overview**: Request rate, error rate (4xx/5xx), p50/p95/p99 latency.
- **Infrastructure**: Pod CPU/memory, node utilization, PVC usage.
- **Database**: PostgreSQL connections, query duration, replication lag.
- **Cache**: Redis hit rate, memory usage, connected clients.
- **Workers**: Celery task throughput, failure rate, queue length.

### Alerting Rules
- API error rate > 5% for 5 minutes.
- P95 latency > 2 seconds for 10 minutes.
- Pod restart count > 3 in 15 minutes.
- Database connection pool exhaustion (> 80% utilized).
- Celery queue depth > 100 for 10 minutes.

## Consequences

### Positive
- **Full ownership**: No third-party SaaS dependency. All data stays within the cluster.
- **Cost predictable**: Open-source stack with no per-host or per-metric pricing. Costs are limited to compute and storage resources.
- **Rich ecosystem**: Prometheus has exporters for PostgreSQL, Redis, Kubernetes, and Celery. Grafana has thousands of community dashboards.
- **Correlation IDs**: Enable tracing a single user request across the API, database, cache, and worker layers without a full distributed tracing system.
- **Kubernetes native**: Prometheus Operator and ServiceMonitor CRDs integrate natively with Kubernetes service discovery.

### Negative
- **Operational overhead**: The team must maintain Prometheus storage, Grafana configuration, and alerting rules. No managed service handles upgrades or scaling.
- **Storage growth**: Prometheus TSDB grows with the number of metrics and retention period. Requires capacity planning and potentially remote storage (Thanos or Cortex) at scale.
- **No distributed tracing**: Correlation IDs provide basic request tracking but lack the span-level detail of a full tracing system (e.g., Jaeger, Tempo). This is acceptable at the current scale.
- **Dashboard maintenance**: Grafana dashboards must be maintained as JSON or provisioned via code. Dashboard drift can occur if edited manually.

### Risks
- **Alert fatigue**: Poorly tuned alerting rules can generate excessive notifications, leading the team to ignore alerts. Mitigation: Start with a small set of critical alerts and iterate based on incident patterns.
- **Prometheus single point of failure**: A single Prometheus instance means metrics are lost if the pod crashes before data is persisted. Mitigation: StatefulSet with persistent volume; consider Thanos for high availability in production.
- **Metric cardinality explosion**: High-cardinality labels (e.g., user IDs in metrics) can cause Prometheus memory and storage issues. Mitigation: Review metric labels in code review; enforce cardinality guidelines.

## Alternatives Considered

### ELK Stack (Elasticsearch + Logstash + Kibana)
Full-text log search and analysis platform.
- **Rejected because**: Primarily a logging solution, not a metrics platform. Elasticsearch is resource-intensive (memory and storage). Would need to be combined with Prometheus anyway for metrics, resulting in two complex systems to operate.

### Datadog
Cloud-based observability platform with metrics, logs, traces, and APM.
- **Rejected because**: Per-host pricing model becomes expensive as the cluster scales. Creates vendor lock-in. Not suitable for a portfolio project where the goal is demonstrating infrastructure skills with open-source tooling.

### AWS CloudWatch
AWS-native monitoring and logging service.
- **Rejected because**: Locked to AWS. Custom metrics incur per-metric costs. Dashboard and alerting capabilities are less flexible than Grafana. Does not demonstrate infrastructure engineering skills as effectively as self-managed tooling.

### Jaeger for Distributed Tracing
OpenTelemetry-compatible distributed tracing system.
- **Not rejected but deferred**: Jaeger adds valuable span-level tracing but introduces additional infrastructure (collector, storage, query service). Correlation IDs provide sufficient traceability at the current scale. Jaeger can be added later as the service count grows.
