from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.utils import timezone

from celery import shared_task

from openedx.core.djangoapps.notifications.models import Notification
from .models import InternalMessageAudit


def _clean_text(value, limit):
    text = strip_tags(str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _create_web_notifications(audit, recipients):
    """
    Create in-platform notifications for recipients, so the message is visible
    in Mission dashboards and Open edX notifications API.
    """
    if not recipients:
        return 0

    User = get_user_model()
    users_by_email = {
        (user.email or "").strip().lower(): user
        for user in User.objects.filter(email__in=recipients, is_active=True).exclude(email__exact="")
    }

    sender = audit.sender
    sender_name = "Mission Formations"
    if sender:
        sender_name = sender.get_full_name().strip() or sender.username or sender_name

    safe_subject = _clean_text(audit.subject, 120) or "Message interne"
    safe_preview = _clean_text(audit.body, 200)
    message_line = f"Nouveau message de {sender_name}: {safe_subject}"
    if safe_preview:
        message_line = f"{message_line} — {safe_preview}"

    notifications = []
    created_ts = timezone.now()
    group_key = f"mission-msg-{audit.id}"
    for email in recipients:
        user = users_by_email.get((email or "").strip().lower())
        if not user:
            continue
        notifications.append(
            Notification(
                user=user,
                course_id=None,
                app_name="updates",
                notification_type="course_updates",
                content_context={
                    "course_update_content": message_line,
                    "mf_internal_message": True,
                    "sender_name": sender_name,
                    "subject": safe_subject,
                    "audit_id": audit.id,
                },
                content_url="/notifications/interne/",
                web=True,
                email=False,
                group_by_id=group_key,
                created=created_ts,
            )
        )

    if notifications:
        Notification.objects.bulk_create(notifications, batch_size=500)
    return len(notifications)


@shared_task(bind=True, max_retries=0)
def send_internal_message_task(self, audit_id):
    try:
        audit = InternalMessageAudit.objects.select_related("sender").get(id=audit_id)
    except InternalMessageAudit.DoesNotExist:
        return {"status": "missing", "audit_id": audit_id}

    if audit.status == InternalMessageAudit.STATUS_SENT:
        return {"status": "already_sent", "audit_id": audit_id, "sent_count": audit.sent_count}

    recipients = audit.recipients()
    if not recipients:
        audit.status = InternalMessageAudit.STATUS_FAILED
        audit.error_message = "Aucun destinataire valide."
        audit.sent_at = timezone.now()
        audit.save(update_fields=["status", "error_message", "sent_at", "modified"])
        return {"status": "failed", "audit_id": audit_id, "error": audit.error_message}

    sender = audit.sender
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@local.openedx.io"
    reply_to = [sender.email] if sender and (sender.email or "").strip() else None
    full_subject = f"[Mission Formations] {audit.subject}"

    sent_total = 0
    try:
        for start in range(0, len(recipients), 150):
            chunk = recipients[start:start + 150]
            message = EmailMessage(
                subject=full_subject,
                body=audit.body,
                from_email=from_email,
                to=[from_email],
                bcc=chunk,
                reply_to=reply_to,
            )
            message.send(fail_silently=False)
            sent_total += len(chunk)

        _create_web_notifications(audit, recipients)

        audit.status = InternalMessageAudit.STATUS_SENT
        audit.sent_count = sent_total
        audit.error_message = ""
        audit.sent_at = timezone.now()
        audit.save(update_fields=["status", "sent_count", "error_message", "sent_at", "modified"])
        return {"status": "sent", "audit_id": audit_id, "sent_count": sent_total}
    except Exception as exc:  # pylint: disable=broad-except
        audit.status = InternalMessageAudit.STATUS_FAILED
        audit.error_message = str(exc)
        audit.sent_at = timezone.now()
        audit.save(update_fields=["status", "error_message", "sent_at", "modified"])
        raise
