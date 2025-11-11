import requests
from django.conf import settings


class WeatherClient:
    BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

    def __init__(self):
        self.api_key = settings.OPENWEATHERMAP_API_KEY
        if not self.api_key:
            raise ValueError('OPENWEATHERMAP_API_KEY is not set in environment variables.')

    def get_weather(self, city: str):
        """Fetches the current weather for a given city.
        Returns the JSON response or None if an error occurs
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Or 'imperial'
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching weather for {city}: {e}')
            return None