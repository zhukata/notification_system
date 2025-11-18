from django.conf import settings
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    channel_order = serializers.ListField(
        child=serializers.ChoiceField(choices=Notification.Channel.choices),
        required=False,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient_email",
            "recipient_phone",
            "recipient_telegram",
            "subject",
            "body",
            "metadata",
            "channel_order",
            "channel_attempts",
            "status",
            "last_error",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "channel_attempts",
            "status",
            "last_error",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        recipients = {
            "email": attrs.get("recipient_email"),
            "sms": attrs.get("recipient_phone"),
            "telegram": attrs.get("recipient_telegram"),
        }
        if not any(recipients.values()):
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один способ связи: email, телефон или Telegram."
            )

        requested_order = attrs.get("channel_order")
        if requested_order:
            cleaned_order = []
            for channel in requested_order:
                if (
                    channel == Notification.Channel.EMAIL
                    and not recipients["email"]
                ):
                    raise serializers.ValidationError(
                        "Нельзя выбрать email без адреса."
                    )
                if (
                    channel == Notification.Channel.SMS
                    and not recipients["sms"]
                ):
                    raise serializers.ValidationError(
                        "Нельзя выбрать SMS без номера телефона."
                    )
                if (
                    channel == Notification.Channel.TELEGRAM
                    and not recipients["telegram"]
                ):
                    raise serializers.ValidationError(
                        "Нельзя выбрать Telegram без username или chat_id."
                    )
                if channel not in cleaned_order:
                    cleaned_order.append(channel)
            attrs["channel_order"] = cleaned_order
        return attrs

    def create(self, validated_data):
        channel_order = validated_data.get("channel_order")
        if not channel_order:
            channel_order = settings.NOTIFICATION_DEFAULT_CHANNEL_ORDER

        recipients = {
            Notification.Channel.EMAIL: validated_data.get("recipient_email"),
            Notification.Channel.SMS: validated_data.get("recipient_phone"),
            Notification.Channel.TELEGRAM: validated_data.get(
                "recipient_telegram"
            ),
        }
        filtered_order = [
            channel for channel in channel_order if recipients.get(channel)
        ]

        if not filtered_order:
            raise serializers.ValidationError(
                "Не удалось определить доступные каналы доставки для выбранных контактов."
            )

        validated_data["channel_order"] = filtered_order
        return super().create(validated_data)
