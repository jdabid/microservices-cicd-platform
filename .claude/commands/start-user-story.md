Inicia el flujo git para una User Story. Crea el branch, actualiza el tracker a EN PROGRESO.

Argumento: $ARGUMENTS (ejemplo: "US-04", "US-14")

## Steps

1. **Parsear el argumento** para obtener el ID de la US (e.g., US-04).

2. **Leer el cronograma** en `docs/evaluations/cronograma-scrum.md` para obtener:
   - Sprint number (1-6)
   - Descripcion corta de la US
   - Story Points

3. **Determinar el tipo de branch** segun la descripcion:
   - Si es feature nuevo o endpoint: `feat`
   - Si es fix o correccion: `fix`
   - Si es config, limpieza, docs: `chore`
   - Si es test: `test`
   - Si es refactor: `refactor`

4. **Generar el nombre del branch** con este formato exacto:
   ```
   feature/s{sprint}-{US-ID}-{slug-corto}
   ```
   Ejemplos:
   - US-04 (Sprint 1, JWT auth) → `feature/s1-US04-jwt-auth`
   - US-14 (Sprint 2, tests integracion) → `feature/s2-US14-integration-tests-appointments`
   - US-22 (Sprint 3, Terraform base) → `feature/s3-US22-terraform-base`

   Reglas del slug:
   - Maximo 5 palabras
   - Solo letras minusculas, numeros y guiones
   - Sin articulos (el, la, los, de, con, para, y)

5. **Ejecutar los comandos git:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b {branch_name}
   ```

6. **Actualizar el tracker** (`docs/evaluations/cronograma-sprints.md`):
   - Cambiar el Estado de la US de `PENDIENTE` a `EN PROGRESO`
   - Agregar el nombre del branch en la columna Branch
   - Incrementar "En progreso" y decrementar "Pendientes" en Resumen General
   - NO commitear el tracker todavia (se hara en finish-user-story)

7. **Mostrar resumen:**
   ```
   US-XX iniciada
   Branch: feature/sN-USXX-slug
   Sprint: N - Nombre del Sprint
   SP: X
   Descripcion: ...
   ```
