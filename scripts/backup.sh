#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Database Backup                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup..."
docker-compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Show size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "📊 Size: $SIZE"
    
    # Keep only last 7 backups
    echo ""
    echo "🧹 Cleaning old backups (keeping last 7)..."
    ls -t "${BACKUP_DIR}"/postgres_backup_*.sql.gz | tail -n +8 | xargs -r rm
    
    echo "✅ Backup complete!"
else
    echo "❌ Backup failed"
    exit 1
fi
