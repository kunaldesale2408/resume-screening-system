#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Resume Screening System - Deployment${NC}"
echo "======================================="

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed.${NC}"
    exit 1
fi

echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down

echo -e "${YELLOW}Building images...${NC}"
docker-compose build --no-cache

echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

# Check if services are healthy
sleep 5

echo -e "${YELLOW}Checking service health...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
fi

echo ""
echo -e "${GREEN}✓ Deployment completed!${NC}"
echo ""
echo "Services running:"
echo "  - Frontend: http://localhost:8501"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"
