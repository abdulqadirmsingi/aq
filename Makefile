.PHONY: help up down build logs migrate seed lint format test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────
up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Rebuild all containers
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

# ── Database ──────────────────────────────────
migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	cd backend && alembic revision --autogenerate -m "$(msg)"

seed: ## Seed the database
	bash infra/scripts/seed.sh

# ── Quality ───────────────────────────────────
lint: ## Run linters
	cd backend && ruff check .
	cd frontend && npm run lint

format: ## Auto-format code
	cd backend && ruff format .
	cd frontend && npm run format

# ── Testing ───────────────────────────────────
test: ## Run all tests
	cd backend && pytest
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && pytest -v

test-frontend: ## Run frontend tests only
	cd frontend && npm test

# ── Setup ─────────────────────────────────────
setup: ## Initial project setup
	bash infra/scripts/setup.sh
