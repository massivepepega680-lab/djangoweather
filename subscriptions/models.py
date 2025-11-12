from django.conf import settings
from django.db import models


class Subscription(models.Model):
    class NotificationMethod(models.TextChoices):
        EMAIL = 'email', 'Email'
        WEBHOOK = 'webhook', 'Webhook'

    class NotificationPeriod(models.IntegerChoices):
        ONE_HOUR = 1, '1 Hour'
        THREE_HOURS = 3, '3 Hours'
        SIX_HOURS = 6, '6 Hours'
        TWELVE_HOURS = 12, '12 Hours'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    city = models.CharField(max_length=100)

    notification_period = models.IntegerField(choices=NotificationPeriod.choices)
    notification_method = models.CharField(max_length=10, choices=NotificationMethod.choices)

    webhook_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    last_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.city} ({self.get_notification_period_display()})"

    class Meta:
        unique_together = ('user', 'city', 'is_active')
