Actualiza automaticamente el archivo `docs/evaluations/cronograma-sprints.md` cada vez que se finaliza una User Story.

## Instructions

1. Leer `docs/evaluations/cronograma-sprints.md`

2. Determinar que US se completo. Si se proporciona como argumento, usar ese valor.

   Argumento: $ARGUMENTS

3. Actualizar la fila de la US completada en la tabla del Sprint correspondiente:
   - Cambiar Estado de `PENDIENTE` a `DONE`
   - Agregar el nombre del branch (obtener con `git branch --show-current`)
   - Agregar el link al PR: `[#N](https://github.com/jdabid/microservices-cicd-platform/pull/N)`
   - Agregar la fecha actual (YYYY-MM-DD)

4. Recalcular las metricas del Sprint (SP Completados, barra de progreso)

5. Recalcular las metricas globales (Resumen General)

6. Actualizar el Burndown Chart

7. Agregar entrada al Historial de Cambios
