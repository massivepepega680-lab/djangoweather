release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn project.wsgi -b 0.0.0.0:$PORT --log-file -
worker: celery -A project worker --loglevel=info --concurrency=4
beat: celery -A project beat --loglevel=info