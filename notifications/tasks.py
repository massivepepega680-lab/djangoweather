from celery import shared_task


@shared_task
def process_and_send_notifications():
    """Placeholder for the main periodic task that will be run by Celery Beat.
    Does nothing for now
    """
    print('Checking for due subscriptions...')
    return 'Notification check complete.'