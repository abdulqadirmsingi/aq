# AQ Project Rules

> These rules are **mandatory** for all contributors. Every pull request must comply.

---

## 1. General Architecture

- **Modular architecture is mandatory.** Every data domain is a self-contained module.
- **No large files.** If a file exceeds ~200 lines, split it. Keep files small and focused on a single responsibility.
- **Separation of concerns is non-negotiable.** Routing, business logic, data access, and validation each belong in their own layer.
- **Write readable, maintainable code.** Favor clarity over cleverness.
- **Use meaningful naming.** Variables, functions, files, and folders must clearly describe their purpose. No abbreviations unless universally understood.

---

## 2. Backend Rules (FastAPI / Python)

### Layered Architecture

```
Router → Service → Repository → Database
```

- **Routers** handle HTTP concerns only: request parsing, response formatting, status codes. **Zero business logic in routers.**
- **Services** contain all business logic, orchestration, and validation beyond schema-level checks.
- **Repositories** are the only layer that touches the database. All queries live here.
- **Schemas** (Pydantic) define request/response shapes. Never pass raw dicts between layers.

### Module Independence

- Each module (`energy/`, `money/`, `hr/`, `medicine/`, `living_cost/`) must be fully self-contained.
- Cross-module imports are **forbidden** at the module level. Use shared utilities in `common/` instead.
- Adding a new domain module must **never** require modifying an existing module.

### Async Patterns

- All database operations must be async (`async def`, `await`).
- Use `AsyncSession` from SQLAlchemy 2.0 — never use synchronous sessions.
- Background tasks go through Celery, not FastAPI's `BackgroundTasks` (except for trivial fire-and-forget work).

### Database

- All schema changes go through **Alembic migrations**. Never modify tables manually.
- Use model mixins (`TimestampMixin`, etc.) for shared columns like `created_at`, `updated_at`.
- Always use the `Base` class from `app/db/base.py` for model declarations.

### Error Handling

- Use custom exception classes from `common/exceptions.py`.
- Never catch generic `Exception` silently. Log and re-raise or convert to a domain-specific error.

---

## 3. Frontend Rules (Next.js / TypeScript)

### App Router Discipline

- **`page.tsx` files must be thin.** They import and compose feature components — nothing more.
- **`layout.tsx`** handles shared chrome (nav, sidebar). No data fetching in layouts unless it applies to all child routes.
- Use **Server Components** by default. Only add `"use client"` when the component needs interactivity, browser APIs, or hooks.

### Feature-Based Structure

- Domain UI logic lives in `features/<domain>/` — not scattered across `components/`.
- Each feature folder owns its components, hooks, and types.
- Shared/reusable UI (buttons, cards, modals) lives in `components/ui/`.
- Chart components live in `components/charts/`.
- Layout primitives (sidebar, header) live in `components/layout/`.

### Data & State Management

- API calls live in `services/` — never inline fetch calls in components.
- Use **Zustand** for client-side global state. Keep stores minimal.
- Avoid prop drilling. If data must pass through more than 2 levels, use a hook or store.
- Colocate hooks with their feature when they're domain-specific. Shared hooks go in `hooks/`.

### Component Rules

- Keep components under ~150 lines. Extract sub-components when they grow.
- Every component must be independently testable.
- Prefer composition over configuration (small composable pieces over mega-components with many props).

### TypeScript

- **Strict mode is always on.** No `any` types unless absolutely unavoidable (and documented why).
- Define shared types in `types/`. Feature-specific types in `features/<domain>/types/`.
- API response types must mirror backend Pydantic schemas.

---

## 4. Scraper Rules

- Every scraper inherits from `BaseScraper` in `scrapers/src/core/base_scraper.py`.
- Scrapers are **domain-isolated**. Each domain folder contains only its own scrapers.
- Use the shared HTTP client (`core/http_client.py`) — never create ad-hoc HTTP sessions.
- All scrapers must implement retry logic via the `core/retry.py` utilities.
- Scrapers must be idempotent: running the same scraper twice for the same date must not create duplicates.
- Scrapers run as **Celery tasks** — they must be serializable and stateless.
- Store raw data before transformation when possible, for auditability.

---

## 5. Git & Code Quality

### Commit Messages

Follow **Conventional Commits** strictly:

```
type(scope): description

feat(energy): add fuel price endpoint
fix(money): correct exchange rate decimal precision
refactor(scrapers): extract shared retry logic
docs(api): update endpoint documentation
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`

### Git Hooks (Husky)

| Hook         | Action                                    |
| ------------ | ----------------------------------------- |
| `pre-commit` | Run linters and formatters on staged files |
| `commit-msg` | Validate conventional commit format        |

### Code Quality Tools

- **Backend**: `ruff` for linting and formatting (line length: 88).
- **Frontend**: `ESLint` + `Prettier` (print width: 100, double quotes, trailing commas).
- All linter warnings must be resolved before merging. Zero tolerance for `no-console` in production code.

### Pull Requests

- Every PR must target `develop` (not `main` directly).
- PRs require at least one approval before merging.
- All CI checks must pass (lint, test, build).

---

## 6. Scalability Rules

### Adding a New Domain

To add a new data domain (e.g., `education`):

1. Create `backend/app/modules/education/` with the standard sub-folders (`models/`, `schemas/`, `services/`, `repositories/`, `routers/`).
2. Create `scrapers/src/domains/education/` with domain-specific scrapers.
3. Create `frontend/src/features/education/` and add a route in `app/(dashboard)/education/`.
4. Register the router in `backend/app/main.py`.
5. Create an Alembic migration for new models.
6. **You must not modify any existing module to do this.**

### Database Migrations

- Every model change requires a migration. No exceptions.
- Migrations must be reversible (`upgrade` and `downgrade`).
- Test migrations against a fresh database before merging.

### Coupling

- Modules communicate through well-defined interfaces, never by importing internals.
- Frontend services are the only layer that knows about API URLs.
- Scrapers never import from the backend `app` package directly — they share the database via SQLAlchemy models or write through a storage abstraction.

---

## 7. Environment & Configuration

- **Never commit `.env` files.** Use `.env.example` as a template.
- All configuration is loaded from environment variables via `pydantic-settings`.
- Secrets (API keys, DB passwords) must never appear in code or commit history.
- Use separate configs per environment: `development`, `staging`, `production`.

---

## 8. Testing

- **Backend**: Use `pytest` with `pytest-asyncio`. Test services and repositories independently.
- **Frontend**: Use Jest + React Testing Library. Test feature components and hooks.
- **Scrapers**: Mock HTTP responses. Never hit real endpoints in tests.
- Aim for meaningful coverage, not 100% line coverage. Test business logic, edge cases, and error paths.

---

*These rules exist to keep AQ maintainable as it scales. When in doubt, ask: "Will this be easy to understand and modify 6 months from now?"*
