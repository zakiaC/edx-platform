"""Tutor plugin: Mission Central Admin (mount-safe version).

Goals:
- Declare Mission central-admin settings in LMS.
- Register the django app in INSTALLED_APPS without mounting full edx-platform.
- Keep URL registration handled by the app itself (AppConfig.ready), which is
  runtime-safe with Tutor v21 where no dedicated openedx-lms-urls patch point
  exists.
"""

from tutor import hooks
from tutor.hooks import priorities

DEFAULT_MAPPING = {
    "formateur1@example.com": ["formation-python", "formation-excel"],
    "formateur2@example.com": ["formation-rse", "formation-management"],
    "admin@missionformations.com": "ALL",
}

DEFAULT_ALLOWED = [
    "admin@missionformations.com",
    "superadmin.mission.test@missionformations.local",
]

PATCH_CONTENT = """
# mission_central_admin plugin settings
MISSION_FORMATIONS_FORMATEURS_FORMATIONS = {{ MISSION_FORMATIONS_FORMATEURS_FORMATIONS }}
MISSION_CENTRAL_ADMIN_ALLOWED = {{ MISSION_CENTRAL_ADMIN_ALLOWED }}

import importlib.util
if importlib.util.find_spec('lms.djangoapps.mission_central_admin'):
    if 'lms.djangoapps.mission_central_admin' not in INSTALLED_APPS:
        INSTALLED_APPS.append('lms.djangoapps.mission_central_admin')

# Middleware: deconnecter les utilisateurs inactifs (email non confirme)
_mf_middleware = 'lms.djangoapps.mission_central_admin.middleware.InactiveUserLogoutMiddleware'
if _mf_middleware not in MIDDLEWARE:
    MIDDLEWARE.append(_mf_middleware)
""".strip()

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("MISSION_FORMATIONS_FORMATEURS_FORMATIONS", DEFAULT_MAPPING),
        ("MISSION_CENTRAL_ADMIN_ALLOWED", DEFAULT_ALLOWED),
    ]
)

# Common settings is enough: production/development import common_lms.
hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-common-settings", PATCH_CONTENT),
    priority=priorities.DEFAULT,
)
