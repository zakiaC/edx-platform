import json

from django.conf import settings
from django.db import models
from django.utils import timezone


class InternalMessageAudit(models.Model):
    STATUS_QUEUED = "queued"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_QUEUED, "Queued"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mission_internal_messages",
    )
    recipient_group = models.CharField(max_length=64, db_index=True)
    recipient_count = models.PositiveIntegerField(default=0)
    recipients_json = models.TextField(default="[]")
    subject = models.CharField(max_length=180)
    body = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_QUEUED, db_index=True)
    task_id = models.CharField(max_length=255, blank=True, default="")
    sent_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "mission_central_admin"
        ordering = ("-created",)

    def recipients(self):
        try:
            parsed = json.loads(self.recipients_json or "[]")
        except Exception:  # pylint: disable=broad-except
            return []
        return [str(item).strip().lower() for item in parsed if str(item).strip()]
