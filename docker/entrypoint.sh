set -eu

# Set RUN_MIGRATIONS=false on tasks that must not migrate.
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "[entrypoint] applying database migrations..."
    alembic upgrade head
fi

# number of Gunicorn workers.
WORKERS="${GUNICORN_WORKERS:-${WEB_CONCURRENCY:-4}}"

echo "[entrypoint] starting gunicorn with ${WORKERS} worker(s)..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WORKERS}" \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5
