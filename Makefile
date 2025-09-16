# ============================================================================
# Makefile
# ============================================================================
.PHONY: help install test lint format clean docker-up docker-down migrate

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $1, $2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	pre-commit install

install-dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov black isort mypy pre-commit

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

lint: ## Run linting
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

clean: ## Clean up temporary files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

docker-build: ## Build docker images
	$(DOCKER_COMPOSE) build

docker-up: ## Start services with Docker
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop Docker services
	$(DOCKER_COMPOSE) down

docker-logs: ## Show Docker logs
	$(DOCKER_COMPOSE) logs -f

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$message"

migrate-downgrade: ## Downgrade database migration
	alembic downgrade -1

run-dev: ## Run development server
	uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run production server
	uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4

setup: ## Initial project setup
	@chmod +x scripts/setup/setup.sh
	@./scripts/setup/setup.sh

backup-db: ## Backup database
	@echo "Creating database backup..."
	@mkdir -p data/backups
	@pg_dump $(DB_URL) > data/backups/backup_$(shell date +%Y%m%d_%H%M%S).sql

monitor: ## Show system monitoring
	@echo "API Health:"
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo "\nSystem Metrics:"
	@curl -s http://localhost:8000/api/v1/monitoring/system/metrics | python -m json.tool import