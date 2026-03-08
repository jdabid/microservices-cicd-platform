# Sprint 3 — Errores y Lecciones Aprendidas

> Registro de errores, problemas y soluciones encontrados durante el desarrollo del Sprint 3.
> Sprint 3: Infrastructure as Code (Terraform) | 7 US | 21 SP | PR #21

---

## Error 1: Modulos Terraform creados sin integracion root

**Contexto:** Se lanzaron 3 agents en paralelo para crear la infraestructura Terraform:
- Agent 1: US-22 + US-23 (base + VPC)
- Agent 2: US-24 + US-25 + US-26 (EKS + RDS + ElastiCache)
- Agent 3: US-27 + US-28 (tfvars + docs)

**Error:** El Agent 1 creo el `main.tf` raiz solo con el modulo VPC (que era lo unico en su scope). El Agent 2 creo los modulos EKS, RDS y ElastiCache como archivos independientes, pero no actualizo el `main.tf` raiz para invocarlos. Resultado: los modulos existian pero no estaban conectados.

**Impacto:** Se requirio trabajo manual de integracion para:
- Agregar `module "eks"`, `module "rds"`, `module "elasticache"` a `main.tf`
- Agregar 12 variables nuevas al `variables.tf` raiz (EKS, RDS, ElastiCache params)
- Agregar 5 outputs nuevos al `outputs.tf` raiz

**Solucion:** Editar manualmente `main.tf`, `variables.tf` y `outputs.tf` desde el contexto principal para conectar todos los modulos, pasando las outputs de VPC (vpc_id, private_subnet_ids) como inputs a EKS, RDS y ElastiCache.

**Leccion:** Cuando se dividen modulos Terraform entre multiples agents, el root module (`main.tf`, `variables.tf`, `outputs.tf`) debe ser responsabilidad de UN solo agent que conozca todos los modulos, o debe haber un paso explicito de integracion. Alternativa: incluir en el prompt del Agent 2 instrucciones para crear un archivo `main.tf.fragment` con las invocaciones de modulos a agregar.

---

## Error 2: tfvars bloqueados por .gitignore

**Contexto:** El `.gitignore` del proyecto tiene el patron `*.tfvars` para prevenir commit de variables con secretos.

**Error:** `git add terraform/environments/dev.tfvars` y `prod.tfvars` fueron rechazados por `.gitignore`.

**Impacto:** Requirio usar `git add -f` para forzar la inclusion de archivos que son ejemplos sin secretos reales.

**Solucion:** Se uso `git add -f` para agregar los archivos. Los tfvars solo contienen configuracion de sizing (instance types, node counts, CIDRs) sin secretos.

**Leccion:** Agregar excepcion en `.gitignore` para tfvars de ejemplo:
```gitignore
*.tfvars
!terraform/environments/*.tfvars
```
O renombrar a `dev.tfvars.example` y `prod.tfvars.example` para evitar confusion.

---

## Error 3: Variables inconsistentes entre root y modulos

**Contexto:** El Agent 3 creo los tfvars con nombres de variables basados en el esquema estandar de Terraform, pero el Agent 2 uso nombres ligeramente diferentes en los modulos.

**Error:** Los tfvars usaban `db_instance_class` mientras el modulo RDS esperaba `instance_class`. Lo mismo con `cache_node_type` vs `node_type` y `cache_num_nodes` vs `num_cache_nodes`.

**Impacto:** Se requirio crear variables "puente" en el `variables.tf` raiz con los nombres usados en los tfvars, y mapearlas a los nombres esperados por los modulos en `main.tf`.

**Solucion:**
```hcl
# variables.tf (root)
variable "db_instance_class" { ... }

# main.tf (root)
module "rds" {
  instance_class = var.db_instance_class  # mapping
}
```

**Leccion:** Al dividir trabajo entre agents, definir un contrato de interfaz claro: especificar los nombres exactos de variables que el root module usara y que los modulos deben aceptar. Incluir esta especificacion en el prompt de TODOS los agents, no solo en uno.

---

## Error 4: Directorio modules/vpc/ no existia al copiar

**Contexto:** Al consolidar archivos desde los 3 worktrees al repo principal.

**Error:**
```
cp: terraform/modules/vpc/main.tf: No such file or directory
```
Se habia creado `terraform/modules/eks`, `terraform/modules/rds` y `terraform/modules/elasticache` con `mkdir -p`, pero se olvido crear `terraform/modules/vpc`.

**Impacto:** El primer intento de copia fallo. Se tuvo que agregar `mkdir -p terraform/modules/vpc` y reintentar.

**Solucion:** Agregar el `mkdir -p` para todos los directorios necesarios antes de copiar.

**Leccion:** Al consolidar archivos de multiples worktrees, crear TODOS los directorios destino de una vez con un solo `mkdir -p` que incluya todas las rutas. No asumir que algunos ya existen.

---

## Error 5: Consolidacion de 3 worktrees requiere coordinacion manual

**Contexto:** Los 3 agents crearon archivos en 3 directorios de worktree separados que debian consolidarse en un solo branch.

**Error:** No es un error per se, sino un overhead de coordinacion: hubo que ejecutar 6 comandos `cp` separados, verificar que todos los archivos se copiaron (20 archivos en total), hacer integracion manual de los root modules, y finalmente validar con `find terraform/ -type f | sort`.

**Impacto:** ~5 minutos de trabajo manual de consolidacion entre el completado de los agents y el commit final.

**Solucion:** Se establecio un flujo:
1. `mkdir -p` todos los directorios destino
2. `cp` archivos de cada worktree
3. Verificar con `find` o `git status`
4. Integrar root modules manualmente
5. `git add` + `git commit`

**Leccion:** Para sprints con muchos archivos interdependientes, considerar usar menos agents pero con scope mas amplio. Por ejemplo, un solo agent con todo el Sprint 3 hubiera evitado la integracion manual. La paralelizacion tiene un costo de coordinacion que no siempre se justifica.

---

## Resumen de Metricas de Errores

| Metrica | Valor |
|---------|-------|
| Total errores registrados | 5 |
| Errores por coordinacion multi-agent | 3 (Error 1, 3, 5) |
| Errores por configuracion git | 1 (Error 2 - recurrente de S2) |
| Errores por filesystem | 1 (Error 4) |
| Trabajo perdido | 0 |
| Tiempo en integracion manual | ~5 minutos |

---

## Mejoras Aplicadas para Sprints Futuros

1. **Definir contratos de interfaz** entre agents — nombres de variables, outputs esperados
2. **Root module como responsabilidad central** — no delegar a un solo agent
3. **Crear todos los directorios destino** de una vez antes de copiar
4. **Evaluar costo de paralelizacion** — a veces 1 agent grande es mas eficiente que 3 pequenos
5. **Revisar .gitignore** para excepciones de archivos de ejemplo
6. **Verificar archivos con `find`** despues de consolidar worktrees
