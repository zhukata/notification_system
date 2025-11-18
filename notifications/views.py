from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.tasks import process_notification


class NotificationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Notification.objects.order_by("-created_at")
    serializer_class = NotificationSerializer

    def perform_create(self, serializer: NotificationSerializer) -> None:
        notification = serializer.save()
        process_notification.delay(notification.pk)

    @action(methods=["post"], detail=True)
    def retry(self, request, pk=None):
        notification = self.get_object()
        notification.status = Notification.Status.PENDING
        notification.channel_attempts = []
        notification.last_error = ""
        notification.save(
            update_fields=[
                "status",
                "channel_attempts",
                "last_error",
                "updated_at"
            ]
        )
        process_notification.delay(notification.pk)
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
