.PHONY: help up down build logs migrate migrate-create seed lint format test test-backend test-frontend test-scrapers
.PHONY: install-backend install-scrapers install-scrapers-browser dev-backend celery-worker celery-beat celery-call-ewura celery-call-bot celery-call-crdb celery-call-nmb scraper-ewura-once scraper-bot-once scraper-crdb-once scraper-nmb-once

# POSIX `sh` (dash): use `.` not `source` for venv activate.
SHELL := /bin/sh

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ── Docker ──────────────────────────────────── 
up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Rebuild all containers
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

# ── Python venvs (backend / scrapers) ───────────
install-backend: ## Create backend/.venv and install backend deps
	test -d backend/.venv || python3 -m venv backend/.venv
	cd backend && . .venv/bin/activate && pip install -r requirements.txt

install-scrapers: ## Create scrapers/.venv and install scraper deps
	test -d scrapers/.venv || python3 -m venv scrapers/.venv
	cd scrapers && . .venv/bin/activate && pip install -r requirements.txt

install-scrapers-browser: ## Install browser automation extras for protected sources like NMB
	test -d scrapers/.venv || python3 -m venv scrapers/.venv
	cd scrapers && . .venv/bin/activate && pip install -r requirements.txt -r requirements-playwright.txt && playwright install chromium

# ── Database (backend venv) ─────────────────────
migrate: ## Run Alembic migrations (uses backend/.venv)
	cd backend && . .venv/bin/activate && alembic upgrade head

migrate-create: ## New migration (usage: make migrate-create msg="description")
	cd backend && . .venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

seed: ## Seed the database
	bash infra/scripts/seed.sh

# ── Run API & workers (local venvs) ─────────────
dev-backend: ## Run FastAPI with reload (backend/.venv)
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

celery-worker: ## Celery worker for scrapers (scrapers/.venv)
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app worker --loglevel=info

celery-beat: ## Celery Beat scheduler (scrapers/.venv)
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app beat --loglevel=info

celery-call-ewura: ## Enqueue one EWURA run (worker must be running)
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app call scrapers.run_ewura_fuel

celery-call-bot: ## Enqueue one BOT exchange-rate run
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app call scrapers.run_bot_exchange_rates

celery-call-crdb: ## Enqueue one CRDB forex run
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app call scrapers.run_crdb_forex

celery-call-nmb: ## Enqueue one NMB exchange-rate run
	cd scrapers && . .venv/bin/activate && celery -A src.workers.celery_app call scrapers.run_nmb_daily_exchange_rates

scraper-ewura-once: ## Run EWURA scraper once in-process (no Celery; scrapers/.venv)
	cd scrapers && . .venv/bin/activate && python -c "from src.domains.energy.fuel_scraper import EwuraFuelScraper; s = EwuraFuelScraper(); s.run(); s.close()"

scraper-bot-once: ## Run BOT scraper once in-process
	cd scrapers && . .venv/bin/activate && python -c "from src.domains.money.bot_exchange_rate_scraper import BotExchangeRateScraper; s = BotExchangeRateScraper(); print(s.run()); s.close()"

scraper-crdb-once: ## Run CRDB scraper once in-process
	cd scrapers && . .venv/bin/activate && python -c "from src.domains.money.crdb_exchange_rate_scraper import CrdbExchangeRateScraper; s = CrdbExchangeRateScraper(); print(s.run()); s.close()"

scraper-nmb-once: ## Run NMB scraper once in-process
	cd scrapers && . .venv/bin/activate && python -c "from src.domains.money.nmb_exchange_rate_scraper import NmbExchangeRateScraper; s = NmbExchangeRateScraper(); print(s.run()); s.close()"

# ── Quality ───────────────────────────────────
lint: ## Run linters
	cd backend && . .venv/bin/activate && ruff check .
	cd frontend && npm run lint

format: ## Auto-format code
	cd backend && . .venv/bin/activate && ruff format .
	cd frontend && npm run format

# ── Testing ────────────────────────────────────
test: ## Run all tests
	cd backend && . .venv/bin/activate && pytest
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && . .venv/bin/activate && pytest -v

test-scrapers: ## Run scraper tests only
	cd scrapers && . .venv/bin/activate && pytest -v

test-frontend: ## Run frontend tests only
	cd frontend && npm test

# ── Setup ─────────────────────────────────────
setup: ## Initial project setup
	bash infra/scripts/setup.sh
