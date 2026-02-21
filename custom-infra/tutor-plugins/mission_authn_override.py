"""Tutor v1 plugin: force legacy themed login/register by disabling Authn MFE.

Installed as a file-based plugin with:
    tutor plugins install /path/to/mission_authn_override.py
"""

from tutor import hooks
from tutor.hooks import priorities

PATCH_CONTENT = """
# mission_authn_override: keep LMS themed login/register pages
FEATURES['ENABLE_AUTHN_MICROFRONTEND'] = False
ENABLE_LEARNER_HOME_MFE = False
LEARNER_HOME_MFE_REDIRECT_PERCENTAGE = 0
""".strip()

# Redirect legacy GET password reset URL to themed login page.
CADDY_LMS_PATCH = """
@mf_password_reset_get {
    method GET HEAD
    path /password_reset /password_reset/
}
redir @mf_password_reset_get /login 302
""".strip()

# Explicitly remove authn MFE app when tutor-mfe is installed.
try:
    from tutormfe.hooks import MFE_APPS
except Exception:  # pragma: no cover - plugin may be absent
    MFE_APPS = None

if MFE_APPS is not None:
    @MFE_APPS.add(priority=priorities.LOW)
    def _disable_authn_mfe_app(apps):
        apps.pop("authn", None)
        apps.pop("learner-dashboard", None)
        return apps

# Override in LMS production/development patches, after tutor-mfe patches.
for patch_target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, PATCH_CONTENT),
        priority=priorities.LOW,
    )

hooks.Filters.ENV_PATCHES.add_item(
    ("caddyfile-lms", CADDY_LMS_PATCH),
    priority=priorities.DEFAULT,
)

# Keep config intent explicit as well.
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_AUTHN_MICROFRONTEND", False))
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_LEARNER_HOME_MFE", False))

# Ensure learner-home waffle flag stays disabled after init/launch.
hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        """
./manage.py lms shell -c "from waffle.models import Flag; f,_=Flag.objects.get_or_create(name='learner_home_mfe.enabled'); f.everyone=False; f.percent=0; f.authenticated=False; f.staff=False; f.superusers=False; f.save()"
""".strip(),
    ),
    priority=priorities.DEFAULT,
)
