from django.test import TestCase, override_settings

from notifications.models import Notification
from notifications.services.delivery import NotificationDeliveryService


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class NotificationDeliveryServiceTests(TestCase):
    @override_settings(NOTIFICATION_SIMULATED_FAILURES={"email"})
    def test_fallback_to_sms(self):
        notification = Notification.objects.create(
            recipient_email="user@example.com",
            recipient_phone="+1000000000",
            body="Test message",
            channel_order=["email", "sms"],
        )

        service = NotificationDeliveryService()
        result = service.send(notification)

        self.assertTrue(result)
        notification.refresh_from_db()
        self.assertEqual(notification.status, Notification.Status.DELIVERED)
        self.assertEqual(notification.channel_attempts[-1]["channel"], "sms")
