# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Backend for a physical cocktail-mixing machine ("CocktailMachine V2" / coma2). It's a small Flask + Flask-SQLAlchemy REST API backed by SQLite. Clients define drink recipes (cocktails), ingredients, and dispenser "slots" (the machine's physical ports, each loaded with one ingredient), and the API is used to check which cocktails can currently be made given what's loaded in the slots.

## Running the backend

Without Docker:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0
```

`.flaskenv` sets `FLASK_APP=coma2/main`, `FLASK_DEBUG=True`, and `FLASK_RUN_PORT=5055`, so `flask run` picks these up automatically (`flask-dotenv` support comes from `python-dotenv`). The API is served at `http://localhost:5055`.

With Docker: `docker-compose up` (builds from `Dockerfile`, maps port 5055, persists `/data` as a named volume).

There is no test suite, linter config, or CI in this repo. `autopep8`/`pycodestyle` are listed as dependencies but have no invoking config — if asked to lint, run `autopep8` or `pycodestyle` directly against changed files.

## Database

SQLite, file at `coma2/coma2.db`, URI defined in `coma2/constants.py` (`DATABASE_URI = "sqlite:///coma2.db"`). Schema is defined purely via the SQLAlchemy models — there are no migrations (no Alembic).

To (re)initialize the schema and seed sample data, run **`init_db.py`** (not `create_tables.py` — the latter is kept only for reference and has a circular-import problem when run standalone; the Docker image explicitly uses `init_db.py`, see the comment in `Dockerfile`). `init_db.py` drops and recreates all tables, then seeds two sample cocktails, three ingredients, and 16 empty slots.

Core tables (see `README.md` for full column-level detail):
- `cocktail` — id, timestamp, name
- `ingredient` — id, timestamp, name, alcohol_percentage
- `cocktail_ingredient` — many-to-many join table between cocktail and ingredient, with an `amount` column (composite PK of both foreign keys)
- `slot` — id, ingredient_id, amount_percentage — represents a physical dispenser slot on the machine and which ingredient (if any) is currently loaded into it. `ingredient_id = 0` means the slot is empty/unassigned (not a real FK relationship — there is no ingredient with id 0).

## Architecture

Flask app factory pattern is *not* used — `coma2/config.py` creates a single module-level `app` and `db` (SQLAlchemy) instance at import time, configured from `coma2/constants.py`. Every other module imports `app`/`db` from `coma2.config`.

`coma2/__init__.py` is the composition root: it imports `app`/`db` from `config`, then imports each feature module's blueprint and registers it. Import order matters here — blueprints are imported *after* `app`/`db` exist to avoid circular imports, which is why `init_db.py` and `create_tables.py` differ in how carefully they sequence imports.

Feature modules follow a consistent structure, each is a self-contained Flask Blueprint:
```
coma2/<feature>/
  models.py   # SQLAlchemy model(s), each with a `.serialize` property returning a plain dict for jsonify
  routes.py   # Blueprint with one route per resource, dispatching on request.method
```
- `coma2/cocktails/` — cocktail CRUD (create/list/delete) plus `/api/cocktails/available`, which computes which cocktails can currently be mixed by intersecting each cocktail's required ingredient ids against the ingredient ids currently loaded across all slots.
- `coma2/ingredients/` — ingredient CRUD. Deleting an ingredient cascades to delete any cocktail that uses it (see the `try/except` block in `handle_ingredient`'s DELETE case).
- `coma2/slots/` — slot listing and `PATCH`-based partial updates (update `ingredient_id` and/or `amount_percentage` independently). Setting `ingredient_id` to `0` explicitly clears a slot; any other id must reference an existing ingredient.

Route handlers follow one recurring pattern worth knowing before adding endpoints: a single route often handles multiple HTTP methods via `if request.method == "...":` branches rather than separate route functions, and duplicate-name checks precede inserts (cocktail names and ingredient names must be unique).

API docs: `coma2/docs/openapi.yml` is a hand-maintained OpenAPI spec, served at `/api/docs` via `flask-swagger-ui` (wired up in `coma2/docs/swagger.py`). When adding or changing an endpoint, update this file too. There is also a Postman collection at `coma2-backend.postman_collection.json` for manual testing.

## Ongoing refactor

Branch `refactor-codebase` is rewriting this backend on a modern stack (FastAPI, SQLAlchemy 2.0, Alembic, uv, Ruff, mypy, pytest). See `docs/refactor-requirements.md` for the agreed scope and decisions before making changes on this branch.

## Working conventions on this branch

- Commit in small, logical units (one coherent change per commit), using Conventional Commits messages (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`).
- Commit locally as you go; do not push until asked.
- Pause for review at each major checkpoint (e.g. after scaffolding, after each module) rather than running through the whole plan unattended.
