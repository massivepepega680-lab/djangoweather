release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn project.wsgi -b 0.0.0.0:$PORT --log-file -
worker: celery -A project.celery worker --loglevel=info
beat: celery -A project.celery beat --loglevel=info