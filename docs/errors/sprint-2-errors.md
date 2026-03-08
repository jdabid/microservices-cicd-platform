# Sprint 2 — Errores y Lecciones Aprendidas

> Registro de errores, problemas y soluciones encontrados durante el desarrollo del Sprint 2.
> Sprint 2: Testing y Calidad | 8 US | 21 SP | PRs #17–#20

---

## Error 1: Tracker desactualizado — 5 US completadas sin registrar

**Contexto:** Al iniciar el trabajo en Sprint 2, se descubrio que el tracker `cronograma-sprints.md` mostraba Sprint 2 como "NO INICIADO" con 0/21 SP y todas las US como PENDIENTE.

**Error:** US-14, US-15, US-16, US-17 y US-18 ya estaban completadas y mergeadas en main (PRs #17, #18, commit `67db4ed`), pero el tracker no reflejaba estos cambios. El diagnostico revelo que 5 de 8 US estaban DONE sin documentar.

**Impacto:** Desalineacion entre el estado real del repo y la documentacion. Metricas globales incorrectas (mostraba 31 SP completados cuando eran 47). Sprint 2 aparecia al 0% cuando realmente estaba al 76%.

**Solucion:**
1. Ejecutar un Agent tipo Explore para auditar el estado real vs el tracker
2. Cruzar `git log --oneline main` con las US del tracker
3. Actualizar todas las metricas: 18 US completadas, 47/136 SP, Sprint 2 EN PROGRESO
4. Marcar US-14 a US-18 como DONE con sus PRs y fechas correspondientes

**Leccion:** Ejecutar `/update-sprint-tracker` inmediatamente despues de cada merge de PR. No delegar la actualizacion a una sesion futura. Implementar un check de consistencia: comparar `git log` con el tracker antes de iniciar trabajo nuevo.

---

## Error 2: Agents en worktree no pueden ejecutar Bash (recurrente)

**Contexto:** Se lanzaron 2 agents en worktree isolation para US-19+US-20 (CI pipeline) y US-21 (Celery tests).

**Error:** Ambos agents completaron la escritura de archivos pero no pudieron ejecutar operaciones git (branch, commit, push, PR). El Agent 1 devolvio las instrucciones bash como texto en su resultado. El Agent 2 solicito permisos de Bash que no tenia.

**Impacto:** Las operaciones git tuvieron que completarse manualmente desde el contexto principal para ambos agents.

**Solucion:**
1. Leer los archivos creados en los worktrees para verificar calidad
2. Navegar al directorio del worktree con `cd` en Bash
3. Ejecutar `git checkout -b`, `git add`, `git commit`, `git push`, `gh pr create` desde el contexto principal
4. Para el Agent 1 (US-19+20): PR #19 creada y mergeada
5. Para el Agent 2 (US-21): PR #20 creada y mergeada

**Leccion:** Este error es recurrente desde Sprint 1 (Error 1, 2, 7). La solucion establecida funciona: agents crean archivos, el contexto principal maneja git. No intentar que los agents hagan git — aceptar esta limitacion y planificar en consecuencia.

---

## Error 3: tfvars bloqueados por .gitignore

**Contexto:** Durante Sprint 3 (registrado aqui por proximidad temporal), al intentar hacer `git add terraform/environments/dev.tfvars` y `prod.tfvars`.

**Error:**
```
The following paths are ignored by one of your .gitignore files:
terraform/environments/dev.tfvars
terraform/environments/prod.tfvars
```
El `.gitignore` del proyecto incluye `*.tfvars` como patron para prevenir commit de archivos con variables sensibles.

**Impacto:** Los archivos de configuracion de ambientes no podian ser commiteados normalmente.

**Solucion:** Usar `git add -f` (force) para agregar los tfvars, ya que estos archivos de ejemplo no contienen secretos reales — solo configuracion de tamano de instancias y CIDRs.

**Leccion:** Considerar separar los tfvars de ejemplo (sin secretos) de los tfvars reales. Opciones: (a) renombrar a `.tfvars.example`, (b) agregar una excepcion en `.gitignore` con `!terraform/environments/*.tfvars`, o (c) documentar que se requiere `git add -f` para estos archivos.

---

## Error 4: Branch US-17 sin PR formal

**Contexto:** US-17 (pytest-cov threshold 80%) fue commiteada directamente en main sin pasar por una PR.

**Error:** El commit `67db4ed` aparece directamente en main sin merge commit ni PR asociada. Esto rompe el patron establecido donde cada US tiene su PR documentada.

**Impacto:** En el tracker, US-17 aparece con `PR: —` mientras todas las demas US tienen su PR. Inconsistencia en la trazabilidad del trabajo.

**Solucion:** Se documento la US-17 sin PR en el tracker. El trabajo esta en main y es funcional.

**Leccion:** Siempre crear PR incluso para cambios pequenos (2 SP). Mantener consistencia en el flujo git-flow: branch → commit → push → PR → merge. Usar `/finish-user-story` para automatizar este proceso.

---

## Resumen de Metricas de Errores

| Metrica | Valor |
|---------|-------|
| Total errores registrados | 4 |
| Errores por documentacion/tracking | 2 (Error 1, 4) |
| Errores por permisos de agents | 1 (Error 2 - recurrente) |
| Errores por configuracion git | 1 (Error 3) |
| Trabajo perdido | 0 (mejora vs Sprint 1) |
| Agents que no pudieron commitear | 2 de 2 (100% - consistente) |

---

## Mejoras Aplicadas para Sprints Futuros

1. **Actualizar tracker inmediatamente** despues de cada merge — no posponer
2. **Aceptar limitacion de Bash en agents** — planificar git operations en contexto principal
3. **Revisar .gitignore** antes de agregar archivos nuevos de configuracion
4. **Siempre crear PR** para cada US, sin excepciones
5. **Diagnosticar tracker** al inicio de cada sesion — cruzar `git log` con estado documentado
