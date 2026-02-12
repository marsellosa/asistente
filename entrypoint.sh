#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

echo "🔄 Running collectstatic..."
python manage.py collectstatic --noinput

# Set workers based on WEB_CONCURRENCY or default to 3
WORKERS=${WEB_CONCURRENCY:-3}
PORT=${PORT:-8000}

echo "🚀 Starting Gunicorn with $WORKERS workers on port $PORT..."
exec gunicorn tgbot.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --threads 2 \
    --log-level info \
    --log-file -

