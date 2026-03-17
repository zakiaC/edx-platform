from django.urls import path

from . import error_views, views

urlpatterns = [
    path("contact/", views.contact_view, name="contact"),
    path("mission-errors/403", error_views.render_403, name="mission-render-403"),
    path("mission-errors/404", error_views.render_404, name="mission-render-404"),
    path("mission-errors/500", error_views.render_500, name="mission-render-500"),
    path("maintenance", error_views.maintenance, name="mission-maintenance"),
    path("course-not-found", error_views.course_not_found_preview, name="mission-course-not-found"),
    path("messagerie/interne/", views.internal_messaging, name="mission-internal-messaging"),
    path("notifications/interne/", views.internal_notifications, name="mission-internal-notifications"),
    path("admin/mission-dashboard/", views.dashboard, name="mission-central-dashboard"),
    path("admin/mission-dashboard/formateur/", views.formateur_detail, name="mission-formateur-detail"),
    path("admin/mission-dashboard/tests/", views.test_dashboard, name="mission-test-dashboard"),
    path("admin/mission-dashboard/users/delete/", views.delete_user, name="mission-delete-user"),
    # Academy Manager
    path("academy-manager/", views.academy_list, name="academy-manager"),
    path("academy-manager/create/", views.academy_create, name="academy-create"),
    path("academy-manager/<slug:slug>/", views.academy_detail, name="academy-detail"),
    path("academy-manager/<slug:slug>/attach-course/", views.academy_attach_course, name="academy-attach-course"),
    path("academy-manager/<slug:slug>/invite/", views.academy_invite, name="academy-invite"),
    # API
    path("api/admin/formateurs-sessions/", views.formateurs_sessions_api, name="mission-central-api"),
    path("api/admin/formateurs-sessions/export.csv", views.formateurs_sessions_export_csv, name="mission-central-export-csv"),
]
