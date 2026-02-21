"""Tutor plugin: Mission Central Admin.

Adds central admin dashboard app to LMS and exposes config mapping:
- MISSION_FORMATIONS_FORMATEURS_FORMATIONS
- MISSION_CENTRAL_ADMIN_ALLOWED
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
""".strip()

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("MISSION_FORMATIONS_FORMATEURS_FORMATIONS", DEFAULT_MAPPING),
        ("MISSION_CENTRAL_ADMIN_ALLOWED", DEFAULT_ALLOWED),
    ]
)

for patch_target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, PATCH_CONTENT),
        priority=priorities.DEFAULT,
    )
