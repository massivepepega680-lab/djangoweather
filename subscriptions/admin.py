from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'city',
        'notification_period',
        'notification_method',
        'is_active',
        'last_notified_at'
    )
    list_filter = ('is_active', 'notification_method', 'city')
    search_fields = ('city', 'user__email')
