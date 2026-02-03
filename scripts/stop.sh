#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Stopping Microservices Platform                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

REMOVE_VOLUMES=${1:-false}

if [ "$REMOVE_VOLUMES" = "clean" ]; then
    echo "⚠️  Stopping and removing volumes (ALL DATA WILL BE LOST)"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose down -v
        echo "✅ Services stopped and volumes removed"
    else
        echo "❌ Cancelled"
        exit 0
    fi
else
    echo "🛑 Stopping services (data will be preserved)..."
    docker-compose down
    echo "✅ Services stopped"
fi

echo ""
echo "💡 To remove volumes: ./scripts/stop.sh clean"
