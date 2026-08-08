FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies first so this layer is cached unless deps change.
# README.md is needed too: hatchling reads it as the package long_description.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV DATABASE_URL="sqlite:////data/coma2.db"

# Persist the sqlite db across container recreation
VOLUME /data

EXPOSE 5055

CMD ["sh", "-c", "alembic upgrade head && uvicorn coma2.main:app --host 0.0.0.0 --port 5055"]
