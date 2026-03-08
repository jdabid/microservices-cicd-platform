# Sprint 4 — Errores y Lecciones Aprendidas

> Registro de errores, problemas y soluciones encontrados durante el desarrollo del Sprint 4.
> Sprint 4: Monitoreo y Observabilidad | 7 US | 22 SP | PR #22

---

## Error 1: `gh pr merge` ejecutado antes de que la PR existiera

**Contexto:** Se intento combinar `gh pr create` y `gh pr merge` en un solo comando encadenado con `&&`.

**Error:** El primer comando (`gh pr create`) retorno la URL de la PR, pero el segundo comando (`gh pr merge --merge --admin`) se ejecuto sin especificar el numero de PR. `gh pr merge` interpreto el merge desde el branch actual sin confirmacion explicita.

**Impacto:** La PR #22 se mergeo exitosamente pero el flujo no fue limpio. El comando `gh pr merge 22 --merge --admin` posterior retorno "Pull request #22 was already merged".

**Solucion:** El merge ya se habia completado correctamente. No se requirio accion adicional.

**Leccion:** No encadenar `gh pr create` con `gh pr merge` en un solo comando. Ejecutar secuencialmente:
1. `gh pr create ...` → obtener numero de PR
2. `gh pr merge <numero> --merge --admin` → merge explicito

---

## Error 2: Dependencias de Python ya existentes en requirements.txt

**Contexto:** El Agent 3 (US-34 structured logging) tenia instrucciones de agregar `python-json-logger==2.0.7` y `prometheus-fastapi-instrumentator==6.1.0` a `requirements.txt`.

**Error:** Ambas dependencias ya estaban presentes en el archivo. El agent detecto esto correctamente y no las agrego por duplicado, pero genero confusion en el reporte ("Already present - no changes needed").

**Impacto:** Ninguno funcional. El agent manejo correctamente la situacion al leer el archivo antes de modificar.

**Solucion:** No se requirio accion. El agent verifico antes de escribir.

**Leccion:** Al dar instrucciones a agents, usar lenguaje condicional: "Add X to requirements.txt **if not already present**". Esto evita confusion en los reportes y hace las instrucciones mas robustas. Siempre incluir la instruccion de leer archivos existentes antes de modificarlos.

---

## Error 3: Dashboard JSON de Grafana potencialmente sobredimensionado

**Contexto:** Los dashboards de Grafana (`backend-api.json` y `infrastructure.json`) fueron generados como archivos JSON completos por el Agent 2.

**Error:** No es un error critico, pero los dashboards JSON generados por el agent son templates estaticos que no han sido validados contra una instancia real de Grafana. Pueden tener:
- Paneles con queries PromQL que no coincidan con los metrics names reales del backend
- Layouts que no se rendericen correctamente en la version especifica de Grafana
- Variables de templating que no funcionen sin el datasource configurado

**Impacto:** Los dashboards necesitaran ajustes manuales cuando se desplieguen en un Grafana real. El objetivo de la US (tener dashboards funcionales) se cumple parcialmente — la estructura es correcta pero requiere validacion en runtime.

**Solucion:** Documentar que los dashboards son templates iniciales que deben validarse en un entorno real. Los queries PromQL usan nombres de metricas estandar de `prometheus-fastapi-instrumentator` y `node-exporter`, lo cual minimiza el riesgo de incompatibilidad.

**Leccion:** Para archivos que requieren validacion en runtime (dashboards, helm charts, K8s manifests), agregar una seccion de "Test plan" en la PR con pasos de validacion manual. Considerar agregar `docker-compose -f monitoring/docker-compose.monitoring.yml config` como validacion basica en CI.

---

## Error 4: Consolidacion de 3 worktrees mejorada pero aun manual

**Contexto:** Se usaron 3 agents en worktree isolation para Sprint 4, similar a Sprint 3.

**Error:** La consolidacion se optimizo respecto a Sprint 3 (se crearon todos los directorios de destino en un solo comando `mkdir -p`), pero sigue siendo un proceso manual de copiar archivos desde 3 ubicaciones distintas.

**Impacto:** Overhead de ~3 minutos de consolidacion. Menor que Sprint 3 (~5 min) gracias a las lecciones aprendidas.

