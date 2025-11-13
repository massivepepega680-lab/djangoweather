release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn Task_17_Basic_Weather_Reminder.wsgi -b 0.0.0.0:$PORT --log-file -
worker: celery -A Task_17_Basic_Weather_Reminder.celery worker --loglevel=info
beat: celery -A Task_17_Basic_Weather_Reminder.celery beat --loglevel=info