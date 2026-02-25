"""Tutor plugin: Mission certificates visibility policy.

Role ownership (single responsibility):
- Certificate menu policy in LMS settings.
"""

from tutor import hooks
from tutor.hooks import priorities

PATCH_CONTENT = """
# mission_certificates_policy: sidebar menu includes only obtained certificates
MF_CERTIFICATES_MENU_ONLY_OBTAINED = True
""".strip()

hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-common-settings", PATCH_CONTENT),
    priority=priorities.DEFAULT,
)

hooks.Filters.CONFIG_OVERRIDES.add_item(("MF_CERTIFICATES_MENU_ONLY_OBTAINED", True))
