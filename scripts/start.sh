#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Starting Microservices Platform                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment loaded from .env"
else
    echo "⚠️  No .env file found, using defaults"
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Choose environment
ENV=${1:-development}
echo "🌍 Environment: $ENV"
echo ""

# Start services
if [ "$ENV" = "production" ]; then
    echo "🚀 Starting in PRODUCTION mode..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
    echo "🚀 Starting in DEVELOPMENT mode..."
    docker-compose up -d
fi

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🔍 Service Status:"
docker-compose ps

echo ""
echo "✅ All services started!"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Access URLs                              ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ Frontend:    http://localhost                              ║"
echo "║ Backend API: http://localhost:8000/docs                    ║"
echo "║ Flower:      http://localhost:5555                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 View logs: docker-compose logs -f [service_name]"
echo "🛑 Stop all:  docker-compose down"
