from rest_framework import serializers
from .models import Subscription


class CaseInsensitiveChoiceField(serializers.ChoiceField):
    """A custom ChoiceField that converts incoming data to lowercase
    before validation
    """
    def to_internal_value(self, data):
        data = str(data).lower()
        return super().to_internal_value(data)

class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.ReadOnlyField(source='user.email')
    notification_method = CaseInsensitiveChoiceField(choices=Subscription.NotificationMethod.choices)

    class Meta:
        model = Subscription
        fields = [
            'url', 'id', 'user', 'city', 'notification_period',
            'notification_method', 'webhook_url', 'is_active',
            'last_notified_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_notified_at', 'created_at', 'updated_at']

        extra_kwargs = {
            'url': {'view_name': 'subscription-detail', 'lookup_field': 'pk'}
        }

    def validate(self, data):
        """Check that webhook_url is provided
        if notification_method is 'webhook'
        """
        method = data.get('notification_method')
        url = data.get('webhook_url')

        if method == 'webhook' and not url:
            raise serializers.ValidationError(
                {'webhook_url': 'Webhook URL is required for the webhook notification method.'}
            )
        if method == 'email':
            data['webhook_url'] = None
        return data

    def validate_city(self, value):
        """Normalizes the city name to a consistent format
        - Removes leading/trailing whitespace
        - Capitalizes the city in title case (e.g., 'new york' -> 'New York')
        """
        if not isinstance(value, str):
            raise serializers.ValidationError('City must be a string.')
        return value.strip().title()