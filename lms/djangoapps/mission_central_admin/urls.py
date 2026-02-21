from django.urls import path

from . import views

urlpatterns = [
    path("admin/mission-dashboard/", views.dashboard, name="mission-central-dashboard"),
    path("api/admin/formateurs-sessions/", views.formateurs_sessions_api, name="mission-central-api"),
    path("api/admin/formateurs-sessions/export.csv", views.formateurs_sessions_export_csv, name="mission-central-export-csv"),
]
