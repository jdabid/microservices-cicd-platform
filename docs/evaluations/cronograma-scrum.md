# Cronograma Scrum: Microservices CI/CD Platform

> Metodologia Scrum adaptada para desarrollador individual.
> Sprints de 2 semanas | 6 Sprints | 12 semanas totales.

---

## Roles Scrum (Adaptados)

| Rol | Responsable |
|-----|-------------|
| Product Owner | Tu (defines prioridades del portafolio) |
| Scrum Master | Tu (facilitas tu propio proceso) |
| Development Team | Tu (ejecutas el trabajo) |

---

## Product Backlog (Epicas)

| ID | Epica | Prioridad | Story Points Totales |
|----|-------|-----------|---------------------|
| E1 | Limpieza del Repositorio + Auth + Exception Handling | Critica | 32 |
| E2 | Testing y Calidad de Codigo | Critica | 21 |
| E3 | Infrastructure as Code (Terraform) | Alta | 21 |
| E4 | Monitoreo y Observabilidad | Alta | 22 |
| E5 | Seguridad y Hardening | Alta | 20 |
| E6 | GitOps + Helm + Documentacion | Media | 20 |

**Velocidad estimada:** 20-22 story points por sprint.
**Total:** 136 Story Points | 50 User Stories | 6 Sprints | 12 Semanas

---

## Sprint 1 — Limpieza y Credibilidad (Semana 1-2, 32 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-01 | Actualizar .gitignore y limpiar archivos del tracking | 1 | .gitignore actualizado, archivos removidos con git rm --cached |
| US-02 | Eliminar .env del repositorio, verificar .env.example | 1 | Solo .env.example en el repo |
| US-03 | Eliminar archivos innecesarios (.backup, .corrupted, main.py raiz) | 1 | Archivos eliminados |
| US-04 | Login y JWT para acceder a la API | 5 | /auth/login, /auth/register, /auth/me funcionales con JWT |
| US-05 | Sistema de excepciones centralizado | 3 | JSON estructurado: status_code, message, detail |
| US-06 | Completar feature patients/ CRUD (CQRS) | 5 | create, read, update, delete funcionales |
| US-07 | Tests unitarios para patients/ | 3 | Minimo 8 tests |
| US-08 | Corregir strings hardcodeados por enums | 1 | AppointmentStatus enum usado |
| US-09 | CORS por ambiente y rate limiting en auth | 3 | No wildcards en prod, 5 req/min en login |
| US-10 | Configurar ruff y mypy | 3 | Pasan sin errores criticos |
| US-11 | Reemplazar psycopg2-binary por asyncpg | 3 | Async DB funcional |
| US-12 | Corregir time.sleep() y datetime sin timezone | 1 | UTC en todos los datetimes |
| US-13 | Corregir typos en Dockerfiles | 1 | Emails correctos en LABEL |

## Sprint 2 — Testing y Calidad (Semana 3-4, 21 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-14 | Tests integracion appointments/ | 5 | 6+ tests con TestClient |
| US-15 | Tests integracion patients/ | 3 | 4+ tests con TestClient |
| US-16 | Tests integracion auth/ | 3 | Login, token, protected routes |
| US-17 | pytest-cov threshold 80% | 2 | --cov-fail-under=80 pasa |
| US-18 | Pre-commit hooks (black, ruff, mypy) | 3 | .pre-commit-config.yaml funcional |
| US-19 | Coverage badge en CI | 1 | Badge real en README |
| US-20 | Bandit en pipeline CI | 2 | Sin vulnerabilidades criticas |
| US-21 | Tests para Celery tasks | 2 | Tasks se encolan correctamente |

## Sprint 3 — Terraform (Semana 5-6, 21 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-22 | Estructura base Terraform + backend remoto | 3 | terraform init exitoso |
| US-23 | Modulo VPC | 5 | terraform plan genera VPC con 2 AZs |
| US-24 | Modulo EKS | 5 | terraform plan genera cluster |
| US-25 | Modulo RDS | 3 | PostgreSQL en subnet privada |
| US-26 | Modulo ElastiCache | 3 | Redis en subnet privada |
| US-27 | tfvars por ambiente | 1 | dev.tfvars y prod.tfvars |
| US-28 | Documentacion infra | 1 | Diagrama de red |

## Sprint 4 — Monitoreo (Semana 7-8, 22 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-29 | Prometheus config | 3 | Scrapea /metrics |
| US-30 | Docker-compose monitoring | 3 | Prometheus + Grafana levantan |
| US-31 | Dashboard Grafana backend-api | 5 | Request rate, latency, errors |
| US-32 | Dashboard Grafana infra | 3 | CPU, memoria, disco |
| US-33 | Alertmanager | 3 | Error rate >5%, latency >2s |
| US-34 | Structured logging + correlation IDs | 3 | JSON logs con request_id |
| US-35 | K8s manifests monitoring | 2 | Deployments para Prometheus/Grafana |

## Sprint 5 — Seguridad (Semana 9-10, 20 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-36 | Trivy en CI/CD | 3 | Falla en HIGH/CRITICAL |
| US-37 | SecurityContext en pods | 3 | runAsNonRoot, drop ALL |
| US-38 | Network Policies | 5 | Trafico aislado entre servicios |
| US-39 | TLS en Ingress | 3 | cert-manager configurado |
| US-40 | RBAC K8s | 2 | ServiceAccount por servicio |
| US-41 | PodDisruptionBudget | 2 | minAvailable: 1 |
| US-42 | Sealed Secrets | 2 | No plaintext en repo |

## Sprint 6 — GitOps y Deploy (Semana 11-12, 20 SP)

| ID | User Story | SP | Criterio de Aceptacion |
|----|------------|----|-----------------------|
| US-43 | Helm chart completo | 5 | helm lint y helm template pasan |
| US-44 | ArgoCD manifest | 3 | Sync policy definido |
| US-45 | CD workflow GitHub Actions | 3 | Staging auto, prod con approval |
| US-46 | README con badges reales | 3 | Build, coverage, license |
| US-47 | 3 ADRs | 2 | CQRS, Terraform, monitoring |
| US-48 | ARCHITECTURE.md | 2 | Diagramas reales |
| US-49 | Revision final | 1 | CI verde, coverage 80%, repo limpio |
| US-50 | Video demo LinkedIn | 1 | 3-5 min demo |

---

## Definition of Done (Global)

- [ ] Codigo funcional sin errores
- [ ] Ruff y mypy pasan sin warnings
- [ ] Tests escritos y pasando
- [ ] Documentacion actualizada si aplica
- [ ] Commit con conventional commits
- [ ] PR creado y revisado

---

## Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Subestimar complejidad de Terraform | Alta | Alto | Empezar con modulo VPC simple |
| Perder motivacion | Media | Alto | Celebrar cada Sprint Review en LinkedIn |
| Sin cuenta AWS | Media | Medio | terraform plan + LocalStack |
| Scope creep | Media | Medio | Limitar a lo definido |
