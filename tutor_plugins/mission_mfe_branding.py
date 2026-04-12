"""Tutor plugin: MFE branding Mission Formations.

Role ownership (single responsibility):
- Logo, favicon, slogan MFE
- Suppression de toute mention edX/OpenEdX dans les MFEs
- Footer links et texte custom
"""
from tutor import hooks
from tutor.hooks import priorities

MFE_BRANDING_PATCH = """
# mission_mfe_branding: branding MFE Mission Formations
MFE_CONFIG = {
    **globals().get('MFE_CONFIG', {}),
    'LOGO_POWERED_BY_OPEN_EDX_URL': False,
    'SHOW_POWERED_BY_OPENEDX': False,
    'FOOTER_POWERED_BY_OPENEDX': False,
    'INDIGO_FOOTER_LEGAL_LINKS': [],
    'INDIGO_FOOTER_EXTRA_LINKS': [],
    'INDIGO_FOOTER_SLOGAN': 'Donnez du sens à votre parcours!',
    'INDIGO_FOOTER_NAV_LINKS': [
        {'title': 'Qui sommes-nous', 'url': 'https://missionformations.com/a-propos/qui-sommes-nous/'},
        {'title': 'Catalogue', 'url': '/catalogue/'},
        {'title': "Centre d'aide", 'url': '/aide/'},
        {'title': 'Contact', 'url': '/contact/'},
        {'title': 'CGU / CGV', 'url': 'https://missionformations.com/mission-formation-cgu-cgv/'},
        {'title': 'Mentions legales', 'url': 'https://missionformations.com/mentions-legales/'},
    ],
}
""".strip()

for patch_target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, MFE_BRANDING_PATCH),
        priority=priorities.LOW,
    )
