from celery import shared_task
from django.db import transaction

from notifications.models import Notification
from notifications.services.delivery import NotificationDeliveryService


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=5,
    retry_jitter=True,
)
def process_notification(notification_id: int) -> bool:
    try:
        notification = Notification.objects.get(pk=notification_id)
    except Notification.DoesNotExist:
        return False

    service = NotificationDeliveryService()
    with transaction.atomic():
        if notification.status == Notification.Status.PENDING:
            notification.status = Notification.Status.PROCESSING
            notification.save(update_fields=["status", "updated_at"])

    return service.send(notification)
