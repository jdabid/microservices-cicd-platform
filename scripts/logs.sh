#!/bin/bash

SERVICE=${1:-""}
FOLLOW=${2:-""}

echo "📊 Service Logs"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ -z "$SERVICE" ]; then
    echo "Available services:"
    docker-compose ps --services
    echo ""
    echo "Usage: ./scripts/logs.sh [service_name] [follow]"
    echo "Example: ./scripts/logs.sh backend-api follow"
    exit 0
fi

if [ "$FOLLOW" = "follow" ] || [ "$FOLLOW" = "-f" ]; then
    docker-compose logs -f "$SERVICE"
else
    docker-compose logs --tail=100 "$SERVICE"
fi
