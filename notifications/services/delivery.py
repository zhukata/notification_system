from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db import transaction

from notifications.models import Notification

from .channels import ChannelError, get_available_channels

logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    def __init__(self) -> None:
        self.channels = {channel.name: channel for channel in get_available_channels()}

    def send(self, notification: Notification) -> bool:
        channel_order = (
            notification.channel_order or settings.NOTIFICATION_DEFAULT_CHANNEL_ORDER
        )
        attempts: list[dict[str, Any]] = list(notification.channel_attempts or [])

        available_channels = [
            channel_name
            for channel_name in channel_order
            if channel_name in self.channels
        ]

        if not available_channels:
            notification.status = Notification.Status.FAILED
            notification.last_error = "Нет доступных каналов отправки"
            notification.channel_attempts = attempts
            notification.save(
                update_fields=["status", "last_error", "channel_attempts", "updated_at"]
            )
            return False

        with transaction.atomic():
            notification.status = Notification.Status.PROCESSING
            notification.save(update_fields=["status", "updated_at"])

        for channel_name in available_channels:
            channel = self.channels[channel_name]
            if not channel.can_send(notification):
                continue

            try:
                channel.send(notification)
            except ChannelError as exc:
                logger.warning(
                    "Ошибка при отправке уведомления %s через %s: %s",
                    notification.pk,
                    channel_name,
                    exc,
                )
                attempts.append(
                    {"channel": channel_name, "status": "failed", "error": str(exc)}
                )
                notification.channel_attempts = attempts
                notification.last_error = str(exc)
                notification.save(
                    update_fields=["channel_attempts", "last_error", "updated_at"]
                )
                continue

            attempts.append({"channel": channel_name, "status": "success"})
            notification.channel_attempts = attempts
            notification.status = Notification.Status.DELIVERED
            notification.last_error = ""
            notification.save(
                update_fields=[
                    "status",
                    "channel_attempts",
                    "last_error",
                    "updated_at",
                ]
            )
            return True

        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status", "updated_at"])
        return False


def send_notification(notification_id: int) -> bool:
    notification = Notification.objects.get(pk=notification_id)
    service = NotificationDeliveryService()
    return service.send(notification)
