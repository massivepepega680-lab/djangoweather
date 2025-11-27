import logging
import os  # <-- ADD THIS IMPORT
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from subscriptions.models import Subscription
from .services.email_sender import send_weather_email
from .services.weather_client import WeatherClient
from .services.webhook_sender import send_weather_webhook

logger = logging.getLogger(__name__)

@shared_task
def process_and_send_notifications():
    """The main periodic task, optimized to fetch weather for each city only once.
    Adapts its scheduling logic based on environment variables for testing.
    """
    now = timezone.now()

    # --- START OF MODIFIED SECTION ---

    # Check if we are in a custom testing schedule by looking for the env var.
    is_testing_mode = os.getenv('CELERY_BEAT_MINUTE_SCHEDULE') is not None

    logger.info(f"Running optimized notification task (Testing Mode: {is_testing_mode})")

    active_subscriptions = Subscription.objects.filter(is_active=True)
    if not active_subscriptions:
        logger.info("No active subscriptions to process.")
        return "Task complete: No active subscriptions."

    due_subscriptions = []
    cities_to_fetch = set()

    for sub in active_subscriptions:
        if is_testing_mode:
            # --- TESTING LOGIC ---
            # In testing mode, send if ~15 minutes have passed since the last notification.
            # We use 14 minutes as a buffer to prevent race conditions with the scheduler.
            is_due = (
                sub.last_notified_at is None or
                sub.last_notified_at <= now - timedelta(minutes=14)
            )
        else:
            # --- PRODUCTION LOGIC ---
            # In production, use the fixed hourly schedule.
            current_hour = now.hour
            is_scheduled_hour = (current_hour % sub.notification_period) == 0
            sent_this_hour = (
                    sub.last_notified_at is not None and
                    sub.last_notified_at >= now - timedelta(hours=1)
            )
            is_due = is_scheduled_hour and not sent_this_hour

        if is_due:
            due_subscriptions.append(sub)
            cities_to_fetch.add(sub.city)

    # --- END OF MODIFIED SECTION ---

    if not due_subscriptions:
        logger.info('No subscriptions are due for notification at this time.')
        return 'Task complete: No due subscriptions.'

    logger.info(f'Found {len(due_subscriptions)} due subscriptions for {len(cities_to_fetch)} unique cities.')

    weather_client = WeatherClient()
    weather_data_map = {}

    logger.info(f'Fetching weather for cities: {list(cities_to_fetch)}')
    for city in cities_to_fetch:
        weather_data_map[city] = weather_client.get_weather(city)

    notifications_sent = 0
    for sub in due_subscriptions:
        weather_data = weather_data_map.get(sub.city)

        if weather_data:
            logger.info(f"Distributing notification for '{sub.city}' (ID: {sub.id})")
            if sub.notification_method == Subscription.NotificationMethod.EMAIL:
                send_weather_email(sub, weather_data)
            elif sub.notification_method == Subscription.NotificationMethod.WEBHOOK:
                send_weather_webhook(sub, weather_data)

            sub.last_notified_at = now
            sub.save(update_fields=['last_notified_at'])
            notifications_sent += 1
        else:
            logger.warning(f"Skipping distribution for '{sub.city}' (ID: {sub.id}): No weather data was fetched.")

    final_message = (f'Task complete: Processed {len(due_subscriptions)} due subscriptions. '
                     f'Sent {notifications_sent} notifications.')
    logger.info(final_message)
    return final_message