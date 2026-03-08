# Sprint 5 — Errores y Lecciones Aprendidas

> Registro de errores, problemas y soluciones encontrados durante el desarrollo del Sprint 5.
> Sprint 5: Seguridad y Hardening | 7 US | 20 SP | PR #23

---

## Error 1: Worktree del Agent 1 (Trivy) auto-limpiado

**Contexto:** Se lanzaron 3 agents en worktree isolation. El Agent 1 (US-36, Trivy CI) edito el archivo `.github/workflows/ci.yml` para agregar el job `container-scan`.

**Error:** Al momento de consolidar archivos de los 3 worktrees, el directorio del Agent 1 (`.claude/worktrees/agent-a5beed57`) ya no existia. Habia sido auto-limpiado por Claude Code.

**Impacto:** El primer intento de copia fallo con:
```
cp: .claude/worktrees/agent-a5beed57/.github/workflows/ci.yml: No such file or directory
```

**Solucion:** Al verificar el `ci.yml` en el repo principal, se descubrio que el cambio ya estaba presente. El Agent 1 habia editado el archivo directamente (no creo un archivo nuevo), y como los worktrees comparten el mismo repositorio git subyacente, la edicion persisitio en el archivo original incluso despues de que el worktree fue limpiado.

**Leccion:** Los worktrees que solo EDITAN archivos existentes (sin crear nuevos) pueden ser auto-limpiados sin perder cambios, ya que las ediciones se aplican al archivo compartido. Sin embargo, los worktrees que CREAN archivos nuevos si pierden esos archivos al ser limpiados. Diferenciar entre estos dos escenarios al planificar la recuperacion de archivos.

---

## Error 2: Primer intento de copia fallo por path incorrecto

**Contexto:** Al consolidar archivos de los worktrees de Agent 2 y Agent 3, se escribio un comando largo con multiples `cp` encadenados.

**Error:** El comando fallo con:
```
cp: kubernetes/security is not a directory
```
El `mkdir -p kubernetes/security` estaba dentro del mismo comando pero se ejecuto despues de que el primer `cp` fallara por la ausencia del worktree del Agent 1.

**Impacto:** El primer intento de consolidacion fallo completamente. Se tuvo que reintentar con un comando corregido.

**Solucion:** Separar el `mkdir -p` como prerequisito y usar `cp -r` con paths mas simples en lugar de paths con variables de shell complejas.

**Leccion:** Para consolidacion multi-worktree:
1. Verificar primero que los worktrees existen (`ls .claude/worktrees/`)
2. Crear TODOS los directorios destino antes de cualquier copia
3. Usar `cp -r` con paths simples en lugar de encadenar multiples `cp` individuales
4. Dividir en comandos separados: mkdir → cp worktree1 → cp worktree2 → cp worktree3

---

## Error 3: SecurityContext requiere UIDs especificos por servicio

**Contexto:** El Agent 2 (US-37) debia agregar `securityContext` a todos los pods de Kubernetes.

**Error:** No todos los servicios pueden usar el mismo `runAsUser: 1000`. Cada servicio tiene su propio UID esperado:
- PostgreSQL: UID 999
- Redis: UID 999
- Prometheus: UID 65534 (nobody)
- Grafana: UID 472
- Alertmanager: UID 65534 (nobody)
- Backend/Frontend: UID 1000

**Impacto:** El prompt del agent tuvo que especificar los UIDs correctos para cada servicio. Si se hubiera usado un UID generico, los pods fallarian al iniciar con errores de permisos de filesystem.

**Solucion:** Especificar los UIDs correctos en el prompt del agent para cada tipo de servicio, basandose en las imagenes Docker oficiales de cada componente.

**Leccion:** Al hardening de seguridad en Kubernetes, investigar el UID esperado por cada imagen Docker oficial ANTES de aplicar `securityContext`. Los UIDs mas comunes:
- PostgreSQL/Redis: 999
- Prometheus/Alertmanager: 65534 (nobody)
- Grafana: 472
- Custom apps: 1000 (appuser)

---

## Error 4: Deployments de aplicacion no existian previamente

**Contexto:** El Agent 2 (US-37) debia EDITAR los deployments existentes para agregar `securityContext`.

**Error:** Los deployments de aplicacion (backend-api, backend-worker, postgres, redis, frontend) no existian como archivos YAML individuales en `kubernetes/`. Solo existian los deployments de monitoring en `kubernetes/monitoring/`. El agent tuvo que CREAR estos archivos desde cero en lugar de editarlos.

**Impacto:** Se crearon 6 archivos nuevos de deployment (backend-api, backend-worker, postgres, redis, frontend, namespace) ademas de editar los 3 existentes de monitoring. Mas trabajo del esperado.

**Solucion:** El agent creo deployments completos con todos los requisitos del CLAUDE.md: securityContext, resource limits, probes, namespace. Esto resulto beneficioso ya que los deployments quedaron correctamente configurados desde el inicio.

**Leccion:** Antes de asignar tareas de "editar archivos existentes" a un agent, verificar que los archivos realmente existen. Incluir en el prompt: "If files don't exist, CREATE them with full configuration".

---

## Error 5: Network Policies requieren conocimiento del flujo de trafico

**Contexto:** El Agent 3 (US-38) debia crear NetworkPolicies para aislar trafico entre servicios.

**Error:** No es un error per se, pero crear NetworkPolicies correctas requiere un modelo mental completo del flujo de trafico entre servicios:
- Que servicio habla con que otro
- En que puertos
- Si necesita egress a DNS (puerto 53 UDP+TCP)
- Si necesita egress a servicios externos (SMTP puerto 587)
- Si el monitoring namespace necesita acceso cross-namespace

**Impacto:** Las NetworkPolicies fueron generadas correctamente gracias a un prompt detallado, pero un prompt generico habria producido policies incorrectas que bloquearian trafico legitimo.

**Solucion:** Especificar en el prompt EXACTAMENTE que servicios se comunican, en que direccion, y en que puertos. Incluir los casos especiales (DNS, SMTP, monitoring cross-namespace).

**Leccion:** Para NetworkPolicies zero-trust:
1. Mapear TODOS los flujos de trafico antes de escribir policies
2. SIEMPRE incluir egress a DNS (53 UDP+TCP) para pods que resuelven nombres
3. Considerar trafico cross-namespace (monitoring → app pods)
4. Implementar default-deny PRIMERO, luego allow explicitos
5. Probar en un entorno de staging antes de produccion

---

## Resumen de Metricas de Errores

| Metrica | Valor |
|---------|-------|
| Total errores registrados | 5 |
| Errores por worktree auto-limpiado | 1 (Error 1) |
| Errores por consolidacion multi-worktree | 1 (Error 2) |
| Errores por conocimiento de dominio | 2 (Error 3, 5) |
| Errores por suposiciones incorrectas | 1 (Error 4) |
| Trabajo perdido | 0 (quinto sprint consecutivo sin perdida) |

---

## Mejoras Aplicadas para Sprints Futuros

1. **Verificar existencia de worktrees** antes de intentar copiar archivos
2. **Diferenciar ediciones vs creaciones** — los edits sobreviven la limpieza de worktrees, las creaciones no
3. **Investigar UIDs de imagenes Docker** antes de aplicar securityContext
4. **Verificar que los archivos destino existen** antes de asignar tareas de edicion
5. **Mapear flujos de trafico** antes de crear NetworkPolicies
6. **Simplificar comandos de copia** — paths simples, `cp -r`, dividir en pasos

---

## Tendencia de Errores por Sprint

| Sprint | Errores | Trabajo perdido | Consolidacion |
|--------|---------|-----------------|---------------|
| Sprint 1 | 8 | 2 US reimplementadas | N/A |
| Sprint 2 | 4 | 0 | N/A |
| Sprint 3 | 5 | 0 | ~5 min |
| Sprint 4 | 5 | 0 | ~3 min |
| Sprint 5 | 5 | 0 | ~4 min (worktree auto-limpiado) |
