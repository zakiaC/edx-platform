from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InternalMessageAudit",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient_group", models.CharField(db_index=True, max_length=64)),
                ("recipient_count", models.PositiveIntegerField(default=0)),
                ("recipients_json", models.TextField(default="[]")),
                ("subject", models.CharField(max_length=180)),
                ("body", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")],
                        db_index=True,
                        default="queued",
                        max_length=16,
                    ),
                ),
                ("task_id", models.CharField(blank=True, default="", max_length=255)),
                ("sent_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True, default="")),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mission_internal_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created",),
            },
        ),
    ]
