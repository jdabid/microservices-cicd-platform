# Load Testing con k6

Scripts de pruebas de carga para la plataforma de citas medicas usando [k6](https://k6.io/).

## Estructura

```
load-testing/
├── scripts/
│   ├── health-check.js        # Test de endpoints /health y /ready
│   ├── auth-flow.js           # Flujo de registro + login + perfil
│   ├── patients-crud.js       # CRUD completo de pacientes
│   ├── appointments-flow.js   # Flujo completo de citas
│   └── full-scenario.js       # Escenario combinado multi-flujo
├── config/
│   ├── env.js                 # Configuracion de entorno
│   └── thresholds.json        # Definiciones de umbrales compartidos
├── docker-compose.k6.yml      # Stack k6 + InfluxDB + Grafana
├── results/                   # Directorio para resultados
└── README.md
```

## Requisitos

### Opcion 1: Instalacion local de k6

```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6

# Windows
choco install k6
```

### Opcion 2: Docker (sin instalacion local)

Solo necesitas Docker y Docker Compose instalados.

## Uso

### Ejecutar tests individuales (local)

```bash
# Desde el directorio load-testing/
cd load-testing

# Health check (mas rapido, ideal para verificar setup)
k6 run scripts/health-check.js

# Auth flow
k6 run scripts/auth-flow.js

# Patients CRUD
k6 run scripts/patients-crud.js

# Appointments flow
k6 run scripts/appointments-flow.js

# Escenario completo (todos los flujos combinados)
k6 run scripts/full-scenario.js
```

### Configurar URL del servidor

```bash
# Apuntar a un entorno diferente
k6 run -e BASE_URL=https://staging.example.com scripts/health-check.js
```

### Ejecutar con Docker Compose (resultados en Grafana)

```bash
# 1. Levantar InfluxDB y Grafana
docker compose -f docker-compose.k6.yml up -d influxdb grafana

# 2. Ejecutar un test (los resultados se envian a InfluxDB)
docker compose -f docker-compose.k6.yml run --rm k6 run /scripts/health-check.js

# 3. Ver resultados en Grafana
#    Abrir http://localhost:3001
#    Agregar datasource InfluxDB: URL=http://influxdb:8086, DB=k6
#    Importar dashboard ID 2587 (k6 Load Testing Results)

# 4. Limpiar
docker compose -f docker-compose.k6.yml down -v
```

### Exportar resultados a JSON

```bash
k6 run --out json=results/health-check-results.json scripts/health-check.js
```

## Objetivos SLO (Service Level Objectives)

| Metrica              | Objetivo     | Descripcion                              |
|----------------------|--------------|------------------------------------------|
| p95 latencia         | < 500ms      | 95% de requests bajo 500ms              |
| p99 latencia         | < 1000ms     | 99% de requests bajo 1 segundo          |
| Tasa de error        | < 5%         | Menos del 5% de requests fallidos       |
| Health check p95     | < 200ms      | Endpoints de salud ultra rapidos         |
| Disponibilidad       | > 99%        | Uptime durante pruebas de carga         |

## Descripcion de Tests

### health-check.js
- **Objetivo**: Validar rendimiento de endpoints de infraestructura
- **Endpoints**: `GET /health`, `GET /ready`
- **Carga**: 10 VUs durante 2 minutos (ramp up/down de 30s)
- **Umbrales**: p95 < 200ms, error rate < 1%

### auth-flow.js
- **Objetivo**: Validar flujo completo de autenticacion
- **Endpoints**: `POST /register`, `POST /login`, `GET /me`
- **Carga**: 5 VUs durante 2 minutos
- **Umbrales**: p95 < 500ms, error rate < 5%

### patients-crud.js
- **Objetivo**: Validar operaciones CRUD de pacientes
- **Endpoints**: `POST /patients`, `GET /patients/:id`, `GET /patients`, `PUT /patients/:id`, `DELETE /patients/:id`
- **Carga**: 5 VUs durante 3 minutos
- **Umbrales**: p95 < 500ms por operacion

### appointments-flow.js
- **Objetivo**: Validar flujo completo de citas medicas
- **Endpoints**: `POST /appointments`, `GET /appointments`, `GET /appointments/:id`, `DELETE /appointments/:id`
- **Carga**: 5 VUs durante 3 minutos
- **Umbrales**: p95 < 500ms por operacion

### full-scenario.js
- **Objetivo**: Simular carga realista con multiples flujos simultaneos
- **Distribucion**: 40% health, 20% auth, 20% patients, 20% appointments
- **Carga**: 20 VUs totales durante 5 minutos
- **Umbrales**: p95 < 500ms global, p99 < 1000ms, error rate < 5%
- **Metricas**: Custom metrics por flujo para analisis granular

## Interpretacion de Resultados

### Metricas clave de k6

- **http_req_duration**: Tiempo total de cada request HTTP
  - `p(95)`: El 95% de requests fue mas rapido que este valor
  - `p(99)`: El 99% de requests fue mas rapido que este valor
  - `avg`: Promedio de duracion
- **http_req_failed**: Porcentaje de requests que fallaron
- **http_reqs**: Total de requests realizados
- **vus**: Virtual Users activos
- **iterations**: Iteraciones completadas por todos los VUs

### Estado de los umbrales

- Si aparece un checkmark verde, el umbral se cumplio
- Si aparece una X roja, se violo el SLO definido
- Revisar metricas custom por flujo para identificar cuellos de botella
