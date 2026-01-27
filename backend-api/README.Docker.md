# Backend API - Docker

## Build
```bash
docker build -t microservices-backend-api:latest .
```

## Run
```bash
docker run -d \
  --name backend-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e REDIS_HOST="redis-host" \
  microservices-backend-api:latest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_HOST` | Redis host | `localhost` |
| `DEBUG` | Debug mode | `False` |

## Image Details

- **Base:** python:3.12-slim-bookworm
- **Size:** ~190MB
- **User:** appuser (non-root)
- **Port:** 8000
- **Health Check:** `/health` endpoint

## Development
```bash
# Build
docker build -t backend-api:dev .

# Run with volume mount
docker run -v $(pwd):/app backend-api:dev
```