python manage.py migrate
python manage.py collectstatic --noinput

echo "=== DIAGNOSTICS START ==="
echo "Current directory: $(pwd)"
echo "Listing files in /app:"
ls -la
echo "Checking Django project structure:"
python manage.py check --deploy 2>&1
echo "=== DIAGNOSTICS END ==="

exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT