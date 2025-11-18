from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "status",
        "recipient_email",
        "recipient_phone",
        "recipient_telegram",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "id",
        "recipient_email",
        "recipient_phone",
        "recipient_telegram",
        "subject",
    )
