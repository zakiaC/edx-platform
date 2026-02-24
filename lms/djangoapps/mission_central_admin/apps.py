from django.apps import AppConfig


class MissionCentralAdminConfig(AppConfig):
    name = "lms.djangoapps.mission_central_admin"
    verbose_name = "Mission Central Admin"

    def ready(self):
        # Register URLs after Django app registry is fully loaded.
        # We prepend patterns so /admin/mission-dashboard/ is matched
        # before Django's generic /admin/ route include.
        from lms import urls as lms_urls  # pylint: disable=import-outside-toplevel
        from . import error_views  # pylint: disable=import-outside-toplevel
        from .urls import urlpatterns as mission_patterns  # pylint: disable=import-outside-toplevel

        # Override Django error handlers at URLConf level.
        lms_urls.handler403 = error_views.render_403
        lms_urls.handler404 = error_views.render_404
        lms_urls.handler500 = error_views.render_500

        existing_names = {getattr(pattern, "name", None) for pattern in lms_urls.urlpatterns}
        for pattern in reversed(mission_patterns):
            if getattr(pattern, "name", None) not in existing_names:
                lms_urls.urlpatterns.insert(0, pattern)

        self._patch_admin_user_creation_form()

    def _patch_admin_user_creation_form(self):
        """
        Ensure Django admin "Add user" requires email.
        Open edX enforces unique auth_user.email in DB fixups.
        """
        from django.contrib import admin  # pylint: disable=import-outside-toplevel
        from django.contrib.auth import get_user_model  # pylint: disable=import-outside-toplevel
        from .forms import MissionAdminUserCreationForm  # pylint: disable=import-outside-toplevel

        user_model = get_user_model()
        model_admin = admin.site._registry.get(user_model)
        if not model_admin:
            return

        model_admin.add_form = MissionAdminUserCreationForm

        add_fieldsets = list(getattr(model_admin, "add_fieldsets", ()) or ())
        if not add_fieldsets:
            model_admin.add_fieldsets = (
                (None, {"classes": ("wide",), "fields": ("username", "email", "usable_password", "password1", "password2")}),
            )
            return

        section_name, section_opts = add_fieldsets[0]
        opts = dict(section_opts or {})
        fields = list(opts.get("fields", ()))
        if "email" not in fields:
            if "username" in fields:
                username_index = fields.index("username")
                fields.insert(username_index + 1, "email")
            else:
                fields.insert(0, "email")
        opts["fields"] = tuple(fields)
        add_fieldsets[0] = (section_name, opts)
        model_admin.add_fieldsets = tuple(add_fieldsets)
