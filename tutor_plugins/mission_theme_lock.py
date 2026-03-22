"""Tutor plugin: lock Mission themed auth/navigation behavior.

Role ownership (single responsibility):
- Auth UX lock and theme selection.
- Auth route normalization (/authn* -> /login).
- Learner home MFE disablement.
"""
from tutor import hooks
from tutor.hooks import priorities

THEME_NAME = "mission-theme"

PATCH_CONTENT = """
# mission_theme_lock: enforce Mission themed auth stack
DEFAULT_SITE_THEME = "mission-theme"
FEATURES['ENABLE_AUTHN_MICROFRONTEND'] = False
FEATURES['ENABLE_THIRD_PARTY_AUTH'] = False
FEATURES['ENABLE_COMBINED_LOGIN_REGISTRATION'] = True
ENABLE_LEARNER_HOME_MFE = False
LEARNER_HOME_MFE_REDIRECT_PERCENTAGE = 0

# MFE Learning URL (obligatoire — sans ca, les redirections /courses/.../course/ → 404)
LEARNING_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/learning"

if "/openedx/themes" not in COMPREHENSIVE_THEME_DIRS:
    COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")
if "/openedx/themes/mission-theme/lms/static" not in STATICFILES_DIRS:
    STATICFILES_DIRS.append("/openedx/themes/mission-theme/lms/static")
""".strip()

CMS_PATCH_CONTENT = """
# mission_theme_lock: keep CMS aligned on Mission default theme
DEFAULT_SITE_THEME = "mission-theme"
if "/openedx/themes" not in COMPREHENSIVE_THEME_DIRS:
    COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")
""".strip()

for patch_target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, PATCH_CONTENT),
        priority=priorities.DEFAULT,
    )

for patch_target in (
    "openedx-cms-common-settings",
    "openedx-cms-production-settings",
    "openedx-cms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, CMS_PATCH_CONTENT),
        priority=priorities.DEFAULT,
    )

CADDY_LMS_PATCH = """
# mission_theme_lock: keep legacy themed auth entrypoints
@mf_authn_native_routes {
    method GET HEAD
    path /authn /authn/*
}
redir @mf_authn_native_routes /login 302
header X-Mission-Theme-Lock "enabled"
""".strip()

hooks.Filters.ENV_PATCHES.add_item(
    ("caddyfile-lms", CADDY_LMS_PATCH),
    priority=priorities.DEFAULT,
)

try:
    from tutormfe.hooks import MFE_APPS
except Exception:  # tutor-mfe may not be installed
    MFE_APPS = None

if MFE_APPS is not None:
    @MFE_APPS.add(priority=priorities.LOW)
    def _disable_authn_mfe_app(apps):
        apps.pop("authn", None)
        apps.pop("learner-dashboard", None)
        return apps

hooks.Filters.CONFIG_OVERRIDES.add_item(("DEFAULT_SITE_THEME", THEME_NAME))
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_AUTHN_MICROFRONTEND", False))
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_LEARNER_HOME_MFE", False))

hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        """
./manage.py lms shell -c "from waffle.models import Flag; f,_=Flag.objects.get_or_create(name='learner_home_mfe.enabled'); f.everyone=False; f.percent=0; f.authenticated=False; f.staff=False; f.superusers=False; f.save()"
""".strip(),
    ),
    priority=priorities.DEFAULT,
)
