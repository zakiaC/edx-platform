from collections import defaultdict
import csv
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.utils.timesince import timesince

from common.djangoapps.edxmako.shortcuts import render_to_response
from common.djangoapps.student.models import CourseAccessRole, CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

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


def _admin_allowed(user):
    return bool(user and user.is_authenticated and user.is_superuser)


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


def _collect(formateur_filter=None):
    now = timezone.now()
    overviews = list(CourseOverview.objects.order_by("-start")[:1200])
    overview_by_id = {str(overview.id): overview for overview in overviews}

    grouped = defaultdict(lambda: {"user": None, "course_ids": set()})

    for access_role in CourseAccessRole.objects.filter(role__in=ROLE_NAMES).exclude(course_id=None).select_related("user"):
        if not access_role.user:
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
        if not user:
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

    all_course_ids = set()
    for item in grouped.values():
        all_course_ids.update(item["course_ids"])

    enrollment_counts = {
        str(item["course_id"]): item["total"]
        for item in CourseEnrollment.objects.filter(
            is_active=True,
            course_id__in=all_course_ids,
        ).values("course_id").annotate(total=Count("id"))
    }

    total_learners = CourseEnrollment.objects.filter(
        is_active=True,
        course_id__in=all_course_ids,
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

        if not sessions:
            continue

        profile = getattr(user, "profile", None)
        name = (
            getattr(profile, "name", "")
            or user.get_full_name().strip()
            or user.username
        )

        avg_rating = 4.2
        if learners_total >= 40:
            avg_rating = 4.7
        elif learners_total >= 25:
            avg_rating = 4.5

        row = (
            {
                "username": user.username,
                "name": name,
                "email": user.email or "",
                "sessions": sessions,
                "sessions_count": len(sessions),
                "learners_total": learners_total,
                "avatar": _initials(name or user.username),
                "specialty": _course_specialty(sessions[0]["display_name"]) if sessions else "Formation professionnelle",
                "frais_pending_eur": 0,
                "rating": avg_rating,
                "status": "active",
            }
        )
        if formateur_filter:
            username_l = _normalize(row["username"])
            email_l = _normalize(row["email"])
            name_l = _normalize(row["name"])
            if formateur_filter not in (username_l, email_l) and formateur_filter not in name_l:
                continue
        rows.append(row)

    rows.sort(key=lambda row: row["name"].lower())

    recent_students = []
    recent_enrollments = CourseEnrollment.objects.filter(
        is_active=True,
        course_id__in=all_course_ids,
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
    return render_to_response("admin_central_dashboard.html", context)


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
