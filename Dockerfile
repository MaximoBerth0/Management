# single source of truth for the interpreter version across both stages
ARG PYTHON_VERSION=3.14.5

# builder
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# build deps needed to compile any wheels (argon2-cffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

# install ONLY the locked runtime deps into ./.venv (no dev deps, no project root)
RUN poetry install --only main --no-root

# runtime
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    WEB_CONCURRENCY=4

WORKDIR /app

# bring over only the virtualenv — no build tools, no poetry, no apt caches
COPY --from=builder /app/.venv /app/.venv

# non-root user
RUN useradd --create-home --uid 1000 appuser

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

USER appuser

EXPOSE 8000

# gunicorn supervising Uvicorn workers. Worker count = WEB_CONCURRENCY.
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]