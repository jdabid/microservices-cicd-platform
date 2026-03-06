Ejecuta el flujo git completo para una User Story: start → (ya implementada) → finish.

Argumento: $ARGUMENTS (ejemplo: "US-06", "US-06 US-07", "US-06 US-07 US-08")

## Modo 1: Una sola US

Si se pasa un solo ID (e.g., "US-06"):

1. Ejecutar `/start-user-story US-06` (crear branch, marcar EN PROGRESO)
2. Decirle al usuario que ya puede implementar la US o pedirme que la implemente
3. Cuando la implementacion este lista, ejecutar `/finish-user-story` (commit, push, PR, merge, tracker)

## Modo 2: Multiples US en batch

Si se pasan multiples IDs (e.g., "US-06 US-07 US-08"):

Evaluar si las US son:

**a) Interdependientes (tocan mismos archivos):**
   - Crear UN solo branch: `feature/s{N}-{US-first}-to-{US-last}-{slug}`
   - Ejemplo: `feature/s1-US06-to-US08-patients-crud`
   - Implementar todas juntas
   - Un solo commit con mensaje que mencione todas las US
   - Una sola PR con titulo que mencione rango
   - En el tracker, marcar todas con el mismo branch y PR

**b) Independientes (no tocan mismos archivos):**
   - Recomendar lanzar Agents en worktree para cada US
   - Cada Agent crea su propio branch y commitea
   - Desde el contexto principal: cherry-pick, push, PR, merge de cada uno
   - Actualizar tracker con cada PR

## Modo 3: Agent en worktree

Si el usuario pide ejecutar con agents:

```
Para cada US independiente:
1. Lanzar Agent(isolation="worktree") con instrucciones de:
   - Crear branch feature/sN-USXX-slug
   - Implementar la US completa
   - git add y git commit con formato conventional commits
2. Desde el contexto principal, cuando el agent termine:
   - git cherry-pick {SHA} al branch correspondiente
   - git push
   - gh pr create
   - gh pr merge
   - Actualizar tracker
```

IMPORTANTE para agents en worktree:
- Los agents DEBEN hacer `git add` y `git commit` dentro del worktree
- Incluir en el prompt del agent: "You MUST commit your work with git add and git commit before finishing"
- Si el agent no commitea, copiar archivos manualmente y commitear desde el contexto principal

## Formato del branch

```
feature/s{sprint}-{US-ID}-{slug}
```

- sprint: numero del sprint (1-6)
- US-ID: sin guion (US04, US14, etc.)
- slug: 2-5 palabras, lowercase, guiones, sin articulos

## Formato del commit

```
{type}({scope}): {descripcion en ingles max 72 chars}

- Cambio 1
- Cambio 2
- US-XX from Sprint N

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

## Formato del PR title

```
{type}({scope}): {descripcion} ({US-ID})
```

Si son multiples US:
```
{type}({scope}): {descripcion} ({US-first}, {US-last})
```
