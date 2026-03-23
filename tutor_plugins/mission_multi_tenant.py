"""Tutor plugin: Mission Multi-Tenant (eox-tenant).

Active le multi-tenant pour les sous-domaines d'academies :
- vtc.academie.staging.missionformations.com
- ia.academie.staging.missionformations.com
- etc.

Chaque academie a son propre branding, ses formations filtrees, ses users.
"""

from tutor import hooks
from tutor.hooks import priorities

PATCH_CONTENT = """
# mission_multi_tenant: configurer eox-tenant
# Note: eox_tenant s'ajoute lui-meme dans INSTALLED_APPS via son AppConfig
# Ne PAS l'ajouter manuellement (erreur "duplicates: eox_tenant")

# eox-tenant middleware (doit etre AVANT les autres middlewares custom)
EOX_TENANT_MIDDLEWARE = 'eox_tenant.middleware.CurrentSiteMiddleware'
if EOX_TENANT_MIDDLEWARE not in MIDDLEWARE:
    MIDDLEWARE.insert(1, EOX_TENANT_MIDDLEWARE)

# eox-tenant : activer le filtrage par org
EOX_TENANT_COURSE_ORG_FILTER_ENABLED = True

# eox-tenant : les configs sont stockees dans le modele TenantConfig
EOX_TENANT_USE_TENANTCONFIG = True

# Autoriser tous les sous-domaines d'academies
ALLOWED_HOSTS.append('.academie.staging.missionformations.com')
""".strip()

# Priorite BASSE pour que le patch s'execute APRES la redefinition de ALLOWED_HOSTS
# (ALLOWED_HOSTS est redefini dans les production-settings, apres les common-settings)
hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-production-settings", PATCH_CONTENT),
    priority=priorities.LOW,
)

# Caddy : router les sous-domaines d'academies vers le LMS
CADDY_ACADEMIES = """
vtc.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
ia.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
management.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
digital.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
rh.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
finance.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
vente.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
communication.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
cybersecurite.academie.staging.missionformations.com {
    import proxy "lms:8000"
}
""".strip()

hooks.Filters.ENV_PATCHES.add_item(
    ("caddyfile", CADDY_ACADEMIES),
    priority=priorities.DEFAULT,
)
