# Backend Refactor Requirements

Status: agreed direction as of 2026-08-08, branch `refactor-codebase`. This document
is the reference for the rewrite; update it if a decision changes during implementation.

## Goals

Rebuild the coma2 backend on a modern Python stack, without over-engineering for
scale this project doesn't need. It's a single Flask+SQLite API that will become a
single FastAPI+SQLite API, running on one Raspberry Pi for one household.

## Non-goals

- No GPIO/hardware control (pumps, motors, sensors) — this backend stays data/API
  only. Hardware control lives elsewhere, now or in the future.
- No authentication/authorization — local network, single trusted user.
- No multi-instance / horizontal scaling concerns.
- No migration of existing `coma2.db` contents — it only holds sample data.
- Frontend changes are tracked separately (frontend will be refactored in parallel,
  coordinated but not part of this repo's work).

## Stack

| Concern | Choice | Replaces |
|---|---|---|
| Language/runtime | Python 3.12 | Python 3.9 |
| Web framework | FastAPI | Flask |
| ORM | SQLAlchemy 2.0-style | SQLAlchemy 1.4 |
| Database | SQLite (unchanged) | — |
| Migrations | Alembic | none (drop/recreate) |
| Validation | Pydantic v2 (via FastAPI) | manual `if` checks in routes |
| Config | pydantic-settings (env vars / `.env`) | `coma2/constants.py` |
| Dependency/venv mgmt | uv | pip + venv + requirements.txt |
| Lint/format | Ruff | autopep8 / pycodestyle (unused in practice) |
| Type checking | mypy | none |
| Tests | pytest, real SQLite (temp file/in-memory) | none |
| API docs | FastAPI auto-generated OpenAPI/Swagger UI | hand-maintained `openapi.yml` |
| Deployment | Docker + docker-compose (kept) | — |
| CI | GitHub Actions: ruff + mypy + pytest on push/PR | none |

## Project structure

Keep the feature-folder layout, modernized per module:

```
app/
  cocktails/
    router.py   # FastAPI routes
    models.py   # SQLAlchemy ORM models
    schemas.py  # Pydantic request/response models
  ingredients/
    router.py
    models.py
    schemas.py
  slots/
    router.py
    models.py
    schemas.py
  config.py     # FastAPI app instance, settings, DB engine/session
  main.py       # composition root: creates app, includes routers
alembic/        # migration environment + versions
```

## Data model

Same core entities as today, carried forward:

- `Cocktail` — id, timestamp, name
- `Ingredient` — id, timestamp, name, alcohol_percentage
- `CocktailIngredient` — join table (cocktail_id, ingredient_id, amount)
- `Slot` — id, ingredient_id, amount_percentage (`ingredient_id = 0` = empty slot)

Schema is defined via SQLAlchemy models and managed by Alembic from an initial
migration. A seed script recreates the sample data currently in `init_db.py`
(2 cocktails, 3 ingredients, 16 empty slots).

## Behavior changes (closing known gaps)

The current code has a few gaps called out in TODOs and error handling; these get
fixed as part of the rewrite rather than carried forward:

- Add delete-cocktail-by-id (today's DELETE only works by id already, but there's
  no update endpoint at all) and add cocktail edit/update.
- When an ingredient is deleted, cascade-clear any slot referencing it
  (`ingredient_id -> 0`) instead of leaving a dangling reference.
- Replace bare `except: pass` blocks with explicit handling.
- Enforce validation via Pydantic schemas: percentages constrained 0–100,
  names non-empty, duplicate-name checks handled consistently.

The API contract (routes, request/response shapes) is free to be redesigned — it
does not need to match the current Flask API — but the resulting shape must be
fully captured by the auto-generated OpenAPI docs, since the frontend refactor will
depend on them as the source of truth.

## Testing

pytest suite covering:

- CRUD for cocktails, ingredients, slots
- The "available cocktails" computation (intersection of required vs. loaded
  ingredient ids)
- Cascade behaviors (ingredient delete → dependent cocktail delete → slot clear)
- Validation error paths (422 responses)

Tests run against a real SQLite database (temp file or in-memory per test), not
mocks.

## Deployment

Docker/docker-compose remains the run method on the Pi. Dockerfile is updated to a
current Python base image and uv-based install. GitHub Actions runs lint, type
check, and tests on push/PR.
