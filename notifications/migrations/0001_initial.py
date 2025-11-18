from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient_email", models.EmailField(blank=True, max_length=254)),
                ("recipient_phone", models.CharField(blank=True, max_length=32)),
                ("recipient_telegram", models.CharField(blank=True, max_length=64)),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("channel_order", django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[("email", "Email"), ("sms", "SMS"), ("telegram", "Telegram")], max_length=16), blank=True, default=list, size=None)),
                ("channel_attempts", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("pending", "В очереди"), ("processing", "В обработке"), ("delivered", "Доставлено"), ("failed", "Ошибка")], default="pending", max_length=16)),
                ("last_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
