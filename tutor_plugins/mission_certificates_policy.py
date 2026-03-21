"""Tutor plugin: Mission certificates — feature flags + visibility policy.

Responsabilites :
- Activer le rendu HTML des certificats web
- Activer les templates de certificats personnalises
- Limiter le menu sidebar aux certificats obtenus
"""

from tutor import hooks
from tutor.hooks import priorities

PATCH_CONTENT = """
# mission_certificates_policy: activer les certificats HTML web
FEATURES['CERTIFICATES_HTML_VIEW'] = True

# Permettre les templates de certificats personnalises (theme ou DB)
FEATURES['CUSTOM_CERTIFICATE_TEMPLATES_ENABLED'] = True

# Sidebar menu : afficher uniquement les certificats obtenus
MF_CERTIFICATES_MENU_ONLY_OBTAINED = True
""".strip()

hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-common-settings", PATCH_CONTENT),
    priority=priorities.DEFAULT,
)

hooks.Filters.CONFIG_OVERRIDES.add_item(("MF_CERTIFICATES_MENU_ONLY_OBTAINED", True))
