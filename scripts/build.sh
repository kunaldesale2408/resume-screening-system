#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Resume Screening System - Docker Build${NC}"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: docker-compose up -d"
    echo "  2. Frontend: http://localhost:8501"
    echo "  3. API: http://localhost:8000/docs"
else
    echo -e "${RED}✗ Build failed. Please check the errors above.${NC}"
    exit 1
fi
