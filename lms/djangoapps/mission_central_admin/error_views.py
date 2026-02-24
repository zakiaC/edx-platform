import logging

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django_ratelimit.exceptions import Ratelimited

from common.djangoapps.edxmako.shortcuts import render_to_string
from common.djangoapps.util.views import fix_crum_request
from lms.djangoapps.static_template_view.views import render_429

log = logging.getLogger(__name__)


@fix_crum_request
def render_403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return render_429(request, exception)
    request.view_name = "403"
    return HttpResponseForbidden(render_to_string("static_templates/403.html", {}, request=request))


@fix_crum_request
def render_404(request, exception=None):
    request.view_name = "404"
    path = (getattr(request, "path", "") or "").lower()
    exception_text = str(exception).lower() if exception else ""
    is_course_not_found = (
        "course not found" in exception_text
        or "cours introuvable" in exception_text
        or "/courses/" in path
        or "/course/" in path
        or "course-v1:" in path
    )
    template = "static_templates/course-not-found.html" if is_course_not_found else "static_templates/404.html"
    return HttpResponseNotFound(render_to_string(template, {}, request=request))


@fix_crum_request
def render_500(request):
    try:
        return HttpResponseServerError(render_to_string("static_templates/server-error.html", {}, request=request))
    except BaseException:
        log.error("Encountered error while rendering Mission custom 500 page.", exc_info=True)
        return HttpResponseServerError("Encountered error while rendering error page.")


@fix_crum_request
def maintenance(request):
    request.view_name = "maintenance"
    return HttpResponse(render_to_string("static_templates/maintenance.html", {}, request=request), status=503)


@fix_crum_request
def course_not_found_preview(request):
    request.view_name = "course-not-found"
    return HttpResponseNotFound(render_to_string("static_templates/course-not-found.html", {}, request=request))
