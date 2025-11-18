import logging
from dataclasses import dataclass
from typing import Protocol

from django.conf import settings
from django.core.mail import send_mail

from notifications.models import Notification

logger = logging.getLogger(__name__)


class ChannelError(Exception):
    """Ошибка при отправке уведомления через конкретный канал."""


class Channel(Protocol):
    name: str

    def can_send(self, notification: Notification) -> bool:
        ...

    def send(self, notification: Notification) -> None:
        ...


@dataclass
class EmailChannel:
    name: str = Notification.Channel.EMAIL

    def can_send(self, notification: Notification) -> bool:
        return bool(notification.recipient_email)

    def send(self, notification: Notification) -> None:
        if self.name in settings.NOTIFICATION_SIMULATED_FAILURES:
            raise ChannelError("Симулированный отказ email-провайдера")

        send_mail(
            subject=notification.subject or "Уведомление",
            message=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient_email],
            fail_silently=False,
        )


@dataclass
class SmsChannel:
    name: str = Notification.Channel.SMS

    def can_send(self, notification: Notification) -> bool:
        return bool(notification.recipient_phone)

    def send(self, notification: Notification) -> None:
        if self.name in settings.NOTIFICATION_SIMULATED_FAILURES:
            raise ChannelError("Симулированный отказ SMS-провайдера")

        # Здесь должен быть вызов реального SMS-провайдера.
        logger.info(
            "Отправка SMS на %s: %s",
            notification.recipient_phone,
            notification.body,
        )


@dataclass
class TelegramChannel:
    name: str = Notification.Channel.TELEGRAM

    def can_send(self, notification: Notification) -> bool:
        return bool(notification.recipient_telegram)

    def send(self, notification: Notification) -> None:
        if self.name in settings.NOTIFICATION_SIMULATED_FAILURES:
            raise ChannelError("Симулированный отказ Telegram-провайдера")

        logger.info(
            "Отправка Telegram-сообщения %s: %s",
            notification.recipient_telegram,
            notification.body,
        )


def get_available_channels() -> list[Channel]:
    return [
        EmailChannel(),
        SmsChannel(),
        TelegramChannel(),
    ]
