#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h db -U postgres; do
  sleep 1
done
echo "PostgreSQL is ready!"

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000