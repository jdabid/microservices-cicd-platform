# Cronograma de Sprints — Tracking en Tiempo Real

> Este documento se actualiza automaticamente cada vez que se finaliza una User Story.
> Ultima actualizacion: 2026-03-08

---

## Resumen General

| Metrica | Valor |
|---------|-------|
| Total User Stories | 50 |
| Completadas | 11 |
| En progreso | 0 |
| Pendientes | 39 |
| Story Points totales | 136 |
| Story Points completados | 23 |
| Story Points restantes | 113 |
| Velocidad actual | 23 SP (Sprint 1 en progreso) |
| Sprint actual | Sprint 1 EN PROGRESO |

### Progreso Global

```
Completado: [######________________________________] 17%  (23/136 SP)
```

---

## Sprint 1 — Limpieza y Credibilidad

**Sprint Goal:** El repositorio esta limpio, profesional, con autenticacion JWT y manejo de errores implementados.
**Duracion:** Semana 1-2
**Estado:** EN PROGRESO
**SP Completados:** 23/32

```
Sprint 1: [###########################___________] 72%  (23/32 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-01 | Actualizar .gitignore y limpiar archivos del tracking | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-02 | Eliminar .env del repositorio, verificar .env.example | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-03 | Eliminar archivos innecesarios (.backup, .corrupted, main.py raiz) | 1 | DONE | `feature/s1-US01-US02-US03-repo-cleanup` | [#6](https://github.com/jdabid/microservices-cicd-platform/pull/6) | 2026-03-06 |
| US-04 | Login y JWT para acceder a la API de forma segura | 5 | DONE | `feature/s1-US04-jwt-auth` | [#9](https://github.com/jdabid/microservices-cicd-platform/pull/9) | 2026-03-06 |
| US-05 | Sistema de excepciones centralizado | 3 | DONE | `feature/s1-US05-exception-handling` | [#8](https://github.com/jdabid/microservices-cicd-platform/pull/8) | 2026-03-06 |
| US-06 | Completar feature patients/ con CRUD completo (CQRS) | 5 | PENDIENTE | — | — | — |
| US-07 | Tests unitarios para patients/ (minimo 8 tests) | 3 | PENDIENTE | — | — | — |
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

---

## Sprint 2 — Testing y Calidad

**Sprint Goal:** Alcanzar >80% de coverage con tests de integracion y pipeline CI reportando calidad.
**Duracion:** Semana 3-4
**Estado:** NO INICIADO
**SP Completados:** 0/21

```
Sprint 2: [______________________________________] 0%  (0/21 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-14 | Tests de integracion con TestClient para appointments/ | 5 | PENDIENTE | — | — | — |
| US-15 | Tests de integracion con TestClient para patients/ | 3 | PENDIENTE | — | — | — |
| US-16 | Tests de integracion para auth/ | 3 | PENDIENTE | — | — | — |
| US-17 | pytest-cov con threshold minimo 80% y reporte HTML | 2 | PENDIENTE | — | — | — |
| US-18 | Pre-commit hooks con black, ruff, mypy | 3 | PENDIENTE | — | — | — |
| US-19 | Coverage badge en CI y README actualizado | 1 | PENDIENTE | — | — | — |
| US-20 | Agregar bandit al pipeline CI | 2 | PENDIENTE | — | — | — |
| US-21 | Tests para Celery tasks (email, notification) | 2 | PENDIENTE | — | — | — |

### Notas del Sprint 2
_(sin notas aun)_

---

## Sprint 3 — Infrastructure as Code (Terraform)

**Sprint Goal:** Infraestructura como codigo funcional que puede provisionar un ambiente completo en AWS.
**Duracion:** Semana 5-6
**Estado:** NO INICIADO
**SP Completados:** 0/21

```
Sprint 3: [______________________________________] 0%  (0/21 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-22 | Estructura base Terraform con providers y backend remoto (S3 + DynamoDB) | 3 | PENDIENTE | — | — | — |
| US-23 | Modulo VPC con subnets publicas/privadas, NAT gateway | 5 | PENDIENTE | — | — | — |
| US-24 | Modulo EKS con cluster, node group, IAM roles | 5 | PENDIENTE | — | — | — |
| US-25 | Modulo RDS para PostgreSQL con subnet group | 3 | PENDIENTE | — | — | — |
| US-26 | Modulo ElastiCache para Redis con subnet group | 3 | PENDIENTE | — | — | — |
| US-27 | tfvars para ambientes dev y prod diferenciados | 1 | PENDIENTE | — | — | — |
| US-28 | Documentacion de infraestructura con diagrama de red | 1 | PENDIENTE | — | — | — |

### Notas del Sprint 3
_(sin notas aun)_

---

## Sprint 4 — Monitoreo y Observabilidad

**Sprint Goal:** Monitoreo funcional con Prometheus, Grafana, logging estructurado y alertas basicas.
**Duracion:** Semana 7-8
**Estado:** NO INICIADO
**SP Completados:** 0/22

```
Sprint 4: [______________________________________] 0%  (0/22 SP)
```

| ID | User Story | SP | Estado | Branch | PR | Fecha |
|----|------------|----|---------|---------|----|-------|
| US-29 | Configuracion Prometheus con scrape configs | 3 | PENDIENTE | — | — | — |
| US-30 | Docker-compose para stack de monitoreo | 3 | PENDIENTE | — | — | — |
| US-31 | Dashboard Grafana para backend-api (request rate, latency, errors) | 5 | PENDIENTE | — | — | — |
| US-32 | Dashboard Grafana para infraestructura (CPU, memoria, disco) | 3 | PENDIENTE | — | — | — |
| US-33 | Alertmanager con reglas basicas | 3 | PENDIENTE | — | — | — |
| US-34 | Structured logging con python-json-logger y correlation IDs | 3 | PENDIENTE | — | — | — |
| US-35 | Manifiestos K8s para Prometheus y Grafana | 2 | PENDIENTE | — | — | — |

### Notas del Sprint 4
_(sin notas aun)_

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
  136 |
      |
  125 |
      |
  115 |
      |
  113 |   *  <- actual (11 US completadas, 23 SP)
      |
  120 |
      |
  104 |
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
