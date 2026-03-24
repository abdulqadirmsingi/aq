# Architecture Overview

## System Design

AQ follows a domain-driven, modular monorepo architecture with clear separation
between the API layer (backend), data collection layer (scrapers), and
presentation layer (frontend).

### Data Flow

```
Data Sources → Scrapers → PostgreSQL → FastAPI → Next.js Dashboard
                  ↑                       ↑
              Celery/Redis           REST API (v1)
```

### Key Principles

- **Domain isolation**: Each data domain (energy, money, etc.) is a self-contained module
- **Layered architecture**: Router → Service → Repository → Database
- **Async-first**: Backend and scrapers use async I/O throughout
- **Queue-driven scraping**: All scraper jobs run via Celery for reliability and scheduling

See `rules.md` for coding standards and conventions.
