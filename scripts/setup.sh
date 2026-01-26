#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Setting up Microservices CI/CD Platform..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || {
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Install from: https://www.python.org/downloads/"
    exit 1
}

command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}❌ Docker is required but not installed.${NC}"
    echo "Install from: https://docs.docker.com/get-docker/"
    exit 1
}

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Setup Backend API
echo "🐍 Setting up Backend API..."
cd backend-api

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
pip install -r requirements-dev.txt --quiet

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file. Please update with your configuration.${NC}"
fi

cd ..

echo -e "${GREEN}✅ Backend API setup complete${NC}"
echo ""

# Start infrastructure
echo "🐳 Starting infrastructure (PostgreSQL + Redis)..."
docker-compose up -d postgres redis

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "  1. Update backend-api/.env with your configuration"
echo ""
echo "  2. Run database migrations (after creating models):"
echo "     cd backend-api"
echo "     source venv/bin/activate"
echo "     alembic upgrade head"
echo ""
echo "  3. Run backend API:"
echo "     cd backend-api"
echo "     source venv/bin/activate"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  4. Open API documentation:"
echo "     http://localhost:8000/docs"
echo ""
echo "🎉 Happy coding!"