from django.db import models
from django.contrib.postgres.fields import ArrayField


class Notification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В очереди"
        PROCESSING = "processing", "В обработке"
        DELIVERED = "delivered", "Доставлено"
        FAILED = "failed", "Ошибка"

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        TELEGRAM = "telegram", "Telegram"

    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=32, blank=True)
    recipient_telegram = models.CharField(max_length=64, blank=True)

    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()

    metadata = models.JSONField(default=dict, blank=True)
    channel_order = ArrayField(
        models.CharField(max_length=16, choices=Channel.choices),
        default=list,
        blank=True,
    )
    channel_attempts = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Notification #{self.pk} ({self.status})"

    def has_destination(self) -> bool:
        return any(
            [
                bool(self.recipient_email),
                bool(self.recipient_phone),
                bool(self.recipient_telegram),
            ]
        )
