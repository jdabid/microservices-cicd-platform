# Microservices CI/CD Platform

🚧 **Work in Progress** - Building a production-ready microservices platform 🚧

[![CI Pipeline](https://github.com/tu-usuario/microservices-cicd-platform/workflows/CI%20Pipeline/badge.svg)](https://github.com/tu-usuario/microservices-cicd-platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A complete microservices platform demonstrating modern DevOps practices with Vertical Slice Architecture and CQRS pattern.

## 🎯 Project Goals

Build a **production-grade microservices application** showcasing:
- ✅ Modern Python backend architecture (Vertical Slice + CQRS)
- ✅ Complete CI/CD automation
- ✅ Container orchestration with Kubernetes
- ✅ Infrastructure as Code
- ✅ Comprehensive monitoring and observability
- ✅ Security best practices

## 🏗️ Architecture

### High-Level Overview
```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│   Backend API        │
│   (FastAPI)          │
│                      │
│   Vertical Slices:   │
│   ├── appointments/  │ ← CQRS: Commands + Queries
│   ├── patients/      │
│   └── doctors/       │
└──────┬───────────────┘
       │
   ┌───┴────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼
┌──────┐ ┌─────┐  ┌────────┐  ┌─────────┐
│  DB  │ │Redis│  │ Worker │  │  Queue  │
│ (PG) │ │     │  │(Celery)│  │ (Redis) │
└──────┘ └─────┘  └────────┘  └─────────┘

═══════════════════════════════════════════
    Orchestrated by Kubernetes
═══════════════════════════════════════════
    Deployed via GitHub Actions CI/CD
═══════════════════════════════════════════
    Monitored with Prometheus + Grafana
═══════════════════════════════════════════
```

### Architecture Patterns

**Vertical Slice Architecture:**
- Each feature is self-contained with all necessary layers
- Reduces coupling between features
- Easier to understand, test, and maintain

**CQRS (Command Query Responsibility Segregation):**
- Commands: Write operations (POST, PUT, DELETE)
- Queries: Read operations (GET)
- Clear separation of concerns

## 📂 Project Structure
```
microservices-cicd-platform/
├── backend-api/              # FastAPI backend
│   └── app/
│       ├── core/             # Configuration
│       ├── common/           # Shared utilities
│       └── features/         # VERTICAL SLICES
│           └── appointments/
│               ├── commands/ # Write ops (CQRS)
│               ├── queries/  # Read ops (CQRS)
│               ├── models/   # SQLAlchemy
│               └── schemas/  # Pydantic
├── backend-worker/           # Celery async workers
├── frontend/                 # React frontend
├── kubernetes/               # K8s manifests
├── terraform/                # Infrastructure as Code
├── monitoring/               # Prometheus + Grafana
├── .github/workflows/        # CI/CD pipelines
└── docs/                     # Documentation
```

## 🚀 Tech Stack

### Application
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | Python 3.11 + FastAPI | RESTful API service |
| **Worker** | Celery | Async task processing |
| **Frontend** | React 18 | User interface |
| **Database** | PostgreSQL 15 | Primary data store |
| **Cache/Queue** | Redis 7 | Caching + message broker |

### DevOps
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Kubernetes | Container management |
| **CI/CD** | GitHub Actions | Automation pipeline |
| **IaC** | Terraform | Infrastructure provisioning |
| **Monitoring** | Prometheus + Grafana | Observability |
| **Cloud** | AWS (EKS, RDS, ElastiCache) | Infrastructure |

## 📋 Prerequisites

- Python 3.11+
- Docker 20.10+
- Docker Compose
- kubectl (for K8s)
- Terraform 1.5+ (for cloud deployment)
- Node.js 18+ (for frontend)

## ⚡ Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/tu-usuario/microservices-cicd-platform.git
cd microservices-cicd-platform

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Run backend API
cd backend-api
source venv/bin/activate
uvicorn app.main:app --reload

# Access API documentation
open http://localhost:8000/docs
```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing
```bash
# Backend API tests
cd backend-api
pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🐳 Docker
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend-api

# Stop and remove
docker-compose down -v
```

## ☸️ Kubernetes Deployment

### Local (Minikube/Kind)
```bash
# Start local cluster
minikube start --cpus=4 --memory=8192

# Deploy application
kubectl apply -f kubernetes/

# Check status
kubectl get all -n microservices

# Access application
kubectl port-forward svc/backend-api 8000:80
```

### Cloud (AWS EKS)
```bash
# Provision infrastructure
cd terraform/aws
terraform init
terraform apply

# Configure kubectl
aws eks update-kubeconfig --name microservices-cluster --region us-east-1

# Deploy application
kubectl apply -f kubernetes/
```

## 📊 Monitoring

Access monitoring dashboards:
```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
open http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80
open http://localhost:3000
# Login: admin / admin
```

## 📚 Documentation

- [Architecture Deep Dive](docs/ARCHITECTURE.md)
- [Vertical Slice Pattern](docs/VERTICAL_SLICE.md)
- [CQRS Pattern](docs/CQRS.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🗓️ Development Roadmap

| Week | Phase | Status |
|------|-------|--------|
| **Week 1** | Backend API + CQRS | ✅ In Progress |
| **Week 2** | Dockerization | ⏳ Planned |
| **Week 3** | CI Pipeline | ⏳ Planned |
| **Week 4** | Kubernetes | ⏳ Planned |
| **Week 5** | CD Pipeline | ⏳ Planned |
| **Week 6** | Infrastructure as Code | ⏳ Planned |
| **Week 7** | Monitoring & Observability | ⏳ Planned |
| **Week 8** | Documentation & Polish | ⏳ Planned |

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Modern Python backend architecture
- ✅ Microservices design patterns
- ✅ Complete CI/CD automation
- ✅ Container orchestration
- ✅ Infrastructure as Code
- ✅ Cloud-native development
- ✅ Production-grade monitoring
- ✅ Security best practices

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 👤 Author

**David Castro**
- GitHub: [@jdabid](https://github.com/jdabid)
- LinkedIn: [david-castro-vanegas](https://www.linkedin.com/in/david-castro-vanegas/)
- Email: dabid.banegas@gmail.com

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built as part of DevOps learning journey. Special thanks to the open-source community.

**Key Technologies:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [Prometheus](https://prometheus.io/) - Monitoring system
- [Grafana](https://grafana.com/) - Observability platform

---

⭐ **Star this repo if you find it helpful!**

📌 *This is a learning/portfolio project demonstrating DevOps practices with modern Python architecture.*