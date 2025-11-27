import logging
import json
import requests
from subscriptions.models import Subscription


logger = logging.getLogger(__name__)

def send_weather_webhook(subscription: Subscription, weather_data: dict):
    """Formats a JSON payload and sends it to the subscription's webhook URL"""
    if not subscription.webhook_url:
        logger.warning(f'Skipping webhook for subscription {subscription.id}: No URL provided.')
        return

    payload = {
        'event': 'weather_update',
        'subscription_id': subscription.id,
        'user_email': subscription.user.email,
        'city': subscription.city,
        'data': {
            'temperature': weather_data.get('main', {}).get('temp'),
            'feels_like': weather_data.get('main', {}).get('feels_like'),
            'description': weather_data.get('weather', [{}])[0].get('description', 'N/A'),
            'humidity': weather_data.get('main', {}).get('humidity'),
            'wind_speed': weather_data.get('wind', {}).get('speed'),
            'raw': weather_data,
        }
    }

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(subscription.webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f'Successfully sent webhook to {subscription.webhook_url} for {subscription.city}')
    except requests.exceptions.RequestException:
        logger.error(f'Error sending webhook to {subscription.webhook_url}', exc_info=True)