"""Tutor plugin: lock Mission Formations themed auth experience.

Purpose:
- Prevent fallback to native auth MFE/native pages outside Mission theme flow.
- Keep login/register/reset on themed LMS pages.
- Remove authn/learner-dashboard MFE apps if tutor-mfe is installed.
- Keep config explicit and override-safe across environments.

Note: this plugin consolidates the former mission_authn_override plugin.
      Run `tutor plugins disable mission_authn_override` after updating.
"""
from tutor import hooks
from tutor.hooks import priorities

# ---------------------------------------------------------------------------
# 1. Django settings patches (applied to all LMS settings targets)
# ---------------------------------------------------------------------------
PATCH_CONTENT = """
# mission_theme_lock: enforce Mission themed auth stack
FEATURES['ENABLE_AUTHN_MICROFRONTEND'] = False
ENABLE_LEARNER_HOME_MFE = False
LEARNER_HOME_MFE_REDIRECT_PERCENTAGE = 0
""".strip()

for patch_target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, PATCH_CONTENT),
        priority=priorities.LOW,
    )

# ---------------------------------------------------------------------------
# 2. Caddy redirects: force all auth routes to /login
# ---------------------------------------------------------------------------
CADDY_LMS_PATCH = """
# mission_theme_lock: keep legacy themed auth entrypoints
@mf_authn_native_routes {
    method GET HEAD
    path /authn /authn/* /register /register/ /password_reset /password_reset/
}
redir @mf_authn_native_routes /login 302
header X-Mission-Theme-Lock "enabled"
""".strip()

hooks.Filters.ENV_PATCHES.add_item(
    ("caddyfile-lms", CADDY_LMS_PATCH),
    priority=priorities.DEFAULT,
)

# ---------------------------------------------------------------------------
# 3. MFE apps removal (absorbed from mission_authn_override)
#    Strips authn + learner-dashboard MFE when tutor-mfe is present.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 4. Tutor config overrides (single source of truth -> no more conflicts)
# ---------------------------------------------------------------------------
hooks.Filters.CONFIG_OVERRIDES.add_item(("DEFAULT_SITE_THEME", "mission-theme"))
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_AUTHN_MICROFRONTEND", False))
hooks.Filters.CONFIG_OVERRIDES.add_item(("ENABLE_LEARNER_HOME_MFE", False))

# ---------------------------------------------------------------------------
# 5. Waffle flag: keep learner-home MFE disabled after init
# ---------------------------------------------------------------------------
hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        """
./manage.py lms shell -c "from waffle.models import Flag; f,_=Flag.objects.get_or_create(name='learner_home_mfe.enabled'); f.everyone=False; f.percent=0; f.authenticated=False; f.staff=False; f.superusers=False; f.save()"
""".strip(),
    ),
    priority=priorities.DEFAULT,
)
