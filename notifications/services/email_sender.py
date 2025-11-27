import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from subscriptions.models import Subscription


logger = logging.getLogger(__name__)

def send_weather_email(subscription: Subscription, weather_data: dict):
    """Renders the weather email template with context and sends it"""
    subject = f'Your Weather Update for {subscription.city}'

    context = {
        'city': subscription.city,
        'temperature': weather_data.get('main', {}).get('temp'),
        'feels_like': weather_data.get('main', {}).get('feels_like'),
        'description': weather_data.get('weather', [{}])[0].get('description', 'N/A').capitalize(),
        'humidity': weather_data.get('main', {}).get('humidity'),
        'wind_speed': weather_data.get('wind', {}).get('speed'),
    }

    html_message = render_to_string('notifications/weather_email.html', context)

    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Successfully sent weather email to {subscription.user.email} for {subscription.city}')
    except Exception:
        logger.error(f'Error sending email to {subscription.user.email}', exc_info=True)