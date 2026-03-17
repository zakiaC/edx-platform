from collections import defaultdict
import csv
import json
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.decorators.http import require_http_methods

from common.djangoapps.edxmako.shortcuts import render_to_response
from common.djangoapps.student.models import CourseAccessRole, CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.notifications.models import Notification
from .models import InternalMessageAudit
from .tasks import send_internal_message_task

ROLE_NAMES = ("instructor", "staff", "limited_staff")
FRENCH_MONTHS = ("Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec")


def _normalize(value):
    return (value or "").strip().lower()


def _initials(label):
    source = (label or "").strip()
    if not source:
        return "MF"
    parts = [p for p in source.split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return source[:2].upper()


def _format_day_month(dt_value):
    if not dt_value:
        return ("--", "---")
    month_idx = max(1, min(12, int(dt_value.month))) - 1
    return (f"{dt_value.day:02d}", FRENCH_MONTHS[month_idx])


def _course_specialty(course_name):
    name_l = _normalize(course_name)
    if "vtc" in name_l:
        return "Reglementation VTC"
    if any(token in name_l for token in ("it", "dev", "devops", "data", "python")):
        return "Academie IT"
    if any(token in name_l for token in ("marketing", "seo", "social")):
        return "Marketing digital"
    if any(token in name_l for token in ("management", "business")):
        return "Management"
    return "Formation professionnelle"


def _activity_time_ago(value):
    if not value:
        return "--"
    return timesince(value, timezone.now()).split(",")[0]


def _person_name(user):
    first = (getattr(user, "first_name", "") or "").strip()
    last = (getattr(user, "last_name", "") or "").strip()
    full = f"{first} {last}".strip()
    if full:
        return full

    email = (getattr(user, "email", "") or "").strip()
    username = (getattr(user, "username", "") or "").strip()
    seed = email.split("@", 1)[0] if email else username
    seed = seed.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    if seed:
        return " ".join(part.capitalize() for part in seed.split())
    return username or "Formateur"


def _admin_allowed(user):
    return bool(user and user.is_authenticated and user.is_superuser)


def _staff_allowed(user):
    return bool(user and user.is_authenticated and user.is_staff)


def _resolve_mapping_courses(mapping_value, overviews):
    if isinstance(mapping_value, str):
        values = [mapping_value]
    elif isinstance(mapping_value, (list, tuple)):
        values = list(mapping_value)
    else:
        return []

    selected = []
    seen = set()
    for raw in values:
        token = str(raw or "").strip()
        if not token:
            continue
        token_l = token.lower()
        for overview in overviews:
            course_id = str(overview.id).strip()
            display_name = (
                getattr(overview, "display_name_with_default", None)
                or getattr(overview, "display_name", None)
                or ""
            ).strip()
            if token == course_id or token_l in course_id.lower() or token_l in display_name.lower():
                if course_id in seen:
                    continue
                seen.add(course_id)
                selected.append(course_id)
    return selected


def _managed_course_ids_for_user(user):
    managed_ids = set(
        str(course_id)
        for course_id in CourseAccessRole.objects.filter(
            user=user,
            role__in=ROLE_NAMES,
        ).exclude(course_id=None).values_list("course_id", flat=True)
    )

    mapping = getattr(settings, "MISSION_FORMATIONS_FORMATEURS_FORMATIONS", {}) or {}
    lookup_keys = {_normalize(getattr(user, "email", "")), _normalize(getattr(user, "username", ""))}
    mapping_value = None
    for key, value in mapping.items():
        if _normalize(str(key)) in lookup_keys:
            mapping_value = value
            break

    if mapping_value is not None:
        overviews = list(CourseOverview.objects.order_by("-start")[:1200])
        if isinstance(mapping_value, str) and mapping_value.strip().upper() == "ALL" and getattr(user, "is_superuser", False):
            managed_ids.update(str(overview.id) for overview in overviews)
        else:
            managed_ids.update(_resolve_mapping_courses(mapping_value, overviews))

    return managed_ids


def _collect_formateur_users():
    User = get_user_model()
    users_by_id = {}

    for access_role in CourseAccessRole.objects.filter(role__in=ROLE_NAMES).exclude(course_id=None).select_related("user"):
        role_user = access_role.user
        if not role_user or role_user.is_superuser or not role_user.is_active:
            continue
        if not (role_user.email or "").strip():
            continue
        users_by_id[role_user.id] = role_user

    mapping = getattr(settings, "MISSION_FORMATIONS_FORMATEURS_FORMATIONS", {}) or {}
    for key in mapping.keys():
        lookup = _normalize(str(key))
        if not lookup:
            continue
        mapped_user = User.objects.filter(email__iexact=lookup).first() or User.objects.filter(username=lookup).first()
        if not mapped_user or mapped_user.is_superuser or not mapped_user.is_active:
            continue
        if not (mapped_user.email or "").strip():
            continue
        users_by_id[mapped_user.id] = mapped_user

    return list(users_by_id.values())


def _build_group_payload(key, label, description, users):
    emails = sorted(
        {
            (email or "").strip().lower()
            for email in (user.email for user in users)
            if (email or "").strip()
        }
    )
    return {
        "key": key,
        "label": label,
        "description": description,
        "count": len(emails),
        "emails": emails,
    }


def _messaging_groups_for_user(user):
    User = get_user_model()
    groups = []

    admin_users = list(
        User.objects.filter(is_active=True, is_superuser=True).exclude(email__exact="")
    )

    if user.is_superuser:
        learner_ids = CourseEnrollment.objects.filter(
            is_active=True,
            user__is_staff=False,
            user__is_superuser=False,
        ).values_list("user_id", flat=True).distinct()
        learner_users = list(
            User.objects.filter(id__in=learner_ids, is_active=True).exclude(email__exact="")
        )
        formateur_users = _collect_formateur_users()

        groups.append(
            _build_group_payload(
                "learners_all",
                "Groupe apprenants (tous les cours)",
                "Tous les apprenants actifs inscrits sur la plateforme.",
                learner_users,
            )
        )
        groups.append(
            _build_group_payload(
                "formateurs_all",
                "Groupe formateurs",
                "Tous les formateurs détectés sur les cours et le mapping Mission.",
                formateur_users,
            )
        )
        groups.append(
            _build_group_payload(
                "admins_global",
                "Groupe admins",
                "Tous les comptes superadmin de la plateforme.",
                admin_users,
            )
        )
        return groups

    managed_course_ids = _managed_course_ids_for_user(user)
    if managed_course_ids:
        learner_ids = CourseEnrollment.objects.filter(
            is_active=True,
            course_id__in=managed_course_ids,
            user__is_staff=False,
            user__is_superuser=False,
        ).values_list("user_id", flat=True).distinct()
        learner_users = list(
            User.objects.filter(id__in=learner_ids, is_active=True).exclude(email__exact="")
        )
    else:
        learner_users = []

    groups.append(
        _build_group_payload(
            "learners_managed",
            "Groupe apprenants (mes formations)",
            "Apprenants inscrits sur vos formations.",
            learner_users,
        )
    )
    groups.append(
        _build_group_payload(
            "admins_global",
            "Groupe admins",
            "Admins Mission Formations.",
            admin_users,
        )
    )
    return groups


def _recent_message_audits(user):
    queryset = InternalMessageAudit.objects.select_related("sender")
    if not user.is_superuser:
        queryset = queryset.filter(sender=user)
    audits = []
    for item in queryset[:12]:
        status_label = "En file d'envoi"
        if item.status == InternalMessageAudit.STATUS_SENT:
            status_label = "Envoye"
        elif item.status == InternalMessageAudit.STATUS_FAILED:
            status_label = "Echec"
        audits.append(
            {
                "created_text": (item.created or timezone.now()).strftime("%d/%m/%Y %H:%M"),
                "group": item.recipient_group,
                "subject": item.subject,
                "count": item.recipient_count,
                "sent_count": item.sent_count,
                "status": item.status,
                "status_label": status_label,
                "error_message": item.error_message or "",
            }
        )
    return audits


def _internal_notifications_for_user(user):
    notifications = Notification.objects.filter(
        user_id=user.id,
    ).order_by("-created")[:50]
    rows = []
    for notif in notifications:
        ctx = notif.content_context or {}
        is_internal = bool(ctx.get("mf_internal_message"))
        sender_name = (
            ctx.get("sender_name")
            or ctx.get("from")
            or ctx.get("author_name")
            or "Equipe Mission"
        )
        subject = (
            ctx.get("subject")
            or ctx.get("title")
            or ctx.get("headline")
            or ""
        )
        message = (
            ctx.get("course_update_content")
            or ctx.get("message")
            or ctx.get("body")
            or ctx.get("text")
            or ""
        )
        if not subject:
            if is_internal:
                subject = "Message interne"
            else:
                subject = "Notification Open edX"
        if not message:
            message = subject
        source_label = "Mission interne" if is_internal else "Open edX"
        base_url = notif.content_url or "/notifications/interne/"
        open_url = f"/notifications/interne/?open={notif.id}"
        rows.append(
            {
                "id": notif.id,
                "sender_name": sender_name,
                "subject": subject,
                "message": message,
                "title": "Nouveau message de {}".format(sender_name) if is_internal else subject,
                "description": message,
                "time": _activity_time_ago(notif.created),
                "created_text": (notif.created or timezone.now()).strftime("%d/%m/%Y %H:%M"),
                "unread": not bool(notif.last_read),
                "content_url": base_url,
                "open_url": open_url,
                "source": source_label,
                "is_internal": is_internal,
            }
        )
    return rows


def _to_positive_int(value):
    try:
        parsed = int(value)
    except Exception:  # pylint: disable=broad-except
        return None
    return parsed if parsed > 0 else None


def _match_formateur_row(identifier, rows):
    normalized = _normalize(identifier)
    if not normalized:
        return None

    for row in rows:
        email_value = _normalize(row.get("email"))
        username_value = _normalize(row.get("username"))
        if normalized in (email_value, username_value):
            return row

    for row in rows:
        person_name = _normalize(row.get("person_name"))
        display_name = _normalize(row.get("name"))
        if normalized and (normalized in person_name or normalized in display_name):
            return row

    return None


def _collect(formateur_filter=None):
    now = timezone.now()
    overviews = list(CourseOverview.objects.order_by("-start")[:1200])
    overview_by_id = {str(overview.id): overview for overview in overviews}

    grouped = defaultdict(lambda: {"user": None, "course_ids": set()})

    for access_role in CourseAccessRole.objects.filter(role__in=ROLE_NAMES).exclude(course_id=None).select_related("user"):
        if not access_role.user or access_role.user.is_superuser:
            continue
        group = grouped[access_role.user.id]
        group["user"] = access_role.user
        group["course_ids"].add(str(access_role.course_id))

    mapping = getattr(settings, "MISSION_FORMATIONS_FORMATEURS_FORMATIONS", {}) or {}
    User = get_user_model()
    for key, value in mapping.items():
        lookup = _normalize(str(key))
        if not lookup:
            continue

        user = User.objects.filter(email__iexact=lookup).first() or User.objects.filter(username=lookup).first()
        if not user or user.is_superuser:
            continue

        if isinstance(value, str) and value.strip().upper() == "ALL":
            resolved_ids = list(overview_by_id.keys())
        else:
            resolved_ids = _resolve_mapping_courses(value, overviews)

        if not resolved_ids:
            continue

        group = grouped[user.id]
        group["user"] = user
        group["course_ids"].update(resolved_ids)

    # Include all active staff users, even if no course/session is assigned yet.
    for staff_user in User.objects.filter(is_staff=True, is_superuser=False, is_active=True):
        group = grouped[staff_user.id]
        if not group["user"]:
            group["user"] = staff_user

    all_course_ids = set()
    for item in grouped.values():
        all_course_ids.update(item["course_ids"])

    enrollment_counts = {
        str(item["course_id"]): item["total"]
        for item in CourseEnrollment.objects.filter(
            is_active=True,
            course_id__in=all_course_ids,
            user__is_staff=False,
            user__is_superuser=False,
        ).values("course_id").annotate(total=Count("id"))
    }

    total_learners = CourseEnrollment.objects.filter(
        is_active=True,
        course_id__in=all_course_ids,
        user__is_staff=False,
        user__is_superuser=False,
    ).values("user_id").distinct().count()

    rows = []
    for item in grouped.values():
        user = item["user"]
        if not user:
            continue

        course_ids = sorted(item["course_ids"])
        sessions = []
        learners_total = 0

        for course_id in course_ids:
            overview = overview_by_id.get(course_id)
            if not overview:
                continue

            learners = int(enrollment_counts.get(course_id, 0) or 0)
            learners_total += learners

            sessions.append(
                {
                    "course_id": course_id,
                    "display_name": getattr(overview, "display_name_with_default", None) or getattr(overview, "display_name", None) or course_id,
                    "learners": learners,
                    "studio_url": f"http://studio.local.openedx.io/course/{quote(course_id, safe='')}",
                }
            )

        profile = getattr(user, "profile", None)
        name = (
            getattr(profile, "name", "")
            or user.get_full_name().strip()
            or user.username
        )
        person_name = _person_name(user)

        avg_rating = 0.0
        if sessions:
            avg_rating = 4.2
            if learners_total >= 40:
                avg_rating = 4.7
            elif learners_total >= 25:
                avg_rating = 4.5

        row = (
            {
                "username": user.username,
                "name": name,
                "person_name": person_name,
                "email": user.email or "",
                "is_staff": bool(getattr(user, "is_staff", False)),
                "sessions": sessions,
                "sessions_count": len(sessions),
                "learners_total": learners_total,
                "avatar": _initials(name or user.username),
                "specialty": _course_specialty(sessions[0]["display_name"]) if sessions else "Aucune session assignee",
                "frais_pending_eur": 0,
                "rating": avg_rating,
                "status": "active" if sessions else "pending",
            }
        )
        if formateur_filter:
            username_l = _normalize(row["username"])
            email_l = _normalize(row["email"])
            name_l = _normalize(row["name"])
            person_name_l = _normalize(row.get("person_name"))
            if (
                formateur_filter not in (username_l, email_l)
                and formateur_filter not in name_l
                and formateur_filter not in person_name_l
            ):
                continue
        rows.append(row)

    rows.sort(key=lambda row: row["name"].lower())

    recent_students = []
    recent_enrollments = CourseEnrollment.objects.filter(
        is_active=True,
        course_id__in=all_course_ids,
        user__is_staff=False,
        user__is_superuser=False,
    ).select_related("user").order_by("-created")[:6]
    for enrollment in recent_enrollments:
        learner = enrollment.user
        learner_name = (
            getattr(getattr(learner, "profile", None), "name", "")
            or learner.get_full_name().strip()
            or learner.username
        )
        course_name = str(enrollment.course_id)
        overview = overview_by_id.get(course_name)
        if overview:
            course_name = (
                getattr(overview, "display_name_with_default", None)
                or getattr(overview, "display_name", None)
                or course_name
            )
        recent_students.append(
            {
                "name": learner_name,
                "initials": _initials(learner_name or learner.username),
                "course_name": course_name,
                "created_text": (enrollment.created or now).strftime("%d %b %Y"),
                "progress_text": "--",
            }
        )

    upcoming_sessions = []
    future_overviews = [item for item in overviews if getattr(item, "start", None) and item.start >= now]
    future_overviews.sort(key=lambda item: item.start)
    for overview in future_overviews[:6]:
        day_text, month_text = _format_day_month(overview.start)
        course_id = str(overview.id)
        upcoming_sessions.append(
            {
                "day": day_text,
                "month": month_text,
                "title": getattr(overview, "display_name_with_default", None) or getattr(overview, "display_name", None) or course_id,
                "details": "{} · {} inscrits".format(
                    (overview.start or now).strftime("%Hh%M"),
                    int(enrollment_counts.get(course_id, 0) or 0),
                ),
                "tag": "Formation",
                "tag_class": "t-form",
            }
        )

    recent_activity = []
    for enrollment in recent_enrollments[:7]:
        learner = enrollment.user
        learner_name = (
            getattr(getattr(learner, "profile", None), "name", "")
            or learner.get_full_name().strip()
            or learner.username
        )
        course_name = str(enrollment.course_id)
        overview = overview_by_id.get(course_name)
        if overview:
            course_name = (
                getattr(overview, "display_name_with_default", None)
                or getattr(overview, "display_name", None)
                or course_name
            )
        recent_activity.append(
            {
                "dot": "gr",
                "text": "{} s'est inscrit(e) a {}".format(learner_name, course_name),
                "time": _activity_time_ago(enrollment.created),
            }
        )

    academy_counts = {"vtc": 0, "it": 0, "marketing": 0}
    for course_id in all_course_ids:
        overview = overview_by_id.get(course_id)
        if not overview:
            continue
        display_name = (
            getattr(overview, "display_name_with_default", None)
            or getattr(overview, "display_name", None)
            or course_id
        )
        learners = int(enrollment_counts.get(course_id, 0) or 0)
        name_l = _normalize(display_name)
        if "vtc" in name_l:
            academy_counts["vtc"] += learners
        elif any(token in name_l for token in ("it", "dev", "devops", "python", "data")):
            academy_counts["it"] += learners
        else:
            academy_counts["marketing"] += learners

    return {
        "total_sessions": len(all_course_ids),
        "total_formateurs": len(rows),
        "total_learners": total_learners,
        "formateurs": rows,
        "recent_students": recent_students,
        "upcoming_sessions": upcoming_sessions,
        "recent_activity": recent_activity,
        "academy_counts": academy_counts,
        "pending_expenses_count": 3,
        "pending_expenses_total_eur": 1240,
    }


@login_required
@require_http_methods(["GET", "POST"])
def internal_messaging(request):
    if not _staff_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    groups = _messaging_groups_for_user(request.user)
    groups_by_key = {group["key"]: group for group in groups}

    preferred_group = _normalize(request.GET.get("group"))
    selected_group = preferred_group if preferred_group in groups_by_key else (groups[0]["key"] if groups else "")
    subject_value = ""
    message_value = ""
    success_message = ""
    error_message = ""

    if request.method == "POST":
        selected_group = _normalize(request.POST.get("recipient_group"))
        subject_value = (request.POST.get("subject") or "").strip()
        message_value = (request.POST.get("message") or "").strip()

        if not groups:
            error_message = "Aucun groupe de destinataires disponible pour votre compte."
        elif selected_group not in groups_by_key:
            error_message = "Le groupe sélectionné est invalide."
        elif not subject_value:
            error_message = "Renseigne l'objet de l'email."
        elif not message_value:
            error_message = "Renseigne le contenu du message."
        else:
            recipients = groups_by_key[selected_group]["emails"]
            if not recipients:
                error_message = "Ce groupe ne contient aucun destinataire avec email valide."
            elif len(recipients) > 5000:
                error_message = "Le groupe dépasse la limite d'envoi (5000). Réduis le ciblage."
            else:
                try:
                    audit = InternalMessageAudit.objects.create(
                        sender=request.user,
                        recipient_group=selected_group,
                        recipient_count=len(recipients),
                        recipients_json=json.dumps(recipients, ensure_ascii=True),
                        subject=subject_value[:180],
                        body=message_value,
                        status=InternalMessageAudit.STATUS_QUEUED,
                    )

                    def _enqueue_after_commit(audit_id):
                        task = send_internal_message_task.delay(audit_id)
                        task_id = getattr(task, "id", "")
                        if task_id:
                            InternalMessageAudit.objects.filter(id=audit_id).update(task_id=task_id)

                    transaction.on_commit(lambda: _enqueue_after_commit(audit.id))
                    success_message = (
                        f"Message mis en file d'envoi pour {len(recipients)} destinataire(s). "
                        f"ID audit: {audit.id}."
                    )
                    subject_value = ""
                    message_value = ""
                except Exception as exc:  # pylint: disable=broad-except
                    error_message = f"Envoi impossible via la file interne: {exc}"

    audits = _recent_message_audits(request.user)
    context = {
        "groups": groups,
        "selected_group": selected_group,
        "subject_value": subject_value,
        "message_value": message_value,
        "success_message": success_message,
        "error_message": error_message,
        "audits": audits,
        "dashboard_url": "/admin/mission-dashboard/" if request.user.is_superuser else "/dashboard",
    }
    return render_to_response("mission_internal_messaging.html", context)


@login_required
@require_http_methods(["GET"])
def internal_notifications(request):
    if not _staff_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    open_id = _to_positive_int(request.GET.get("open"))
    if open_id:
        unread = Notification.objects.filter(
            id=open_id,
            user_id=request.user.id,
            last_read__isnull=True,
        ).first()
        if unread:
            unread.last_read = timezone.now()
            unread.last_seen = unread.last_read
            unread.save(update_fields=["last_read", "last_seen"])

    notifications = _internal_notifications_for_user(request.user)
    selected = notifications[0] if notifications else None
    if open_id:
        selected = next((item for item in notifications if item["id"] == open_id), selected)

    context = {
        "notifications": notifications,
        "selected_notification": selected,
        "dashboard_url": "/admin/mission-dashboard/" if request.user.is_superuser else "/dashboard",
    }
    return render_to_response("mission_internal_notifications.html", context)


@login_required
def dashboard(request):
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    formateur_filter = _normalize(request.GET.get("formateur"))
    context = _collect(formateur_filter=formateur_filter)
    context["api_url"] = "/api/admin/formateurs-sessions/"
    context["export_url"] = "/api/admin/formateurs-sessions/export.csv"
    context["current_formateur"] = formateur_filter
    profile = getattr(request.user, "profile", None)
    context["admin_name"] = (
        getattr(profile, "name", "")
        or request.user.get_full_name().strip()
        or request.user.username
    )
    context["admin_initials"] = _initials(context["admin_name"])
    context["internal_notifications"] = _internal_notifications_for_user(request.user)
    return render_to_response("admin_central_dashboard.html", context)


@login_required
def formateur_detail(request):
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    identifier = (request.GET.get("id") or "").strip()
    if not identifier:
        raise Http404("Formateur introuvable")

    data = _collect()
    row = _match_formateur_row(identifier, data.get("formateurs", []))
    if not row:
        raise Http404("Formateur introuvable")

    User = get_user_model()
    row_email = (row.get("email") or "").strip()
    row_username = (row.get("username") or "").strip()
    formateur_user = (
        User.objects.filter(email__iexact=row_email).first()
        or User.objects.filter(username=row_username).first()
    )

    if formateur_user:
        date_joined_text = (formateur_user.date_joined or timezone.now()).strftime("%d/%m/%Y %H:%M")
        if formateur_user.last_login:
            last_login_text = formateur_user.last_login.strftime("%d/%m/%Y %H:%M")
        else:
            last_login_text = "Jamais connecte"
    else:
        date_joined_text = "--"
        last_login_text = "--"

    profile = getattr(request.user, "profile", None)
    context = {
        "dashboard_url": "/admin/mission-dashboard/",
        "formateur": row,
        "date_joined_text": date_joined_text,
        "last_login_text": last_login_text,
        "admin_name": (
            getattr(profile, "name", "")
            or request.user.get_full_name().strip()
            or request.user.username
        ),
    }
    return render_to_response("admin_formateur_detail.html", context)


@login_required
def formateurs_sessions_api(request):
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")
    formateur_filter = _normalize(request.GET.get("formateur"))
    return JsonResponse(_collect(formateur_filter=formateur_filter), safe=False)


@login_required
def formateurs_sessions_export_csv(request):
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    formateur_filter = _normalize(request.GET.get("formateur"))
    data = _collect()

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="mission_admin_formateurs_sessions.csv"'
    writer = csv.writer(response)
    writer.writerow(["Formateur", "Email", "Course ID", "Formation", "Nb apprenants"])

    for row in data["formateurs"]:
        row_username = _normalize(row.get("username"))
        row_email = _normalize(row.get("email"))
        if formateur_filter and formateur_filter not in (row_username, row_email):
            continue

        for session in row.get("sessions", []):
            writer.writerow(
                [
                    row.get("name", ""),
                    row.get("email", ""),
                    session.get("course_id", ""),
                    session.get("display_name", ""),
                    session.get("learners", 0),
                ]
            )

    return response


@login_required
@require_http_methods(["GET", "POST"])
def test_dashboard(request):
    """Dashboard Qualite & Tests — execute pytest et affiche les resultats."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    import subprocess
    import pathlib

    results = None
    email_sent = False
    if request.method == "POST":
        suite = request.POST.get("suite", "unit")
        send_email = request.POST.get("send_email") == "1"
        email_to = (request.POST.get("email_to") or request.user.email or "").strip()
        allowed_suites = {"unit": "tests/unit/", "integration": "tests/integration/", "smoke": "tests/smoke/", "all": "tests/"}
        test_path = allowed_suites.get(suite, "tests/unit/")
        marker = f"-m {suite}" if suite != "all" else ""

        project_root = pathlib.Path(settings.PROJECT_ROOT).parent if hasattr(settings, "PROJECT_ROOT") else pathlib.Path("/openedx/edx-platform")
        # -o addopts= ecrase les arguments de setup.cfg qui entrent en conflit
        # -c tests/pytest.ini force notre propre config au lieu de setup.cfg
        cmd = (
            f"cd {project_root} && python -m pytest {test_path} {marker} "
            f"-c tests/pytest.ini -o 'addopts=-v --tb=short' --no-header 2>&1 | tail -80"
        )
        try:
            proc = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True, timeout=120,
            )
            raw = proc.stdout or proc.stderr or "Aucune sortie"
            # Parser la sortie pytest en donnees structurees
            import re as _re
            passed_tests = []
            failed_tests = []
            skipped_tests = []
            for line in raw.splitlines():
                line_s = line.strip()
                if " PASSED" in line_s:
                    name = line_s.split(" PASSED")[0].strip()
                    # Extraire le nom court: fichier::classe::methode
                    parts = name.rsplit("::", 1)
                    short = parts[-1] if len(parts) > 1 else name
                    module = parts[0].split("/")[-1] if len(parts) > 1 else ""
                    passed_tests.append({"name": short, "module": module, "full": name})
                elif " FAILED" in line_s:
                    name = line_s.split(" FAILED")[0].strip()
                    parts = name.rsplit("::", 1)
                    short = parts[-1] if len(parts) > 1 else name
                    module = parts[0].split("/")[-1] if len(parts) > 1 else ""
                    failed_tests.append({"name": short, "module": module, "full": name})
                elif " SKIPPED" in line_s:
                    name = line_s.split(" SKIPPED")[0].strip()
                    parts = name.rsplit("::", 1)
                    short = parts[-1] if len(parts) > 1 else name
                    module = parts[0].split("/")[-1] if len(parts) > 1 else ""
                    skipped_tests.append({"name": short, "module": module, "full": name})

            # Extraire la ligne de resume (ex: "81 passed, 53 skipped in 0.28s")
            summary_line = ""
            duration = ""
            for line in raw.splitlines():
                if "passed" in line and ("in " in line or "failed" in line):
                    summary_line = line.strip().lstrip("=").rstrip("=").strip()
                    dur_match = _re.search(r'in ([\d.]+)s', line)
                    if dur_match:
                        duration = dur_match.group(1) + "s"
                    break

            # Extraire les details des echecs (le --tb=short donne le contexte)
            failure_details = []
            in_failure = False
            current_detail = []
            for line in raw.splitlines():
                if line.startswith("FAILED ") or line.startswith("_ "):
                    if current_detail:
                        failure_details.append("\n".join(current_detail))
                    current_detail = [line]
                    in_failure = True
                elif in_failure and (line.startswith("    ") or line.startswith("E ") or line.startswith("> ")):
                    current_detail.append(line)
                elif in_failure and line.strip() == "":
                    if current_detail:
                        failure_details.append("\n".join(current_detail))
                        current_detail = []
                    in_failure = False
            if current_detail:
                failure_details.append("\n".join(current_detail))

            results = {
                "output": raw,
                "returncode": proc.returncode,
                "suite": suite,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "summary": summary_line,
                "duration": duration,
                "failure_details": failure_details,
                "total": len(passed_tests) + len(failed_tests) + len(skipped_tests),
            }
        except subprocess.TimeoutExpired:
            results = {
                "output": "Timeout: les tests ont pris plus de 2 minutes.",
                "returncode": -1, "suite": suite,
                "passed": [], "failed": [], "skipped": [],
                "summary": "Timeout", "duration": ">120s",
                "failure_details": [], "total": 0,
            }

        if send_email and email_to and results:
            try:
                status = "PASS" if results["returncode"] == 0 else "FAIL"
                send_mail(
                    subject=f"[Mission Formations] Tests {suite.upper()} — {status}",
                    message=(
                        f"Resultats des tests {suite.upper()}\n"
                        f"Statut : {status}\n"
                        f"Lance par : {request.user.username} ({request.user.email})\n"
                        f"Date : {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
                        f"\n{'=' * 60}\n\n"
                        f"{results['output']}"
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@missionformations.com",
                    recipient_list=[email_to],
                    fail_silently=False,
                )
                email_sent = True
            except Exception:
                email_sent = False

    context = {
        "results": results,
        "email_sent": email_sent,
        "user_email": request.user.email or "",
        "dashboard_url": "/admin/mission-dashboard/",
    }
    return render_to_response("admin_test_dashboard.html", context)


# ── ACADEMY MANAGER ─────────────────────────────────────────────────────────

@login_required
def academy_list(request):
    """Dashboard Academy Manager — liste toutes les academies."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    from .models import Academy, AcademyEnrollment
    from django.db.models import Count

    academies = Academy.objects.annotate(
        course_count=Count("courses", distinct=True),
        learner_count=Count("academy_enrollments", distinct=True),
    ).order_by("academy_type", "name")

    internal = [a for a in academies if a.academy_type == "internal"]
    b2b = [a for a in academies if a.academy_type == "b2b"]

    # Stats globales
    total_learners = AcademyEnrollment.objects.values("user").distinct().count()
    total_courses = sum(a.course_count for a in academies)
    total_active = sum(1 for a in academies if a.is_active)

    context = {
        "internal_academies": internal,
        "b2b_academies": b2b,
        "total_academies": len(internal) + len(b2b),
        "total_learners": total_learners,
        "total_courses": total_courses,
        "total_active": total_active,
        "dashboard_url": "/admin/mission-dashboard/",
    }
    return render_to_response("academy_manager/dashboard.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def academy_create(request):
    """Formulaire de creation d'une nouvelle academie."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    from .models import Academy, AcademyAdmin as AcadAdmin

    error_message = ""
    success_message = ""

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        short_name = (request.POST.get("short_name") or "").strip().upper()
        academy_type = request.POST.get("academy_type", "internal")
        description = (request.POST.get("description") or "").strip()
        primary_color = request.POST.get("primary_color", "#0965D0").strip()
        secondary_color = request.POST.get("secondary_color", "#01E8AE").strip()
        admin_email = (request.POST.get("admin_email") or "").strip()

        # B2B fields
        client_name = (request.POST.get("client_name") or "").strip()
        client_contact = (request.POST.get("client_contact") or "").strip()
        contract_start = request.POST.get("contract_start") or None
        contract_end = request.POST.get("contract_end") or None
        max_seats = int(request.POST.get("max_seats") or 0)

        if not name or not short_name:
            error_message = "Nom et identifiant sont obligatoires."
        elif Academy.objects.filter(short_name=short_name).exists():
            error_message = f"L'identifiant {short_name} existe deja."
        else:
            try:
                academy = Academy.objects.create(
                    name=name,
                    short_name=short_name,
                    academy_type=academy_type,
                    description=description,
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    client_name=client_name,
                    client_contact=client_contact,
                    contract_start=contract_start,
                    contract_end=contract_end,
                    max_seats=max_seats,
                )

                # Creer l'organisation OpenEdX
                try:
                    from organizations.models import Organization
                    org, _ = Organization.objects.get_or_create(
                        short_name=short_name,
                        defaults={"name": name, "active": True},
                    )
                    academy.organization_id = str(org.id)
                    academy.save(update_fields=["organization_id"])
                except Exception:
                    pass

                # Assigner l'admin si email fourni
                if admin_email:
                    User = get_user_model()
                    admin_user = User.objects.filter(email__iexact=admin_email).first()
                    if admin_user:
                        role = "client_admin" if academy_type == "b2b" else "academy_admin"
                        AcadAdmin.objects.get_or_create(
                            academy=academy, user=admin_user,
                            defaults={"role": role},
                        )

                return redirect(f"/academy-manager/{academy.slug}/")
            except Exception as exc:
                error_message = f"Erreur: {exc}"

    context = {
        "error_message": error_message,
        "success_message": success_message,
        "dashboard_url": "/admin/mission-dashboard/",
    }
    return render_to_response("academy_manager/create.html", context)


@login_required
def academy_detail(request, slug):
    """Page de gestion d'une academie (onglets cours/apprenants/stats)."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    from .models import Academy, AcademyCourse, AcademyEnrollment, AcademyAdmin as AcadAdmin

    try:
        academy = Academy.objects.get(slug=slug)
    except Academy.DoesNotExist:
        raise Http404("Academie introuvable")

    courses = AcademyCourse.objects.filter(academy=academy).order_by("order")
    enrollments = AcademyEnrollment.objects.filter(academy=academy).select_related("user").order_by("-enrolled_at")[:100]
    admins = AcadAdmin.objects.filter(academy=academy).select_related("user")

    # Stats
    total_learners = enrollments.count()
    total_courses = courses.count()

    # Cours disponibles pour rattachement
    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
    all_courses = CourseOverview.objects.order_by("-start")[:200]
    attached_keys = set(courses.values_list("course_key", flat=True))
    available_courses = [c for c in all_courses if str(c.id) not in attached_keys]

    tab = request.GET.get("tab", "overview")

    context = {
        "academy": academy,
        "courses": courses,
        "enrollments": enrollments,
        "admins": admins,
        "total_learners": total_learners,
        "total_courses": total_courses,
        "available_courses": available_courses,
        "tab": tab,
        "dashboard_url": "/admin/mission-dashboard/",
    }
    return render_to_response("academy_manager/detail.html", context)


@login_required
@require_http_methods(["POST"])
def academy_attach_course(request, slug):
    """Rattacher un cours a une academie."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    from .models import Academy, AcademyCourse

    try:
        academy = Academy.objects.get(slug=slug)
    except Academy.DoesNotExist:
        raise Http404("Academie introuvable")

    course_key = (request.POST.get("course_key") or "").strip()
    if course_key:
        AcademyCourse.objects.get_or_create(
            academy=academy, course_key=course_key,
        )
    return redirect(f"/academy-manager/{slug}/?tab=courses")


@login_required
@require_http_methods(["POST"])
def academy_invite(request, slug):
    """Inviter des apprenants a une academie (par email)."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    from .models import Academy, AcademyEnrollment

    try:
        academy = Academy.objects.get(slug=slug)
    except Academy.DoesNotExist:
        raise Http404("Academie introuvable")

    emails_raw = (request.POST.get("emails") or "").strip()
    emails = [e.strip().lower() for e in emails_raw.replace(",", "\n").splitlines() if e.strip()]

    User = get_user_model()
    invited = 0
    for email in emails:
        user = User.objects.filter(email__iexact=email).first()
        if user:
            _, created = AcademyEnrollment.objects.get_or_create(
                academy=academy, user=user,
                defaults={"invited_by": request.user},
            )
            if created:
                invited += 1

    return redirect(f"/academy-manager/{slug}/?tab=learners&invited={invited}")


@login_required
@require_http_methods(["GET", "POST"])
def delete_user(request):
    """Suppression securisee d'un utilisateur — gere les foreign keys CMS."""
    if not _admin_allowed(request.user):
        return HttpResponseForbidden("403 Forbidden")

    import logging
    logger = logging.getLogger(__name__)
    User = get_user_model()

    user_id = request.GET.get("id") or request.POST.get("id")
    target = User.objects.filter(id=user_id).first() if user_id else None

    error_message = ""
    success_message = ""

    if request.method == "POST" and target:
        if target.is_superuser:
            error_message = "Impossible de supprimer un superuser."
        elif target.id == request.user.id:
            error_message = "Impossible de supprimer votre propre compte."
        else:
            try:
                from django.db import connection
                username = target.username
                uid = target.id

                # Tables CMS partagees avec foreign key vers auth_user
                # que Django LMS ne connait pas dans son CASCADE
                orphan_tables = [
                    "course_creators_coursecreator",
                    "social_django_usersocialauth",
                    "social_django_nonce",
                    "social_django_association",
                    "social_django_code",
                    "social_django_partial",
                ]
                cleaned = []
                with connection.cursor() as cursor:
                    for table in orphan_tables:
                        try:
                            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", [uid])
                            if cursor.rowcount > 0:
                                cleaned.append(f"{table}: {cursor.rowcount}")
                        except Exception:
                            pass  # Table n'existe pas, on continue

                # Maintenant le CASCADE Django peut fonctionner
                target.delete()
                success_message = f"Utilisateur {username} (id={uid}) supprime. Nettoyage: {', '.join(cleaned) or 'aucune table orpheline'}."
                logger.info(f"[MF-ADMIN] User deleted: {username} (id={uid}) by {request.user.username}. Cleaned: {cleaned}")
                target = None
            except Exception as exc:
                error_message = f"Erreur lors de la suppression: {exc}"
                logger.error(f"[MF-ADMIN] Delete failed for user_id={user_id}: {exc}")

    # Liste des utilisateurs pour la page GET
    users = User.objects.filter(is_active=True).order_by("username").values(
        "id", "username", "email", "first_name", "last_name",
        "is_staff", "is_superuser", "date_joined", "last_login",
    )[:200]

    context = {
        "users": list(users),
        "target": target,
        "success_message": success_message,
        "error_message": error_message,
        "dashboard_url": "/admin/mission-dashboard/",
    }
    return render_to_response("admin_delete_user.html", context)


@require_http_methods(["GET", "POST"])
def contact_view(request):
    field_names = ("prenom", "nom", "email", "telephone", "profil", "sujet", "message")
    form_data = {name: (request.POST.get(name, "") or "").strip() for name in field_names}
    success = request.GET.get("success") == "1"
    error_message = ""

    if request.method == "POST":
        missing_required = [name for name in ("prenom", "nom", "email", "sujet", "message") if not form_data[name]]
        if missing_required:
            error_message = "Merci de renseigner tous les champs obligatoires."
        else:
            subject = f"[Contact Mission Formations] {form_data['sujet']}"
            body = "\n".join(
                [
                    "Nouveau message depuis la page contact.",
                    "",
                    f"Prenom: {form_data['prenom']}",
                    f"Nom: {form_data['nom']}",
                    f"Email: {form_data['email']}",
                    f"Telephone: {form_data['telephone']}",
                    f"Profil: {form_data['profil']}",
                    f"Sujet: {form_data['sujet']}",
                    "",
                    "Message:",
                    form_data["message"],
                ]
            )
            sender = (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip() or form_data["email"]
            send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=["contact@missionformations.com"],
                fail_silently=False,
            )
            return redirect("/contact?success=1")

    return render(
        request,
        "mission_central_admin/contact.html",
        {
            "success": success,
            "error_message": error_message,
            "form_data": form_data,
        },
    )
