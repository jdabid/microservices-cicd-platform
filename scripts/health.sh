#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Health Check                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local name=$1
    local url=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name is healthy"
        return 0
    else
        echo -e "${RED}❌${NC} $name is unhealthy"
        return 1
    fi
}

echo "🔍 Checking Docker services..."
docker-compose ps
echo ""

echo "🔍 Checking endpoints..."
check_service "Frontend" "http://localhost/"
check_service "Backend API" "http://localhost:8000/health"
check_service "Flower" "http://localhost:5555"
echo ""

echo "🔍 Checking Docker health status..."
for service in $(docker-compose ps --services); do
    health=$(docker inspect --format='{{.State.Health.Status}}' "$(docker-compose ps -q $service)" 2>/dev/null || echo "no-healthcheck")
    
    if [ "$health" = "healthy" ]; then
        echo -e "${GREEN}✅${NC} $service: $health"
    elif [ "$health" = "no-healthcheck" ]; then
        echo -e "${YELLOW}⚠️${NC}  $service: (no healthcheck configured)"
    else
        echo -e "${RED}❌${NC} $service: $health"
    fi
done

echo ""
echo "✅ Health check complete"
