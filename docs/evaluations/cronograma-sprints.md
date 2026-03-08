# Cronograma de Sprints — Tracking en Tiempo Real

> Este documento se actualiza automaticamente cada vez que se finaliza una User Story.
> Ultima actualizacion: 2026-03-10

---

## Resumen General

| Metrica | Valor |
|---------|-------|
| Total User Stories | 50 |
| Completadas | 35 |
| En progreso | 0 |
| Pendientes | 15 |
| Story Points totales | 136 |
| Story Points completados | 95 |
| Story Points restantes | 41 |
| Velocidad actual | 31 SP (S1), 21 SP (S2), 21 SP (S3), 22 SP (S4) |
| Sprint actual | Sprint 4 COMPLETADO |

### Progreso Global

```
Completado: [############################__________] 70%  (95/136 SP)
```

---

## Sprint 1 — Limpieza y Credibilidad

**Sprint Goal:** El repositorio esta limpio, profesional, con autenticacion JWT y manejo de errores implementados.
**Duracion:** Semana 1-2
**Estado:** COMPLETADO
**SP Completados:** 31/32

```
Sprint 1: [#####################################_] 97%  (31/32 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-01 | Actualizar .gitignore y limpiar archivos del tracking | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-02 | Eliminar .env del repositorio, verificar .env.example | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-03 | Eliminar archivos innecesarios (.backup, .corrupted, main.py raiz) | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-04 | Login y JWT para acceder a la API de forma segura | 5 | DONE | `feature/s1-US04-jwt-auth` | [#9](https://github.com/jdabid/microservices-cicd-platform/pull/9) | 2026-03-06 |
| US-05 | Sistema de excepciones centralizado | 3 | DONE | `feature/s1-US05-exception-handling` | [#8](https://github.com/jdabid/microservices-cicd-platform/pull/8) | 2026-03-06 |
| US-06 | Completar feature patients/ con CRUD completo (CQRS) | 5 | DONE | `feature/s1-US06-to-US07-patients-crud` | [#16](https://github.com/jdabid/microservices-cicd-platform/pull/16) | 2026-03-09 |
| US-07 | Tests unitarios para patients/ (minimo 8 tests) | 3 | DONE | `feature/s1-US06-to-US07-patients-crud` | [#16](https://github.com/jdabid/microservices-cicd-platform/pull/16) | 2026-03-09 |
| US-08 | Corregir strings hardcodeados por enums en update_appointment.py | 1 | DONE | `feature/s1-US08-fix-enum-strings` | [#10](https://github.com/jdabid/microservices-cicd-platform/pull/10) | 2026-03-07 |
| US-09 | CORS configurado por ambiente y rate limiting en auth | 3 | DONE | `feature/s1-US09-cors-rate-limiting` | [#13](https://github.com/jdabid/microservices-cicd-platform/pull/13) | 2026-03-07 |
| US-10 | Configurar ruff y mypy para calidad de codigo | 3 | DONE | `feature/s1-US10-ruff-mypy` | [#11](https://github.com/jdabid/microservices-cicd-platform/pull/11) | 2026-03-07 |
| US-11 | Reemplazar psycopg2-binary por asyncpg | 3 | DONE | `feature/s1-US11-asyncpg` | [#12](https://github.com/jdabid/microservices-cicd-platform/pull/12) | 2026-03-07 |
| US-12 | Corregir time.sleep() en Celery tasks y datetime sin timezone | 1 | DONE | `feature/s1-US12-fix-sleep-datetime` | [#14](https://github.com/jdabid/microservices-cicd-platform/pull/14) | 2026-03-08 |
| US-13 | Corregir typos en Dockerfiles (emails en LABEL) | 1 | DONE | `feature/s1-US13-fix-dockerfile-typos` | [#15](https://github.com/jdabid/microservices-cicd-platform/pull/15) | 2026-03-08 |

### Notas del Sprint 1
- US-01, US-02, US-03 completadas en batch (misma PR #6, eran tareas de limpieza interdependientes)
- US-04 y US-05 lanzadas en paralelo con Agents en worktree isolation
- US-05 completada primero (PR #8), US-04 despues (PR #9) - cherry-pick desde worktree
- US-04 creo 17 archivos (676 lineas): auth feature completo con CQRS + 15 tests
- US-05 creo 6 archivos (535 lineas): exception hierarchy + handlers + 30 tests
- US-08, US-09, US-10, US-11 completadas en batch (agents en worktree + implementacion directa)
- US-08: fix 1 linea hardcoded string → AppointmentStatus enum (PR #10)
- US-09: slowapi rate limiting + CORS por ambiente (PR #13)
- US-10: pyproject.toml con ruff + mypy config (PR #11)
- US-11: asyncpg reemplaza psycopg2-binary, async session factory (PR #12)
- US-12: remove time.sleep, fix datetime.utcnow → datetime.now(timezone.utc) (PR #14)
- US-13: fix email typos en 3 Dockerfiles (dabid→david, gmailc→gmail) (PR #15)
- US-06 y US-07 completadas en batch (interdependientes, misma PR #16)
- US-06: 18 archivos, 625 lineas - patients CRUD completo con CQRS
- US-07: 13 tests unitarios (8 commands + 5 queries) - todos pasando

---

## Sprint 2 — Testing y Calidad

**Sprint Goal:** Alcanzar >80% de coverage con tests de integracion y pipeline CI reportando calidad.
**Duracion:** Semana 3-4
**Estado:** COMPLETADO
**SP Completados:** 21/21

```
Sprint 2: [######################################] 100%  (21/21 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-14 | Tests de integracion con TestClient para appointments/ | 5 | DONE | `feature/s2-US14-to-US16-integration-tests` | [#18](https://github.com/jdabid/microservices-cicd-platform/pull/18) | 2026-03-09 |
| US-15 | Tests de integracion con TestClient para patients/ | 3 | DONE | `feature/s2-US14-to-US16-integration-tests` | [#18](https://github.com/jdabid/microservices-cicd-platform/pull/18) | 2026-03-09 |
| US-16 | Tests de integracion para auth/ | 3 | DONE | `feature/s2-US14-to-US16-integration-tests` | [#18](https://github.com/jdabid/microservices-cicd-platform/pull/18) | 2026-03-09 |
| US-17 | pytest-cov con threshold minimo 80% y reporte HTML | 2 | DONE | `feature/s2-US17-pytest-cov-threshold` | — | 2026-03-09 |
| US-18 | Pre-commit hooks con black, ruff, mypy | 3 | DONE | `feature/s2-US18-pre-commit-hooks` | [#17](https://github.com/jdabid/microservices-cicd-platform/pull/17) | 2026-03-09 |
| US-19 | Coverage badge en CI y README actualizado | 1 | DONE | `feature/s2-US19-to-US20-ci-pipeline` | [#19](https://github.com/jdabid/microservices-cicd-platform/pull/19) | 2026-03-10 |
| US-20 | Agregar bandit al pipeline CI | 2 | DONE | `feature/s2-US19-to-US20-ci-pipeline` | [#19](https://github.com/jdabid/microservices-cicd-platform/pull/19) | 2026-03-10 |
| US-21 | Tests para Celery tasks (email, notification) | 2 | DONE | `feature/s2-US21-celery-task-tests` | [#20](https://github.com/jdabid/microservices-cicd-platform/pull/20) | 2026-03-10 |

### Notas del Sprint 2
- US-18 completada primero (PR #17): .pre-commit-config.yaml con black, ruff, mypy, pre-commit-hooks
- US-14, US-15, US-16 completadas en batch (misma PR #18, tests de integracion interdependientes)
- US-14: 8 tests (create, get, list, cancel, update appointments)
- US-15: 7 tests (create, get, list, update, soft-delete patients)
- US-16: 7 tests (register, login, token validation, protected routes)
- US-17: pytest-cov configurado con --cov-fail-under=80 y reporte HTML
- US-19 y US-20 completadas en batch (misma PR #19): CI pipeline con 3 jobs (lint, test, security)
- US-19: GitHub Actions CI con pytest-cov, coverage badge en README, PR coverage comments
- US-20: Bandit security scan job, falla en HIGH severity, config en pyproject.toml
- US-21 completada independiente (PR #20): 23 tests para Celery tasks (13 email + 10 notification)

---

## Sprint 3 — Infrastructure as Code (Terraform)

**Sprint Goal:** Infraestructura como codigo funcional que puede provisionar un ambiente completo en AWS.
**Duracion:** Semana 5-6
**Estado:** COMPLETADO
**SP Completados:** 21/21

```
Sprint 3: [######################################] 100%  (21/21 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-22 | Estructura base Terraform con providers y backend remoto (S3 + DynamoDB) | 3 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-23 | Modulo VPC con subnets publicas/privadas, NAT gateway | 5 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-24 | Modulo EKS con cluster, node group, IAM roles | 5 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-25 | Modulo RDS para PostgreSQL con subnet group | 3 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-26 | Modulo ElastiCache para Redis con subnet group | 3 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-27 | tfvars para ambientes dev y prod diferenciados | 1 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |
| US-28 | Documentacion de infraestructura con diagrama de red | 1 | DONE | `feature/s3-US22-to-US28-terraform` | [#21](https://github.com/jdabid/microservices-cicd-platform/pull/21) | 2026-03-10 |

### Notas del Sprint 3
- Sprint completo en una sola PR #21 (7 US batch, todas interdependientes)
- 3 Agents en worktree isolation ejecutados en paralelo:
  - Agent 1: US-22 + US-23 (base + VPC) — 8 archivos
  - Agent 2: US-24 + US-25 + US-26 (EKS + RDS + ElastiCache) — 9 archivos
  - Agent 3: US-27 + US-28 (tfvars + docs) — 3 archivos
- Consolidacion manual de archivos desde 3 worktrees + integracion root main.tf/variables.tf/outputs.tf
- 20 archivos, 1,227 lineas de Terraform
- Modulos: vpc (2 AZ, IGW, NAT), eks (cluster + node group + IAM), rds (PostgreSQL 15), elasticache (Redis 7)
- Ambientes: dev (cost-efficient) vs prod (HA, Multi-AZ, nodes mas grandes)

---

## Sprint 4 — Monitoreo y Observabilidad

**Sprint Goal:** Monitoreo funcional con Prometheus, Grafana, logging estructurado y alertas basicas.
**Duracion:** Semana 7-8
**Estado:** COMPLETADO
**SP Completados:** 22/22

```
Sprint 4: [######################################] 100%  (22/22 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-29 | Configuracion Prometheus con scrape configs | 3 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-30 | Docker-compose para stack de monitoreo | 3 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-31 | Dashboard Grafana para backend-api (request rate, latency, errors) | 5 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-32 | Dashboard Grafana para infraestructura (CPU, memoria, disco) | 3 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-33 | Alertmanager con reglas basicas | 3 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-34 | Structured logging con python-json-logger y correlation IDs | 3 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |
| US-35 | Manifiestos K8s para Prometheus y Grafana | 2 | DONE | `feature/s4-US29-to-US35-monitoring` | [#22](https://github.com/jdabid/microservices-cicd-platform/pull/22) | 2026-03-10 |

### Notas del Sprint 4
- Sprint completo en una sola PR #22 (7 US batch)
- 3 Agents en worktree isolation ejecutados en paralelo:
  - Agent 1: US-29 + US-30 + US-33 (Prometheus + docker-compose + Alertmanager) — 4 archivos
  - Agent 2: US-31 + US-32 + US-35 (Grafana dashboards + K8s manifests) — 9 archivos
  - Agent 3: US-34 (Structured logging + correlation IDs) — 2 nuevos + 1 modificado
- 16 archivos, 1,557 lineas
- Prometheus: scrape configs para backend-api, node, redis, postgres con 10s/15s intervals
- Grafana: 2 dashboards JSON (backend-api 6 paneles, infra 7 paneles) + provisioning automatico
- Alertmanager: 8 reglas (error rate >5%, latency >2s, service down, CPU >80%, memory >85%, disk <15%, PG/Redis down)
- Logging: JSON estructurado con correlation IDs via X-Correlation-ID header
- K8s: namespace monitoring + deployments con securityContext, probes, resource limits

---

## Sprint 5 — Seguridad y Hardening

**Sprint Goal:** Seguridad reforzada en CI/CD, Kubernetes y configuracion de red.
**Duracion:** Semana 9-10
**Estado:** NO INICIADO
**SP Completados:** 0/20

```
Sprint 5: [______________________________________] 0%  (0/20 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-36 | Trivy container scanning en CI/CD pipeline | 3 | PENDIENTE | — | — | — |
| US-37 | SecurityContext en todos los pods K8s | 3 | PENDIENTE | — | — | — |
| US-38 | Network Policies para aislar trafico entre servicios | 5 | PENDIENTE | — | — | — |
| US-39 | TLS en Ingress con cert-manager y Let's Encrypt | 3 | PENDIENTE | — | — | — |
| US-40 | RBAC con ServiceAccount, Role y RoleBinding | 2 | PENDIENTE | — | — | — |
| US-41 | PodDisruptionBudget para servicios criticos | 2 | PENDIENTE | — | — | — |
| US-42 | Sealed Secrets o External Secrets para credenciales | 2 | PENDIENTE | — | — | — |

### Notas del Sprint 5
_(sin notas aun)_

---

## Sprint 6 — GitOps, Helm y Deploy Final

**Sprint Goal:** Proyecto listo para portafolio con Helm, GitOps, documentacion profesional y deploy publico.
**Duracion:** Semana 11-12
**Estado:** NO INICIADO
**SP Completados:** 0/20

```
Sprint 6: [______________________________________] 0%  (0/20 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-43 | Helm chart para la aplicacion completa | 5 | PENDIENTE | — | — | — |
| US-44 | ArgoCD Application manifest para deployment automatico | 3 | PENDIENTE | — | — | — |
| US-45 | CD workflow en GitHub Actions (staging auto, prod con aprobacion) | 3 | PENDIENTE | — | — | — |
| US-46 | README.md actualizado con badges reales | 3 | PENDIENTE | — | — | — |
| US-47 | 3 ADRs (CQRS, Terraform, stack de monitoreo) | 2 | PENDIENTE | — | — | — |
| US-48 | docs/ARCHITECTURE.md con diagramas actualizados | 2 | PENDIENTE | — | — | — |
| US-49 | Revision final: tests, coverage, CI verde, repo limpio | 1 | PENDIENTE | — | — | — |
| US-50 | Video demo para LinkedIn | 1 | PENDIENTE | — | — | — |

### Notas del Sprint 6
_(sin notas aun)_

---

## Burndown Chart

```
Story Points
Restantes
  136 |*
      |  \
  125 |    \
      |      \
  115 |        \
      |          \
  105 |            *  <- fin Sprint 1 (13 US, 31 SP)
      |              \
   89 |                \
      |                  \
   84 |                    *  <- fin Sprint 2 (21 US, 52 SP)
      |                      \
      |                        \
   63 |                          *  <- fin Sprint 3 (28 US, 73 SP)
      |                            \
      |                              \
   41 |                                *  <- actual (35 US completadas, 95 SP, Sprint 4 DONE)
      |
   83 |
      |
   62 |
      |
   40 |
      |
   20 |
      |
    0 |________________________________________
      S1         S2         S3         S4         S5         S6
```

---

## Historial de Cambios

| Fecha | US | Accion | SP | Herramientas usadas |
|-------|-----|--------|----|---------------------|
| 2026-03-06 | US-01 | COMPLETADA | 1 | Bash (git rm --cached), Write (.gitignore) |
| 2026-03-06 | US-02 | COMPLETADA | 1 | Bash (git rm --cached), Read (.env verification) |
| 2026-03-06 | US-03 | COMPLETADA | 1 | Bash (git rm --cached main.py, *.backup, *.corrupted) |
| 2026-03-06 | US-05 | COMPLETADA | 3 | Agent (worktree isolation), Bash (cherry-pick, gh pr) |
| 2026-03-06 | US-04 | COMPLETADA | 5 | Agent (worktree isolation), Bash (cherry-pick, gh pr) |
| 2026-03-07 | US-08 | COMPLETADA | 1 | Edit (enum fix), Bash (gh pr) |
| 2026-03-07 | US-10 | COMPLETADA | 3 | Agent (worktree), Write (pyproject.toml), Edit (requirements) |
| 2026-03-07 | US-11 | COMPLETADA | 3 | Agent (worktree), Write (session.py, database.py), Edit (config, requirements) |
| 2026-03-07 | US-09 | COMPLETADA | 3 | Edit (config, main, router, requirements), Bash (gh pr) |
| 2026-03-08 | US-12 | COMPLETADA | 1 | Edit (email_tasks, notification_tasks, list_appointments) |
| 2026-03-08 | US-13 | COMPLETADA | 1 | Edit (Dockerfile, Dockerfile.worker, frontend/Dockerfile) |
| 2026-03-09 | US-06 | COMPLETADA | 5 | Write (model, schemas, commands, queries, router), Edit (main.py) |
| 2026-03-09 | US-07 | COMPLETADA | 3 | Write (test_commands.py, test_queries.py), 13 tests passing |
| 2026-03-09 | US-18 | COMPLETADA | 3 | Write (.pre-commit-config.yaml), pre-commit hooks: black, ruff, mypy |
| 2026-03-09 | US-14 | COMPLETADA | 5 | Write (test_appointments.py), 8 integration tests con TestClient |
| 2026-03-09 | US-15 | COMPLETADA | 3 | Write (test_patients.py), 7 integration tests con TestClient |
| 2026-03-09 | US-16 | COMPLETADA | 3 | Write (test_auth.py), 7 integration tests con TestClient |
| 2026-03-09 | US-17 | COMPLETADA | 2 | Edit (pyproject.toml), pytest-cov --cov-fail-under=80 + HTML report |
| 2026-03-10 | US-19 | COMPLETADA | 1 | Write (ci.yml), Edit (README.md), badges CI + coverage + security |
| 2026-03-10 | US-20 | COMPLETADA | 2 | Write (ci.yml bandit job), Edit (pyproject.toml bandit config) |
| 2026-03-10 | US-21 | COMPLETADA | 2 | Write (test_email_tasks.py, test_notification_tasks.py), 23 tests |
| 2026-03-10 | US-22 | COMPLETADA | 3 | Write (versions.tf, providers.tf, main.tf, variables.tf, outputs.tf) |
| 2026-03-10 | US-23 | COMPLETADA | 5 | Write (modules/vpc/*), VPC + 2 AZ + IGW + NAT |
| 2026-03-10 | US-24 | COMPLETADA | 5 | Write (modules/eks/*), cluster + node group + IAM roles |
| 2026-03-10 | US-25 | COMPLETADA | 3 | Write (modules/rds/*), PostgreSQL 15 + encryption + backups |
| 2026-03-10 | US-26 | COMPLETADA | 3 | Write (modules/elasticache/*), Redis 7 + subnet group |
| 2026-03-10 | US-27 | COMPLETADA | 1 | Write (environments/dev.tfvars, prod.tfvars) |
| 2026-03-10 | US-28 | COMPLETADA | 1 | Write (terraform/README.md), ASCII network diagram |
| 2026-03-10 | US-29 | COMPLETADA | 3 | Write (prometheus/prometheus.yml), 5 scrape configs |
| 2026-03-10 | US-30 | COMPLETADA | 3 | Write (docker-compose.monitoring.yml), 6 servicios |
| 2026-03-10 | US-31 | COMPLETADA | 5 | Write (backend-api.json), 6 paneles Grafana |
| 2026-03-10 | US-32 | COMPLETADA | 3 | Write (infrastructure.json), 7 paneles Grafana |
| 2026-03-10 | US-33 | COMPLETADA | 3 | Write (alert_rules.yml, alertmanager.yml), 8 reglas |
| 2026-03-10 | US-34 | COMPLETADA | 3 | Write (logging.py, middleware.py), Edit (main.py) |
| 2026-03-10 | US-35 | COMPLETADA | 2 | Write (5 K8s manifests monitoring namespace) |
