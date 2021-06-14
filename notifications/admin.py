from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'notification_type',
        'business_account',
        'action_date',
        'is_seen'
    )
    list_filter = ('action_date', 'is_seen')
    search_fields = ('notication_type', 'action')

