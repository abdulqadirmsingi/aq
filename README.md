# AQ — Data Intelligence Hub

A modular, scalable data intelligence platform that collects, stores, and serves time-series data across multiple domains.

## Domains

| Domain        | Examples                              |
| ------------- | ------------------------------------- |
| Energy        | Fuel, gas, electricity prices         |
| Money         | Exchange rates, inflation, stocks     |
| Living Cost   | Rent, land prices                     |
| Medicine      | Drug / pharmaceutical prices          |
| HR            | Salaries, job market trends           |

## Tech Stack

| Layer      | Technology                                    |
| ---------- | --------------------------------------------- |
| Backend    | FastAPI, SQLAlchemy 2.0 (async), PostgreSQL   |
| Frontend   | Next.js 15 (App Router), TypeScript, Tailwind |
| Scrapers   | Python, Celery, Redis                         |
| Infra      | Docker Compose, Nginx, GitHub Actions         |

## Quick Start

```bash
make setup   # Copy env files
make up      # Start all services (Docker)
make migrate # Run database migrations
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
aq/
├── backend/          # FastAPI application (domain-driven modules)
├── frontend/         # Next.js dashboard (App Router + TypeScript)
├── scrapers/         # Independent data collection workers
├── shared/           # Constants and types shared across services
├── infra/            # Docker, Nginx, automation scripts
├── docs/             # Architecture and domain documentation
├── .github/          # CI/CD workflows
├── .husky/           # Git hooks (lint, commit message validation)
├── rules.md          # Mandatory project rules and conventions
└── docker-compose.yml
```

See [docs/setup.md](docs/setup.md) for detailed development setup instructions.

See [rules.md](rules.md) for project conventions and coding standards.

## License

Private — All rights reserved.
