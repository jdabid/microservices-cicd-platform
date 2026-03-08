# Microservices CI/CD Platform

[![CI Pipeline](https://github.com/jdabid/microservices-cicd-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/jdabid/microservices-cicd-platform/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/jdabid/microservices-cicd-platform/actions/workflows/cd.yml/badge.svg)](https://github.com/jdabid/microservices-cicd-platform/actions/workflows/cd.yml)
[![Coverage](https://img.shields.io/badge/coverage-80%25+-brightgreen)](https://github.com/jdabid/microservices-cicd-platform)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/jdabid/microservices-cicd-platform/actions/workflows/ci.yml)
[![Security: Trivy](https://img.shields.io/badge/security-trivy-blue.svg)](https://github.com/jdabid/microservices-cicd-platform/security)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-%3E%3D1.5-purple.svg)](https://www.terraform.io/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326ce5.svg)](https://kubernetes.io/)

Production-ready medical appointments microservices platform demonstrating DevOps best practices. Built with Vertical Slice Architecture and CQRS pattern, fully containerized, orchestrated with Kubernetes, and deployed via GitOps.

## Architecture

```
                          +------------------+
                          |    Frontend      |
                          |  (React + Vite)  |
                          +--------+---------+
                                   |
                                   v
                          +------------------+
                          |   Backend API    |
                          |    (FastAPI)     |
                          |                  |
                          |  Vertical Slices |
                          |  - appointments  |
                          |  - patients      |
                          |  - auth          |
                          +--+-----+------+--+
                             |     |      |
                    +--------+     |      +---------+
                    v              v                 v
              +-----------+  +---------+     +--------------+
              | PostgreSQL |  |  Redis  |     | Celery Worker|
              |   (DB)     |  | (Cache/ |     | (Async Tasks)|
              +-----------+  |  Queue) |     +--------------+
                             +---------+

  ============================================================
       Kubernetes (Deployments, Services, Network Policies)
  ============================================================
       GitOps: ArgoCD  |  Helm Charts  |  GitHub Actions CD
  ============================================================
       Monitoring: Prometheus + Grafana + Alertmanager
  ============================================================
       Infrastructure: Terraform (VPC, EKS, RDS, ElastiCache)
  ============================================================
```

### Architecture Patterns

- **Vertical Slice Architecture** -- Each feature (appointments, patients, auth) is self-contained with its own models, schemas, commands, queries, and router.
- **CQRS** -- Commands handle write operations; Queries handle read operations. Clear separation of concerns throughout.

## Tech Stack

### Application

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | Python 3.12 + FastAPI | RESTful API service |
| **Worker** | Celery | Async task processing |
| **Frontend** | React 18 + Vite + Nginx | User interface |
| **Database** | PostgreSQL 15 | Primary data store |
| **Cache/Queue** | Redis 7 | Caching + message broker |

### DevOps

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containers** | Docker (multi-stage) | Application packaging |
| **Orchestration** | Kubernetes | Container management |
| **CI** | GitHub Actions | Lint, test, security scan |
| **CD** | GitHub Actions + ArgoCD | Staging auto, prod with approval |
| **IaC** | Terraform | AWS infrastructure (VPC, EKS, RDS, ElastiCache) |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Alerting** | Alertmanager | Incident notification |
| **Package Management** | Helm | Kubernetes templating |

## Project Structure

```
microservices-cicd-platform/
+-- backend-api/
|   +-- app/
|   |   +-- core/              # Config, security, Celery setup
|   |   +-- common/            # Database, dependencies, exceptions
|   |   +-- features/
|   |   |   +-- appointments/  # CQRS: commands/, queries/, models/, schemas/
|   |   |   +-- patients/      # CQRS: commands/, queries/, models/, schemas/
|   |   |   +-- auth/          # JWT authentication + RBAC
|   |   +-- tasks/             # Celery background tasks
|   +-- tests/
|       +-- unit/              # Unit tests per feature
|       +-- integration/       # Integration tests (auth, patients, appointments)
+-- frontend/                  # React 18 + Vite + Nginx
+-- kubernetes/                # K8s manifests (deployments, services, RBAC)
|   +-- security/              # Network policies (zero-trust)
|   +-- monitoring/            # ServiceMonitor, Prometheus rules
+-- terraform/
|   +-- modules/
|   |   +-- vpc/               # AWS VPC with public/private subnets
|   |   +-- eks/               # EKS cluster configuration
|   |   +-- rds/               # PostgreSQL RDS instance
|   |   +-- elasticache/       # Redis ElastiCache cluster
|   +-- environments/          # Per-environment tfvars (dev, prod)
+-- monitoring/
|   +-- prometheus/            # Prometheus configuration
|   +-- grafana/               # Dashboards and provisioning
|   +-- alertmanager/          # Alert rules and routing
+-- .github/workflows/
|   +-- ci.yml                 # Lint, test, Bandit, Trivy
|   +-- cd.yml                 # Build, push, deploy staging/prod
+-- helm/                      # Helm chart for the platform
+-- docs/                      # Architecture and evaluation docs
```

## Features Implemented

- [x] JWT Authentication + Role-Based Access Control (RBAC)
- [x] CQRS Pattern (Commands for writes, Queries for reads)
- [x] Vertical Slice Architecture (self-contained features)
- [x] CI Pipeline (linting, type checking, tests, coverage, security scans)
- [x] CD Pipeline (staging auto-deploy, production with manual approval)
- [x] Docker multi-stage builds (non-root, health checks)
- [x] Kubernetes deployments with security hardening
- [x] Network Policies (zero-trust pod communication)
- [x] Terraform IaC (VPC, EKS, RDS, ElastiCache modules)
- [x] Prometheus + Grafana monitoring with custom dashboards
- [x] Alertmanager for incident notification
- [x] Structured logging with correlation IDs
- [x] Helm charts for templated deployments
- [x] ArgoCD GitOps continuous delivery
- [x] Pre-commit hooks (Black, Ruff, mypy)
- [x] Integration tests (auth, patients, appointments)

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/jdabid/microservices-cicd-platform.git
cd microservices-cicd-platform

# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Run backend API
cd backend-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Access API docs
open http://localhost:8000/docs
```

### Docker

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes

```bash
# Local cluster (Minikube)
minikube start --cpus=4 --memory=8192

# Deploy
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/

# Check status
kubectl get all -n microservices-cicd-platform

# Access application
kubectl port-forward -n microservices-cicd-platform svc/backend-api 8000:80
```

## Testing

```bash
cd backend-api

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-fail-under=80

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# View coverage report
open htmlcov/index.html
```

## Infrastructure

Terraform modules provision the full AWS stack:

```bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

| Module | Resources |
|--------|-----------|
| **vpc** | VPC, public/private subnets, NAT gateway, route tables |
| **eks** | EKS cluster, managed node groups, IAM roles |
| **rds** | PostgreSQL RDS instance, subnet groups, security groups |
| **elasticache** | Redis ElastiCache cluster, parameter groups |

## Monitoring

Prometheus + Grafana stack with pre-configured dashboards:

```bash
# Start monitoring stack
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3000    # admin / admin

# Access Prometheus
open http://localhost:9090
```

Alertmanager handles incident routing for critical metrics (pod restarts, high error rates, resource exhaustion).

## Security

- **Application**: JWT authentication, RBAC, input validation (Pydantic v2)
- **CI**: Bandit static analysis, Trivy container scanning
- **Docker**: Multi-stage builds, non-root user (UID 1000), no cached packages
- **Kubernetes**: Pod security contexts (`runAsNonRoot`), network policies (zero-trust), RBAC
- **Infrastructure**: Private subnets for data stores, security groups, encrypted storage
- **Code Quality**: Pre-commit hooks (Black, Ruff, mypy), 80%+ test coverage enforced

## Author

**David Castro** -- DevOps Engineer & Python Developer

- GitHub: [@jdabid](https://github.com/jdabid)
- LinkedIn: [david-castro-vanegas](https://www.linkedin.com/in/david-castro-vanegas/)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
