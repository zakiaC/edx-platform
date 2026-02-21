from django.apps import AppConfig


class MissionCentralAdminConfig(AppConfig):
    name = "lms.djangoapps.mission_central_admin"
    verbose_name = "Mission Central Admin"

    def ready(self):
        # Register URLs after Django app registry is fully loaded.
        # We prepend patterns so /admin/mission-dashboard/ is matched
        # before Django's generic /admin/ route include.
        from lms import urls as lms_urls  # pylint: disable=import-outside-toplevel
        from .urls import urlpatterns as mission_patterns  # pylint: disable=import-outside-toplevel

        existing_names = {getattr(pattern, "name", None) for pattern in lms_urls.urlpatterns}
        for pattern in reversed(mission_patterns):
            if getattr(pattern, "name", None) not in existing_names:
                lms_urls.urlpatterns.insert(0, pattern)
