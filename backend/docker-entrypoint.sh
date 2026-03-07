#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput

# Диагностика
echo "=== DIAGNOSTICS START ==="
echo "Current directory: $(pwd)"
echo "Listing files in /app:"
ls -la
echo "Checking Django project structure:"
python manage.py check --deploy 2>&1
echo "Testing database connection:"
python manage.py dbshell 2>&1 || echo "Database connection failed"
echo "=== DIAGNOSTICS END ==="

exec "$@"