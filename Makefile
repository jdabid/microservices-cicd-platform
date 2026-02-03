.PHONY: help start stop restart logs health backup restore clean build test

help: ## Show this help
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║           Microservices Platform - Commands                ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

start: ## Start all services
	@./scripts/start.sh

start-prod: ## Start in production mode
	@./scripts/start.sh production

stop: ## Stop all services
	@./scripts/stop.sh

stop-clean: ## Stop and remove volumes
	@./scripts/stop.sh clean

restart: stop start ## Restart all services

logs: ## View logs (use: make logs service=backend-api)
	@./scripts/logs.sh $(service)

logs-f: ## Follow logs (use: make logs-f service=backend-api)
	@./scripts/logs.sh $(service) follow

health: ## Check health of all services
	@./scripts/health.sh

backup: ## Backup database
	@./scripts/backup.sh

restore: ## Restore database (use: make restore file=backup.sql.gz)
	@./scripts/restore.sh $(file)

build: ## Rebuild all images
	docker-compose build

build-no-cache: ## Rebuild without cache
	docker-compose build --no-cache

ps: ## Show running containers
	docker-compose ps

stats: ## Show resource usage
	docker stats $(shell docker-compose ps -q)

clean: ## Remove all containers, images, volumes
	docker-compose down -v --rmi all

test-backend: ## Run backend tests
	docker-compose exec backend-api pytest

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	@curl -f http://localhost:8000/health || exit 1
	@curl -f http://localhost/ || exit 1
	@echo "✅ Integration tests passed"

shell-backend: ## Open shell in backend container
	docker-compose exec backend-api bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres appointments_db

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

update: ## Pull latest images
	docker-compose pull

prune: ## Clean up unused Docker resources
	docker system prune -af --volumes

# Development helpers
dev-frontend: ## Start frontend in dev mode
	cd frontend && npm run dev

dev-backend: ## Start backend in dev mode with reload
	cd backend-api && uvicorn app.main:app --reload

install-backend: ## Install backend dependencies
	cd backend-api && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install
