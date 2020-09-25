cd /app
gunicorn --timeout 600 --bind 0.0.0.0:8000 --log-level=DEBUG wsgi:app