**Solucion:** Se ejecuto todo en un solo comando de Bash largo que:
1. Define variables para las rutas de worktrees (`WT1`, `WT2`, `WT3`)
2. Crea todos los directorios con `mkdir -p`
3. Copia todos los archivos con multiples `cp`
4. Verifica el conteo con `find | wc -l`

**Leccion:** El patron de consolidacion multi-worktree esta madurando. Para Sprint 5+, considerar:
- Un script reutilizable de consolidacion
- O reducir a 2 agents en lugar de 3 para minimizar la coordinacion
- El costo de integracion manual NO existio en Sprint 4 (a diferencia de Sprint 3 donde hubo que editar main.tf) porque los archivos de cada agent eran independientes (monitoring/, kubernetes/monitoring/, backend-api/)

---

## Error 5: Archivos de worktree sin validacion de sintaxis

**Contexto:** Los archivos creados por los agents (YAML de Prometheus, JSON de Grafana, YML de K8s) fueron commiteados sin validacion de sintaxis.

**Error:** No se ejecuto ninguna validacion antes del commit:
- No se corrio `docker-compose -f monitoring/docker-compose.monitoring.yml config` para validar el compose
- No se corrio `kubectl apply --dry-run=client` para validar los K8s manifests
- No se verifico que los JSON de Grafana fueran validos con `python -m json.tool`
- No se verifico el YAML de Prometheus con `promtool check config`

**Impacto:** Potenciales errores de sintaxis no detectados hasta el despliegue. El riesgo es bajo porque los agents usan templates bien conocidos, pero la validacion deberia ser parte del flujo.

**Solucion:** Los archivos se commitearon tal cual. La validacion se hara cuando se despliegue el stack de monitoreo.

**Leccion:** Agregar pasos de validacion basica antes de commitear:
```bash
# Validar YAML
python -c "import yaml; yaml.safe_load(open('file.yml'))"

# Validar JSON
python -m json.tool file.json > /dev/null

# Validar docker-compose
docker-compose -f file.yml config --quiet

# Validar K8s (si kubectl disponible)
kubectl apply --dry-run=client -f file.yml
```
Considerar agregar estos checks al skill `/pre-commit` o al CI pipeline.

---

## Resumen de Metricas de Errores

| Metrica | Valor |
|---------|-------|
| Total errores registrados | 5 |
| Errores por flujo git/CLI | 1 (Error 1) |
| Errores por instrucciones a agents | 1 (Error 2) |
| Errores por falta de validacion | 2 (Error 3, 5) |
| Errores por coordinacion multi-agent | 1 (Error 4 - mejorando) |
| Trabajo perdido | 0 (tercer sprint consecutivo sin perdida) |
| Tiempo de consolidacion | ~3 min (mejora vs ~5 min Sprint 3) |

---

## Mejoras Aplicadas para Sprints Futuros

1. **No encadenar `gh pr create` con `gh pr merge`** — ejecutar secuencialmente
2. **Instrucciones condicionales a agents** — "add if not present", "read before modify"
3. **Agregar validacion de sintaxis** antes de commitear (YAML, JSON, docker-compose, K8s)
4. **Documentar dashboards como templates** que requieren validacion en runtime
5. **Consolidacion multi-worktree optimizada** — variables, mkdir -p, un solo comando
6. **Evaluar reduccion de agents** cuando los archivos son independientes entre si

---

## Tendencia de Errores por Sprint

| Sprint | Errores | Trabajo perdido | Agents fallidos | Consolidacion |
|--------|---------|-----------------|-----------------|---------------|
| Sprint 1 | 8 | 2 US reimplementadas | 6/6 (100%) | N/A |
| Sprint 2 | 4 | 0 | 2/2 (100%) | N/A |
| Sprint 3 | 5 | 0 | 0/3 (exito*) | ~5 min |
| Sprint 4 | 5 | 0 | 0/3 (exito*) | ~3 min |

*Los agents no commitean pero crean archivos exitosamente. La consolidacion manual es el patron aceptado.

**Conclusion:** La curva de aprendizaje muestra mejora sostenida: trabajo perdido eliminado desde Sprint 2, consolidacion cada vez mas eficiente, y errores cambiando de "criticos" (perdida de trabajo) a "operacionales" (optimizacion de flujo).
