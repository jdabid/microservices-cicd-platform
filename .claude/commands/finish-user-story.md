Finaliza el flujo git de una User Story: commit, push, PR, merge, y actualiza el tracker.

Argumento: $ARGUMENTS (opcional - si no se da, infiere del branch actual)

## Steps

### 1. Determinar la US

Si se da argumento, usar ese ID. Si no, inferir del nombre del branch actual:
```bash
git branch --show-current
```
Extraer el US-XX del nombre del branch (e.g., `feature/s1-US04-jwt-auth` → `US-04`).

### 2. Leer el cronograma

Leer `docs/evaluations/cronograma-scrum.md` para obtener:
- Sprint number
- Descripcion corta
- Story Points
- Criterio de aceptacion

### 3. Verificar que hay cambios

```bash
git status
git diff --stat
```
Si no hay cambios, avisar al usuario y abortar.

### 4. Generar el commit message

Formato conventional commits:
```
{type}({scope}): {descripcion corta en ingles}

- Bullet point 1 de lo que se hizo
- Bullet point 2
- ...
- US-XX from Sprint N

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

Determinar el type:
- Nuevo feature/endpoint/modelo → `feat`
- Bug fix o correccion → `fix`
- Tests → `test`
- Documentacion → `docs`
- Config, limpieza, herramientas → `chore`
- Refactor sin cambio funcional → `refactor`

Determinar el scope del commit:
- Si toca auth/ → `auth`
- Si toca appointments/ → `appointments`
- Si toca patients/ → `patients`
- Si toca exceptions/ → `exceptions`
- Si toca Docker → `docker`
- Si toca K8s → `k8s`
- Si toca Terraform → `terraform`
- Si toca monitoring/ → `monitoring`
- Si toca CI/CD → `ci`
- Si toca varios → scope del mas importante

### 5. Stage y commit

```bash
git add {archivos_relevantes}
git commit -m "{mensaje generado con HEREDOC}"
```

IMPORTANTE: Usar git add con archivos especificos, NUNCA `git add -A` o `git add .`
IMPORTANTE: Usar HEREDOC para el commit message.

### 6. Push

```bash
git push -u origin {branch_name}
```

### 7. Crear PR

Formato EXACTO del PR:
```bash
gh pr create --title "{type}({scope}): {descripcion} ({US-ID})" --body "$(cat <<'EOF'
## Summary
- Bullet 1 de cambios principales
- Bullet 2
- Bullet 3

## User Story
**{US-ID}**: {descripcion completa de la US} ({SP} SP)

## Files Changed
- `path/to/file1` - descripcion corta
- `path/to/file2` - descripcion corta

## Test plan
- [ ] Check 1
- [ ] Check 2
- [ ] Check 3

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### 8. Merge

```bash
gh pr merge {PR_NUMBER} --merge --delete-branch
```

### 9. Volver a main

```bash
git checkout main
git pull origin main
```

### 10. Actualizar el tracker

Editar `docs/evaluations/cronograma-sprints.md`:

a) Actualizar la fila de la US:
   - Estado: `DONE`
   - Branch: `\`{branch_name}\``
   - PR: `[#{N}](https://github.com/jdabid/microservices-cicd-platform/pull/{N})`
   - Fecha: `{YYYY-MM-DD}`

b) Recalcular metricas del Sprint:
   - SP Completados: sumar todos los DONE del sprint
   - Barra de progreso: `[####____] XX%  (X/Y SP)` (38 chars, # = completado, _ = pendiente)
   - Si todas DONE → Estado del sprint = `COMPLETADO`

c) Recalcular metricas globales (Resumen General):
   - Completadas, En progreso, Pendientes
   - SP completados, SP restantes
   - Barra de progreso global
   - Ultima actualizacion

d) Actualizar Burndown Chart (mover `<- actual`)

e) Agregar al Historial de Cambios:
   ```
   | {fecha} | {US-ID} | COMPLETADA | {SP} | {herramientas usadas} |
   ```

### 11. Commit del tracker

```bash
git add docs/evaluations/cronograma-sprints.md
git commit -m "docs: update sprint tracker - {US-ID} completed"
git push origin main
```

### 12. Mostrar resumen

```
{US-ID} completada!
Branch: {branch_name}
PR: #{N} (mergeada)
Sprint N progress: X/Y SP (XX%)
Global progress: X/136 SP (XX%)
```
