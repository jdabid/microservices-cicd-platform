#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Database Restore                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

BACKUP_FILE=${1:-""}

if [ -z "$BACKUP_FILE" ]; then
    echo "Available backups:"
    ls -lh ./backups/*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Usage: ./scripts/restore.sh <backup_file>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "⚠️  This will REPLACE the current database!"
echo "📁 Backup file: $BACKUP_FILE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🔄 Restoring backup..."

gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB"

if [ $? -eq 0 ]; then
    echo "✅ Restore complete!"
else
    echo "❌ Restore failed"
    exit 1
fi
