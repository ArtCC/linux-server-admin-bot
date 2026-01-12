.PHONY: help install dev test lint format type-check clean build up down logs restart

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black ruff mypy

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=bot --cov=config --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check bot/ config/ tests/

format: ## Format code with black
	black bot/ config/ tests/ main.py

type-check: ## Run type checking
	mypy bot/ config/

quality: lint type-check test ## Run all quality checks

clean: ## Clean up cache and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

build: ## Build Docker image
	docker-compose build

up: ## Start bot in detached mode
	docker-compose up -d

down: ## Stop and remove containers
	docker-compose down

logs: ## Follow bot logs
	docker-compose logs -f

restart: ## Restart bot
	docker-compose restart

stop: ## Stop bot
	docker-compose stop

status: ## Show container status
	docker-compose ps

shell: ## Open shell in container
	docker-compose exec linux-server-admin-bot /bin/bash

update: ## Update and restart bot
	git pull
	docker-compose build
	docker-compose up -d
	@echo "Bot updated and restarted!"

env: ## Create .env from example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example"; \
		echo "Please edit .env with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

setup: env ## Quick setup
	@echo "Running setup..."
	@chmod +x setup.sh
	@./setup.sh
