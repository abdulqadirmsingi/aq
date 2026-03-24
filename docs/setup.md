# Development Setup

## Prerequisites

- Python 3.12+
- Node.js 22+
- Docker & Docker Compose
- PostgreSQL 16 (or use Docker)
- Redis 7 (or use Docker)

## Quick Start

```bash
# 1. Clone and enter the project
cd aq

# 2. Run initial setup
make setup

# 3. Start all services via Docker
make up

# 4. Run database migrations
make migrate

# 5. Access the application
#    Frontend:  http://localhost:3000
#    Backend:   http://localhost:8000
#    API Docs:  http://localhost:8000/docs
```

## Manual Setup (without Docker)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Scrapers
```bash
cd scrapers
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
celery -A src.workers.celery_app worker --loglevel=info
```
