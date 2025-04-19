#!/bin/bash

echo "🔄 Corriendo collectstatic..."
python manage.py collectstatic --noinput

echo "🚀 Levantando Gunicorn..."
exec gunicorn tgbot.wsgi --log-file -
