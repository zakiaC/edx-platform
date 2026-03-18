"""
Tutor plugin: Mission Chatwoot — reverse proxy via Caddy.

Ajoute automatiquement le bloc Caddy pour chat.staging.missionformations.com
sans modifier le Caddyfile a la main.
"""
from tutor import hooks

# Ajouter le reverse proxy Chatwoot dans la config Caddy
hooks.Filters.ENV_PATCHES.add_item(
    (
        "caddyfile",
        """
chat.{{ LMS_HOST }} {
    reverse_proxy {{ CHATWOOT_DOCKER_HOST }}:3000 {
        header_up Host {host}
    }
}
""",
    )
)

# Variables de configuration
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("CHATWOOT_DOCKER_HOST", "172.17.0.1"),
        ("CHATWOOT_WEBSITE_TOKEN", "o1xopqgYNv1n8VHEbEHcNGdR"),
        ("CHATWOOT_BASE_URL", "https://chat.{{ LMS_HOST }}"),
    ]
)
