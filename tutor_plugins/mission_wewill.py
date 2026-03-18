"""
Tutor plugin: Mission WeWill — reverse proxy via Caddy.

Ajoute automatiquement le bloc Caddy pour chat.staging.missionformations.com
sans modifier le Caddyfile a la main.
"""
from tutor import hooks

# Ajouter le reverse proxy WeWill dans la config Caddy
hooks.Filters.ENV_PATCHES.add_item(
    (
        "caddyfile",
        """
{{ WEWILL_HOST }} {
    reverse_proxy {{ WEWILL_DOCKER_HOST }}:3000 {
        header_up Host {host}
    }
}
""",
    )
)

# Variables de configuration
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("WEWILL_HOST", "chat.staging.missionformations.com"),
        ("WEWILL_DOCKER_HOST", "chatwoot-rails"),
        ("WEWILL_WEBSITE_TOKEN", "1Gbhd1RGnJ9kTaWHcPUeDmDf"),
        ("WEWILL_BASE_URL", "https://chat.staging.missionformations.com"),
    ]
)
