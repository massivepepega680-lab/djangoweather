release: python manage.py migrate
web: gunicorn project.wsgi --log-file -
worker: celery -A project.celery worker --loglevel=info
beat: celery -A project.celery beat --loglevel=info