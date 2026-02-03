# 🐳 Docker Compose - Guía de Uso

## 🚀 Quick Start
```bash
# Desarrollo
make start

# Producción
make start-prod

# Ver logs
make logs service=backend-api
make logs-f service=celery-worker

# Parar todo
make stop
```

---

## 📂 Estructura de Archivos
```
docker-compose.yml           → Base configuration
docker-compose.override.yml  → Development overrides (auto-loaded)
docker-compose.prod.yml      → Production configuration
.env                         → Environment variables (not in git)
.env.example                 → Template for .env
```

---

## 🌍 Environments

### Development
```bash
# Usa docker-compose.yml + docker-compose.override.yml
docker-compose up -d

# Features:
# - Hot reload enabled
# - Debug logging
# - Ports exposed
# - Source code mounted
```

### Production
```bash
# Usa docker-compose.yml + docker-compose.prod.yml
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Features:
# - Multiple replicas
# - Rolling updates
# - Secrets management
# - No exposed ports
# - Warning-level logging
```

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
nano .env
```

**Important variables:**
- `SECRET_KEY`: Change to secure random string
- `POSTGRES_PASSWORD`: Strong password
- `FLOWER_BASIC_AUTH`: user:password for Flower UI
- `ENVIRONMENT`: development | staging | production

---

## 🌐 Networks
```
frontend-network   → Frontend ↔ Backend API
backend-network    → Backend API ↔ Celery ↔ Redis
database-network   → Backend API ↔ Celery ↔ PostgreSQL
cache-network      → Celery ↔ Redis
```

**Benefits:**
- Isolation between layers
- Security (frontend can't access DB directly)
- Clear service boundaries

---

## 💾 Volumes
```
postgres_data  → /data/postgres (persistent DB data)
redis_data     → /data/redis (persistent cache data)
```

**Backup:**
```bash
make backup
# Creates: ./backups/postgres_backup_YYYYMMDD_HHMMSS.sql.gz
```

**Restore:**
```bash
make restore file=./backups/postgres_backup_20250128_120000.sql.gz
```

---

## 📊 Resource Limits

### Backend API
```yaml
limits:
  cpus: '1'       # Max 1 CPU core
  memory: 512M    # Max 512MB RAM
reservations:
  cpus: '0.5'     # Guaranteed 0.5 CPU
  memory: 256M    # Guaranteed 256MB
```

### PostgreSQL
```yaml
limits:
  cpus: '1'
  memory: 512M
```

### Redis
```yaml
limits:
  cpus: '0.5'
  memory: 256M
```

### Frontend (Nginx)
```yaml
limits:
  cpus: '0.5'
  memory: 128M
```

---

## 🔄 Restart Policies
```yaml
restart: unless-stopped
```

**Options:**
- `no`: Never restart
- `always`: Always restart
- `on-failure`: Only on error
- `unless-stopped`: Always, except manual stop

---

## 📝 Logging
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # Max file size
    max-file: "3"     # Keep 3 files
```

**View logs:**
```bash
docker-compose logs -f backend-api
docker-compose logs --tail=100 celery-worker
```

---

## 🔍 Health Checks

All services have health checks:
```bash
# View health status
docker-compose ps

# Inspect specific service
docker inspect microservices-backend-api --format='{{.State.Health.Status}}'
```

---

## 🛠️ Common Commands
```bash
# Start
make start

# Stop
make stop

# Restart
make restart

# View logs
make logs service=backend-api

# Health check
make health

# Backup DB
make backup

# Restore DB
make restore file=backup.sql.gz

# Rebuild images
make build

# Clean everything
make clean

# Show resource usage
make stats
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs backend-api

# Check health
docker-compose ps

# Restart specific service
docker-compose restart backend-api
```

### Database connection issues
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Connect to DB
make shell-db
```

### Out of memory
```bash
# Check resource usage
make stats

# Increase limits in docker-compose.yml
```

### Volumes issues
```bash
# Remove and recreate
make stop-clean
make start
```

---

## 📚 Referencias

- Docker Compose: https://docs.docker.com/compose/
- Resource limits: https://docs.docker.com/compose/compose-file/#resources
- Networking: https://docs.docker.com/compose/networking/
- Volumes: https://docs.docker.com/storage/volumes/

