# Architecture Overview

This document describes the architecture of the Medical Appointments Microservices Platform, a portfolio project demonstrating DevOps engineering and Python backend development skills.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Application Architecture](#application-architecture)
3. [Infrastructure Architecture](#infrastructure-architecture)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Monitoring Architecture](#monitoring-architecture)
6. [Security Architecture](#security-architecture)
7. [Data Flow](#data-flow)
8. [Technology Decisions](#technology-decisions)

---

## System Architecture

The platform runs on AWS using Kubernetes (EKS) for container orchestration, with GitHub Actions for CI and ArgoCD for GitOps-based continuous delivery.

```
                          +--------------------+
                          |   GitHub Actions    |
                          |   CI/CD Pipeline    |
                          +---------+----------+
                                    |
                          +---------v----------+
                          |      ArgoCD         |
                          |   (GitOps Sync)     |
                          +---------+----------+
                                    |
                 +------------------v-------------------+
                 |        Kubernetes (EKS)               |
                 |                                       |
  +--------+    |  +----------+    +-----------+        |
  | Users  |------>| Frontend |    | Backend   |        |
  |        |    |  | (React   |--->|   API     |        |
  +--------+    |  |  + Nginx)|   | (FastAPI) |        |
                |  +----------+    +-----+-----+        |
                |                   |    |    |         |
                |              +----+    |    +----+    |
                |              v         v         v    |
                |        +--------+ +-------+ +------+ |
                |        |Postgres| | Redis | |Worker| |
                |        | (RDS)  | | (EC)  | |(Cely)| |
                |        +--------+ +-------+ +------+ |
                |                                       |
                |  +----------------------------------+ |
                |  | Prometheus + Grafana + Alertmgr  | |
                |  |          (Monitoring)             | |
                |  +----------------------------------+ |
                +---------------------------------------+
                                    |
                 +------------------v-------------------+
                 |         Terraform (IaC)               |
                 |    VPC  |  EKS  |  RDS  |  ElastiCache|
                 +---------------------------------------+
```

### Component Summary

| Component       | Technology              | Purpose                              |
|----------------|-------------------------|--------------------------------------|
| Frontend       | React 18 + Vite + Nginx | User interface for appointments       |
| Backend API    | FastAPI + Python 3.12   | REST API with CQRS pattern            |
| Database       | PostgreSQL (RDS)        | Persistent data storage               |
| Cache/Broker   | Redis (ElastiCache)     | Caching, sessions, Celery broker      |
| Worker         | Celery                  | Background task processing            |
| Orchestration  | Kubernetes (EKS)        | Container scheduling and management   |
| CI/CD          | GitHub Actions + ArgoCD | Automated build, test, deploy         |
| IaC            | Terraform               | Cloud infrastructure provisioning     |
| Monitoring     | Prometheus + Grafana    | Metrics, dashboards, alerting         |

---

## Application Architecture

The backend follows **Vertical Slice Architecture** combined with **CQRS** (Command Query Responsibility Segregation). Each feature is a self-contained module with its own models, schemas, commands (writes), and queries (reads).

```
backend-api/app/
|
+-- features/                    <-- Vertical Slices
|   |
|   +-- appointments/            <-- Feature: Medical Appointments
|   |   +-- commands/            <-- CQRS Write: create, update, cancel
|   |   +-- queries/             <-- CQRS Read: list, get_by_id, filter
|   |   +-- models/              <-- SQLAlchemy ORM models
|   |   +-- schemas/             <-- Pydantic v2 request/response schemas
|   |   +-- router.py            <-- FastAPI router
|   |
|   +-- patients/                <-- Feature: Patient Management
|   |   +-- commands/
|   |   +-- queries/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- router.py
|   |
|   +-- auth/                    <-- Feature: Authentication
|       +-- commands/
|       +-- queries/
|       +-- models/
|       +-- schemas/
|       +-- router.py
|
+-- core/                        <-- Cross-Cutting Concerns
|   +-- config.py                <-- Settings (Pydantic BaseSettings)
|   +-- security.py              <-- JWT token handling
|   +-- logging.py               <-- Structured JSON logging
|   +-- middleware.py            <-- Correlation ID, request timing
|   +-- celery/                  <-- Celery app configuration
|
+-- common/                      <-- Shared Utilities
|   +-- database/                <-- AsyncSession, engine setup
|   +-- dependencies/            <-- FastAPI dependency injection
|   +-- exceptions/              <-- Custom exception classes + handlers
|
+-- tasks/                       <-- Celery Background Tasks
    +-- notifications.py         <-- Email/SMS reminders
    +-- reports.py               <-- Report generation
```

### CQRS Flow

```
                    HTTP Request
                         |
                    +----v----+
                    | Router  |
                    +----+----+
                    |         |
             +------+      +------+
             | POST |      | GET  |
             | PUT  |      |      |
             |DELETE|      |      |
             +--+---+      +--+---+
                |              |
          +-----v-----+  +----v------+
          | Commands   |  | Queries   |
          | (writes)   |  | (reads)   |
          +-----+------+  +----+------+
                |              |
          +-----v--------------v------+
          |       Database (PostgreSQL)|
          |       Cache (Redis)        |
          +----------------------------+
```

- **Commands** handle mutations: creating appointments, updating patient records, canceling bookings. They validate input, enforce business rules, and persist changes.
- **Queries** handle reads: listing appointments, searching patients, fetching details. They are read-only and can leverage Redis caching for performance.

---

## Infrastructure Architecture

All cloud resources are provisioned with Terraform using a modular design. See [ADR-002](adr/002-terraform-modules.md) for the decision rationale.

### Terraform Module Layout

```
terraform/
+-- main.tf                      <-- Root module (composes all modules)
+-- variables.tf                 <-- Root input variables
+-- outputs.tf                   <-- Root outputs
+-- providers.tf                 <-- AWS provider config
+-- versions.tf                  <-- Version constraints
|
+-- modules/
|   +-- vpc/                     <-- Networking
|   |   +-- VPC, public/private subnets
|   |   +-- NAT Gateway, Internet Gateway
|   |   +-- Route tables, security groups
|   |
|   +-- eks/                     <-- Compute
|   |   +-- EKS cluster, managed node groups
|   |   +-- IRSA (IAM Roles for Service Accounts)
|   |   +-- Cluster autoscaler configuration
|   |
|   +-- rds/                     <-- Database
|   |   +-- PostgreSQL instance (Multi-AZ)
|   |   +-- DB subnet group, parameter group
|   |   +-- Automated backups, encryption at rest
|   |
|   +-- elasticache/             <-- Caching
|       +-- Redis cluster
|       +-- Subnet group, parameter group
|       +-- Encryption in transit
|
+-- environments/
    +-- dev.tfvars               <-- Smaller instances, single AZ
    +-- prod.tfvars              <-- Production-grade sizing, Multi-AZ
```

### Network Topology

```
+----------------------------------------------------------+
|                        AWS VPC                            |
|  CIDR: 10.0.0.0/16                                      |
|                                                          |
|  +-- Public Subnets (10.0.1.0/24, 10.0.2.0/24) ------+ |
|  |   - NAT Gateway                                     | |
|  |   - Load Balancer (ALB)                             | |
|  |   - Bastion Host (if needed)                        | |
|  +-----------------------------------------------------+ |
|                                                          |
|  +-- Private Subnets (10.0.10.0/24, 10.0.20.0/24) ---+ |
|  |   - EKS Worker Nodes                               | |
|  |   - RDS PostgreSQL (Multi-AZ)                      | |
|  |   - ElastiCache Redis                              | |
|  +-----------------------------------------------------+ |
|                                                          |
+----------------------------------------------------------+
```

### State Management

Terraform state is stored remotely to enable safe team collaboration:

- **S3 Bucket**: Versioned state file storage with server-side encryption.
- **DynamoDB Table**: State locking to prevent concurrent modifications.

---

## CI/CD Pipeline

The pipeline uses GitHub Actions for continuous integration and ArgoCD for continuous delivery via GitOps.

### Pipeline Stages

```
+-------+    +---------------------------------------------+    +---------------------------+
| Push  |--->|              CI (GitHub Actions)             |--->|    CD (ArgoCD GitOps)     |
+-------+    |                                             |    |                           |
             |  +------+  +------+  +--------+  +-------+ |    |  +-------+  +-----------+ |
             |  | Lint |->| Test |->|Security|->|Container| |    |  |Staging|->|Production | |
             |  |      |  |      |  | Scan   |  | Build  | |    |  | Auto  |  |Manual Gate| |
             |  +------+  +------+  +--------+  +-------+ |    |  +-------+  +-----------+ |
             +---------------------------------------------+    +---------------------------+
```

### CI Stage Detail

| Step            | Tool                    | Purpose                                |
|----------------|-------------------------|----------------------------------------|
| Lint           | Black, Ruff, MyPy       | Code formatting, linting, type checking|
| Test           | Pytest + Coverage       | Unit and integration tests (>80% cov)  |
| Security Scan  | Bandit, Safety          | SAST and dependency vulnerability scan |
| Container Build| Docker (multi-stage)    | Build and push image to registry        |
| Container Scan | Trivy                   | Scan image for OS/library CVEs          |

### CD Stage Detail

| Step       | Mechanism                | Purpose                              |
|-----------|--------------------------|--------------------------------------|
| Staging   | ArgoCD auto-sync         | Deploy to staging on image push       |
| Testing   | Smoke tests + health     | Validate deployment health            |
| Production| ArgoCD manual sync       | Deploy after manual approval gate     |

### Docker Build Standards

All Docker images follow these conventions:
- Multi-stage builds (builder + runtime) to minimize image size.
- Non-root user (`appuser`, UID 1000) for security.
- `HEALTHCHECK` instruction for container health monitoring.
- Base image: `python:3.12-slim-bookworm`.

### Image Tagging Strategy

```
Image Tag Format:
  - git SHA:    ghcr.io/jdabid/backend-api:abc1234
  - semver:     ghcr.io/jdabid/backend-api:v1.2.3   (on release)
  - latest:     ghcr.io/jdabid/backend-api:latest    (main branch)
```

---

## Monitoring Architecture

The observability stack provides metrics collection, visualization, and alerting. See [ADR-003](adr/003-monitoring-stack.md) for the decision rationale.

### Metrics Pipeline

```
+------------------+     +--------------+     +------------------+
| FastAPI App      |     |              |     |                  |
| /metrics endpoint|---->|  Prometheus  |---->|    Grafana       |
|                  |     |  (scrape     |     |  (dashboards)    |
+------------------+     |   15s)       |     +------------------+
                         |              |
+------------------+     |              |     +------------------+
| Node Exporter    |---->|              |---->|  Alertmanager    |
| (host metrics)   |     |              |     |  (notifications) |
+------------------+     +--------------+     +--------+---------+
                                                       |
+------------------+                          +--------v---------+
| PostgreSQL       |                          | Slack / PagerDuty|
| Exporter         |------------------------>| (alert routing)  |
+------------------+                          +------------------+
|                  |
| Redis Exporter   |
+------------------+
```

### Application-Level Observability

```
HTTP Request
     |
     v
+--------------------+
| Correlation ID     |  <-- Middleware generates UUID per request
| Middleware         |
+--------+-----------+
         |
         v
+--------+-----------+
| Structured JSON    |  <-- All logs include correlation_id field
| Logger             |
+--------+-----------+
         |
    +----+----+
    |         |
    v         v
 stdout    /metrics
 (logs)    (Prometheus)
```

**Log Format Example:**
```json
{
  "timestamp": "2026-03-10T14:30:00Z",
  "level": "INFO",
  "message": "Appointment created",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service": "backend-api",
  "endpoint": "POST /api/v1/appointments",
  "duration_ms": 42
}
```

### Dashboards

| Dashboard        | Key Metrics                                          |
|-----------------|------------------------------------------------------|
| API Overview    | Request rate, error rate (4xx/5xx), p50/p95/p99 latency |
| Infrastructure  | Pod CPU/memory, node utilization, PVC usage          |
| Database        | Connection count, query duration, replication lag    |
| Cache           | Redis hit rate, memory usage, connected clients      |
| Workers         | Celery task throughput, failure rate, queue depth     |

### Alerting Rules

| Alert                  | Condition                           | Severity |
|-----------------------|-------------------------------------|----------|
| High Error Rate       | API 5xx rate > 5% for 5 min        | Critical |
| High Latency          | P95 > 2s for 10 min                | Warning  |
| Pod Crash Loop        | Restarts > 3 in 15 min             | Critical |
| DB Connection Pool    | Utilization > 80%                  | Warning  |
| Queue Backlog         | Celery queue > 100 for 10 min      | Warning  |

---

## Security Architecture

Security is implemented in layers, following defense-in-depth principles.

```
+-----------------------------------------------------------+
|                    Security Layers                         |
|                                                           |
|  +-- Layer 1: Network ---------------------+              |
|  |  - Kubernetes NetworkPolicies           |              |
|  |  - VPC security groups                  |              |
|  |  - Private subnets for data services    |              |
|  +----------------------------------------+              |
|                                                           |
|  +-- Layer 2: Transport -------------------+              |
|  |  - TLS termination (cert-manager)       |              |
|  |  - Let's Encrypt certificates           |              |
|  |  - HTTPS-only ingress                   |              |
|  +----------------------------------------+              |
|                                                           |
|  +-- Layer 3: Authentication ---------------+             |
|  |  - JWT tokens (access + refresh)        |              |
|  |  - bcrypt password hashing              |              |
|  |  - Token expiration and rotation        |              |
|  +----------------------------------------+              |
|                                                           |
|  +-- Layer 4: Pod Security -----------------+             |
|  |  - runAsNonRoot: true                   |              |
|  |  - readOnlyRootFilesystem: true         |              |
|  |  - Drop all capabilities               |              |
|  |  - Resource limits (CPU/memory)         |              |
|  +----------------------------------------+              |
|                                                           |
|  +-- Layer 5: Secrets Management -----------+             |
|  |  - Sealed Secrets (encrypted in Git)    |              |
|  |  - External Secrets Operator (AWS SM)   |              |
|  |  - No plaintext secrets in repo         |              |
|  +----------------------------------------+              |
|                                                           |
|  +-- Layer 6: RBAC -------------------------+             |
|  |  - Kubernetes RBAC (least privilege)    |              |
|  |  - Service accounts per workload        |              |
|  |  - IRSA for AWS access                  |              |
|  +----------------------------------------+              |
+-----------------------------------------------------------+
```

### Kubernetes Security Resources

| Resource           | File                              | Purpose                       |
|-------------------|-----------------------------------|-------------------------------|
| NetworkPolicies   | `kubernetes/security/network-policies.yml` | Restrict pod-to-pod traffic |
| RBAC              | `kubernetes/rbac.yml`             | Role-based access control     |
| TLS / Ingress     | `kubernetes/security/ingress.yml` | HTTPS with cert-manager       |
| Sealed Secrets    | `kubernetes/security/sealed-secrets.yml` | Encrypted secrets in Git |
| External Secrets  | `kubernetes/security/external-secrets.yml` | AWS Secrets Manager sync |
| cert-manager      | `kubernetes/security/cert-manager.yml` | Automated TLS certificates |

---

## Data Flow

### Request Lifecycle

```
1. Client Request
        |
        v
2. +-- Ingress Controller (Nginx) --+
   |   TLS termination              |
   |   Route: /api/* -> backend     |
   |   Route: /*    -> frontend     |
   +-----------+--------------------+
               |
        +------+------+
        |             |
        v             v
3. Frontend        4. Backend API
   (React SPA)        (FastAPI)
   Static files        |
   served by           +-- Middleware: correlation ID, auth, logging
   Nginx               |
                       +-- Router: dispatch to command or query
                       |
                  +----+----+
                  |         |
                  v         v
             5. Command  6. Query
                  |         |
             +----+    +----+----+
             |         |         |
             v         v         v
        7. PostgreSQL  Redis    Redis
           (write)    (cache    (read
                       miss)    cache hit)
                  |
                  v
        8. Celery Worker (async tasks)
           - Send confirmation email
           - Generate reports
           - Process notifications
                  |
                  v
        9. Response back through chain
           Backend -> Ingress -> Client
```

### Async Task Flow

```
API Request                    Celery Worker
    |                               ^
    v                               |
Command                        +----+----+
    |                          | Process  |
    +-- Publish task --------->| Task     |
    |   to Redis broker        +----------+
    v
Immediate Response
(HTTP 202 Accepted)
```

---

## Technology Decisions

Significant architectural decisions are documented as Architecture Decision Records (ADRs) in the `docs/adr/` directory.

| ADR   | Title                    | Status   | Summary                                              |
|-------|--------------------------|----------|------------------------------------------------------|
| [001](adr/001-cqrs-pattern.md)   | CQRS Pattern             | Accepted | Separate read/write operations per feature slice     |
| [002](adr/002-terraform-modules.md) | Terraform Modules        | Accepted | Modular IaC with per-environment tfvars              |
| [003](adr/003-monitoring-stack.md)  | Monitoring Stack         | Accepted | Prometheus + Grafana + Alertmanager + structured logs|

### Technology Stack Summary

| Layer          | Technology                  | Version  |
|---------------|-----------------------------|----------|
| Language      | Python                      | 3.12     |
| Web Framework | FastAPI                     | 0.100+   |
| ORM           | SQLAlchemy                  | 2.0      |
| Validation    | Pydantic                    | v2       |
| Task Queue    | Celery                      | 5.x      |
| Database      | PostgreSQL                  | 15+      |
| Cache/Broker  | Redis                       | 7.x      |
| Frontend      | React + Vite                | 18       |
| Containers    | Docker (multi-stage)        | 24+      |
| Orchestration | Kubernetes (EKS)            | 1.28+    |
| IaC           | Terraform                   | 1.5+     |
| CI            | GitHub Actions              | -        |
| CD            | ArgoCD                      | 2.x      |
| Monitoring    | Prometheus + Grafana        | -        |
| Secrets       | Sealed Secrets + External Secrets | -  |
| TLS           | cert-manager + Let's Encrypt | -       |
