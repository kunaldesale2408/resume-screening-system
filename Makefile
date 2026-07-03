.PHONY: help install setup clean run-backend run-frontend run-all test lint format docker-build docker-up docker-down

# Variables
PYTHON := python3
PIP := pip3
VENV := venv

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.DEFAULT_GOAL := help

help: ## Display this help message
	@echo "$(GREEN)Resume Screening System - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

setup: ## Set up development environment
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	cp .env.example .env
	@echo "$(GREEN)Environment configured. Please update .env with your settings.$(NC)"

clean: ## Clean up cache and temporary files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "$(GREEN)Cleanup complete!$(NC)"

run-backend: ## Run FastAPI backend
	@echo "$(YELLOW)Starting FastAPI backend...$(NC)"
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run Streamlit frontend
	@echo "$(YELLOW)Starting Streamlit frontend...$(NC)"
	streamlit run src/web/streamlit_app.py

run-all: ## Run both backend and frontend (requires two terminals)
	@echo "$(YELLOW)Run the following commands in separate terminals:$(NC)"
	@echo "$(GREEN)Terminal 1: make run-backend$(NC)"
	@echo "$(GREEN)Terminal 2: make run-frontend$(NC)"

test: ## Run tests with coverage
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest tests/ -v --cov=src --cov-report=html
	@echo "$(GREEN)Tests completed! Coverage report: htmlcov/index.html$(NC)"

lint: ## Run linting checks
	@echo "$(YELLOW)Running linting checks...$(NC)"
	flake8 src tests --max-line-length=120
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code...$(NC)"
	isort src tests
	black src tests --line-length=120
	@echo "$(GREEN)Code formatted!$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checks...$(NC)"
	mypy src --ignore-missing-imports
	@echo "$(GREEN)Type checking complete!$(NC)"

docker-build: ## Build Docker images
	@echo "$(YELLOW)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)Docker images built!$(NC)"

docker-up: ## Start Docker containers
	@echo "$(YELLOW)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Containers started!$(NC)"
	@echo "Frontend: http://localhost:8501"
	@echo "API: http://localhost:8000/docs"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)Containers stopped!$(NC)"

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)Docker cleanup complete!$(NC)"

download-dataset: ## Download Kaggle dataset
	@echo "$(YELLOW)Downloading Kaggle dataset...$(NC)"
	pip install kaggle
	kaggle datasets download -d elnahas/resume-dataset -p data/raw/
	@echo "$(GREEN)Dataset downloaded!$(NC)"
