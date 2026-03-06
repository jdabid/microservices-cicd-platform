# Microservices CI/CD Platform - Claude Code Instructions

## Project Overview
Medical appointments microservices platform demonstrating DevOps + Python Backend skills for portfolio.
Stack: FastAPI + PostgreSQL + Redis + Celery + Docker + Kubernetes + GitHub Actions.

## Architecture
- **Pattern**: Vertical Slice Architecture + CQRS (Command Query Responsibility Segregation)
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Celery
- **Frontend**: React 18 + Vite + Nginx
- **Infrastructure**: Docker (multi-stage), Kubernetes, GitHub Actions CI/CD

## Project Structure
```
backend-api/app/
  core/           -> config.py, security.py, celery/
  common/         -> database/, dependencies/, exceptions/
  features/       -> Each feature is a vertical slice with:
    <feature>/
      commands/   -> Write operations (CQRS)
      queries/    -> Read operations (CQRS)
      models/     -> SQLAlchemy models
      schemas/    -> Pydantic schemas
      router.py   -> FastAPI router
  tasks/          -> Celery background tasks
backend-api/tests/
  unit/features/  -> Unit tests per feature
  integration/    -> Integration tests (to be created)
kubernetes/       -> K8s manifests
.github/workflows/ -> CI/CD pipelines
terraform/        -> IaC (to be created)
monitoring/       -> Prometheus + Grafana (to be created)
```

## Development Roadmap (Current Sprint Backlog)
See `docs/evaluations/cronograma-scrum.md` for full backlog.
See `docs/evaluations/cronograma-sprints.md` for live tracking.

## Coding Conventions

### Python / Backend
- Use type hints on ALL functions (params + return)
- Use Pydantic v2 for all schemas with field validators
- Use async def for all endpoint handlers and database operations
- Use asyncpg (not psycopg2-binary) for async DB access
- Use AppointmentStatus enum, NEVER hardcoded strings for status
- Use timezone-aware datetimes: `datetime.now(timezone.utc)`
- Follow CQRS: commands/ for writes, queries/ for reads - never mix
- Each feature must have its own router, models, schemas, commands, queries
- Custom exceptions go in common/exceptions/ - never raise raw HTTPException from commands/queries
- Tests: pytest + pytest-asyncio, follow Arrange-Act-Assert pattern
- Naming: snake_case for files/functions/variables, PascalCase for classes

### Docker
- Always multi-stage builds (builder + runtime)
- Always non-root user (appuser UID 1000)
- Always include HEALTHCHECK
- Always use --no-cache-dir for pip install
- Base image: python:3.12-slim-bookworm

### Kubernetes
- All resources must specify namespace: microservices-cicd-platform
- All deployments must have resource requests AND limits
- All deployments must have liveness AND readiness probes
- All pods must have securityContext (runAsNonRoot: true)
- Secrets must NEVER contain real credentials in the repo

### Terraform
- Use modules for each infrastructure component
- Use variables with descriptions and type constraints
- Use remote state (S3 + DynamoDB)
- Separate tfvars per environment (dev, prod)
- Mark sensitive variables as sensitive = true

### CI/CD
- Conventional commits: feat(), fix(), docs(), test(), chore(), refactor()
- All PRs must pass CI before merge
- Docker images tagged with: git SHA, semver (on release), latest

### Git
- Branch naming: feature/<name>, fix/<name>, chore/<name>
- Never commit .env, .idea/, node_modules/, __pycache__/
- Never commit files with real secrets or passwords

## Commands Available
- `/sprint-status` - Check current sprint progress
- `/implement` - Implement a specific user story from the backlog
- `/test` - Run tests and check coverage
- `/review` - Code review for current changes
- `/docker-check` - Validate Docker configurations
- `/k8s-check` - Validate Kubernetes manifests
- `/security-audit` - Run security analysis
- `/cleanup` - Find and fix repo cleanliness issues
- `/terraform-validate` - Validate Terraform modules
- `/pre-commit` - Run all pre-commit checks
- `/update-sprint-tracker` - Update sprint tracking after completing a user story
