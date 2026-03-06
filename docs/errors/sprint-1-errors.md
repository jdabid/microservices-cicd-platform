# Sprint 1 — Errores y Lecciones Aprendidas

> Registro de errores, problemas y soluciones encontrados durante el desarrollo del Sprint 1.
> Sprint 1: Limpieza y Credibilidad | 13 US | 31 SP | PRs #6–#16

---

## Error 1: Agents en worktree no pueden ejecutar Bash

**Contexto:** Se lanzaron agents en worktree isolation para US-04 (JWT auth) y US-05 (exception handling) en paralelo.

**Error:** Los agents completaron la escritura de archivos pero no pudieron ejecutar `git add` ni `git commit` porque la herramienta Bash estaba restringida por permisos del usuario en el modo de ejecucion de agents.

**Impacto:** Los agents terminaron sin commitear su trabajo. Los cambios quedaron como archivos sin trackear en los worktrees.

**Solucion:**
1. Verificar manualmente que los archivos existen en el worktree con `git status`
2. Copiar los archivos desde el worktree al repositorio principal
3. Crear el branch, hacer commit y push desde el contexto principal

**Leccion:** Incluir en el prompt del agent la instruccion explicita: _"You MUST commit your work with git add and git commit before finishing"_. Aun asi, si el usuario no otorga permisos de Bash al agent, este no podra commitear. Tener un plan B de copia manual.

---

## Error 2: Worktree auto-limpiado antes de recuperar cambios

**Contexto:** El primer agent de US-04 escribio 17 archivos (676 lineas) de auth feature completo.

**Error:** El directorio del worktree fue eliminado automaticamente por Claude Code antes de que se pudieran recuperar los archivos. Los cambios no commiteados se perdieron.

**Impacto:** Se perdio todo el trabajo del primer agent de US-04. Hubo que relanzar un segundo agent.

**Solucion:**
1. Relanzar un segundo agent con instrucciones mas explicitas
2. El segundo agent logro hacer commit (SHA `96c1d19`)
3. Se uso `git cherry-pick 96c1d19` para traer el commit al branch real

**Leccion:** Recuperar archivos del worktree inmediatamente despues de que el agent termine. No asumir que el worktree persistira. Si el agent no commiteo, copiar archivos antes de que el worktree sea limpiado.

---

## Error 3: Conflicto de branch con worktree activo

**Contexto:** Intentar eliminar un branch que todavia estaba asociado a un worktree.

**Error:**
```
error: Cannot delete branch 'worktree-agent-xxx' checked out at '/path/to/worktree'
```
`git branch -D` fallo porque el worktree aun referenciaba el branch.

**Solucion:**
```bash
git worktree remove --force /path/to/worktree
git worktree prune
git branch -D worktree-agent-xxx
```

**Leccion:** Siempre remover el worktree primero con `--force`, luego `prune`, y finalmente eliminar el branch.

---

## Error 4: Archivos de evaluacion perdidos al cambiar de branch

**Contexto:** Se crearon documentos de evaluacion (CLAUDE.md, cronogramas, commands) mientras se estaba en el branch `feature/patients-crud`.

**Error:** Al hacer `git checkout main`, los archivos no commiteados en el branch anterior se perdieron. El stash solo contenia cambios de patients-crud, no los documentos de evaluacion.

**Impacto:** Se tuvo que recrear todos los archivos de evaluacion, commands y configuracion desde el contexto de la conversacion.

**Solucion:** Recrear manualmente todos los archivos usando la informacion disponible en el historial de la conversacion.

**Leccion:** Commitear o hacer stash de archivos importantes ANTES de cambiar de branch. Nunca asumir que archivos no trackeados sobreviviran un checkout.

---

## Error 5: `git worktree remove` falla con "not a working tree"

**Contexto:** Intentar limpiar worktrees despues de que Claude Code ya habia eliminado el directorio.

**Error:**
```
fatal: '/path/to/worktree' is not a working tree
```
El directorio del worktree ya no existia pero git aun lo tenia registrado.

**Solucion:**
```bash
git worktree prune  # Limpia referencias a worktrees que ya no existen
```

**Leccion:** Usar `git worktree prune` como primer paso de limpieza. Verificar `git worktree list` antes de intentar `remove`.

---

## Error 6: Dependencia no detectada entre US

**Contexto:** Se intento ejecutar US-07 (tests para patients/) en paralelo con US-08, US-09, US-10, US-11.

**Error:** US-07 requiere que el codigo de patients/ exista (US-06), pero US-06 aun no estaba implementada. El directorio `backend-api/app/features/patients/` no existia en main.

**Impacto:** US-07 no podia ejecutarse. Se tuvo que posponer hasta despues de completar US-06.

**Solucion:**
1. Saltar US-07 del batch paralelo
2. Implementar US-06 primero
3. Ejecutar US-06 y US-07 juntas en un solo branch (`feature/s1-US06-to-US07-patients-crud`)

**Leccion:** Antes de lanzar agents en paralelo, verificar dependencias entre US. Si una US produce codigo que otra necesita, deben ejecutarse secuencialmente o en el mismo branch.

---

## Error 7: Segundo batch de agents tampoco pudo commitear

**Contexto:** Se lanzaron 4 agents en worktree para US-08, US-09, US-10, US-11.

**Error:** Los 4 agents completaron ediciones de archivos pero ninguno pudo ejecutar `git commit`. Dos worktrees (US-08, US-09) fueron limpiados automaticamente antes de recuperar cambios. Dos worktrees (US-10, US-11) persistieron con cambios sin commitear.

**Impacto:**
- US-10 y US-11: se copiaron los cambios desde los worktrees
- US-08 y US-09: se reimplementaron directamente (eran cambios simples)

**Solucion:** Implementar todo directamente desde el contexto principal sin agents, ya que los agents no podian usar Bash.

**Leccion:** Si los agents no tienen permisos de Bash, es mas eficiente implementar directamente. Reservar agents en worktree para cuando se confirme que tienen permisos completos.

---

## Error 8: Sprint 1 suma 31 SP, no 32 SP

**Contexto:** El cronograma original asigna 32 SP al Sprint 1.

**Error:** La suma real de las 13 US es: 1+1+1+5+3+5+3+1+3+3+3+1+1 = **31 SP**, no 32 SP. Hay un SP de diferencia con el valor documentado en el Sprint Goal.

**Impacto:** Menor. El tracker muestra 31/32 SP (97%) aunque todas las US estan DONE.

**Solucion:** Se documento la discrepancia en las notas. No se modifico el total del Sprint para mantener consistencia con el cronograma original.

**Leccion:** Verificar que la suma de SP de las US coincida con el total asignado al Sprint al momento de planificar.

---

## Resumen de Metricas de Errores

| Metrica | Valor |
|---------|-------|
| Total errores registrados | 8 |
| Errores por permisos de agents | 3 (Error 1, 2, 7) |
| Errores por git/worktree | 3 (Error 3, 4, 5) |
| Errores por planificacion | 2 (Error 6, 8) |
| Trabajo perdido y recreado | US-04 primer intento, archivos evaluacion |
| Agents que no pudieron commitear | 6 de 6 (100%) |

---

## Mejoras Aplicadas para Sprints Futuros

1. **No usar agents en worktree** salvo que se confirme permisos de Bash — implementar directamente es mas rapido y confiable
2. **Verificar dependencias** entre US antes de paralelizar
3. **Commitear frecuentemente** — nunca dejar archivos importantes sin trackear
4. **Limpiar worktrees inmediatamente** despues de recuperar cambios
5. **Validar sumas de SP** contra el total del Sprint al planificar
