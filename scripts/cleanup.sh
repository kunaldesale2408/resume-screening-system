#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Resume Screening System - Cleanup${NC}"
echo "===================================="

echo -e "${YELLOW}Stopping Docker containers...${NC}"
docker-compose down

echo -e "${YELLOW}Removing Docker volumes...${NC}"
docker-compose down -v

echo -e "${YELLOW}Cleaning up local cache...${NC}"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/
rm -rf *.egg-info/
rm -rf build/
rm -rf dist/

echo -e "${YELLOW}Removing Docker system resources (optional)...${NC}"
echo -e "${YELLOW}This will remove unused images, containers, and networks.${NC}"
read -p "Do you want to clean up Docker system resources? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker system prune -f
    echo -e "${GREEN}✓ Docker system cleaned${NC}"
fi

echo ""
echo -e "${GREEN}✓ Cleanup completed!${NC}"
echo -e "${YELLOW}Note: data/raw/ and models/ directories were preserved.${NC}"
