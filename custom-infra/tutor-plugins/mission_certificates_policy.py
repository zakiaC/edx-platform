"""Tutor plugin: enforce Mission certificates sidebar policy.

Policy:
- Sidebar certificates menu shows only validated/obtained certificates.
"""

from tutor import hooks
from tutor.hooks import priorities

PATCH_CONTENT = """
# mission_certificates_policy: sidebar menu includes only obtained certificates
MF_CERTIFICATES_MENU_ONLY_OBTAINED = True
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

hooks.Filters.CONFIG_OVERRIDES.add_item(("MF_CERTIFICATES_MENU_ONLY_OBTAINED", True))
