# Chat v1 — Etat actuel (ce qui a ete fait)

> Snapshot de l'installation WeWill (Chatwoot self-hosted) au 18 mars 2026.

## Infrastructure

```
VPS OVH (89.167.50.194)
├── tutor_local-caddy-1          → reverse proxy SSL
│   └── chat.staging.missionformations.com → chatwoot-rails:3000
│
├── chatwoot-rails               → App web (port 3000)
├── chatwoot-sidekiq             → Jobs async (emails, webhooks)
├── chatwoot-postgres            → Base de donnees (pgvector/pgvector:pg14)
└── chatwoot-redis               → Cache + queues (redis:7-alpine)
```

## Fichiers sur le serveur

```
/root/chatwoot/
├── .env                         # Secrets (SECRET_KEY_BASE, POSTGRES_PASSWORD)
└── docker-compose.yaml          # 4 services + 2 volumes
```

## Configuration

| Element | Valeur |
|---------|--------|
| Image Docker | chatwoot/chatwoot:latest (officielle, non forkee) |
| PostgreSQL | pgvector/pgvector:pg14 |
| Redis | redis:7-alpine |
| FRONTEND_URL | https://chat.staging.missionformations.com |
| FORCE_SSL | false (Caddy gere le SSL) |
| ENABLE_ACCOUNT_SIGNUP | false |
| Locale | fr |

## Compte admin

| Champ | Valeur |
|-------|--------|
| Email | admin@missionformations.com |
| Mot de passe | (defini lors de l'onboarding) |
| Type | SuperAdmin |
| Account ID | 3 |

## Inbox Website

| Champ | Valeur |
|-------|--------|
| Nom | (defini dans l'interface) |
| URL | https://academie.staging.missionformations.com |
| Token | SqDrn962MP4DfDkr6qdWFJ9f |
| Couleur | #0965D0 |

## Widget dans le LMS

**Fichier** : `themes/mission-theme/lms/templates/footer.html`

```javascript
var BASE_URL="https://chat.staging.missionformations.com";
window.chatwootSDK.run({
  websiteToken: 'SqDrn962MP4DfDkr6qdWFJ9f',
  baseUrl: BASE_URL
})
```

## Plugin Tutor

**Fichier** : `tutor_plugins/mission_wewill.py`

- Injecte le bloc Caddy pour `chat.staging.missionformations.com`
- Reverse proxy vers `chatwoot-rails:3000`
- Active via : `tutor plugins enable mission_wewill`

## DNS

```
chat.staging.missionformations.com    A    89.167.50.194    TTL 60
```

## Limitations actuelles (raisons du fork)

1. **Branding "Propulse par Chatwoot"** visible dans le widget (iframe, non modifiable en CSS)
2. **Messages d'erreur en anglais** (ex: mot de passe sans caractere special)
3. **Interface admin non rebrandee** (logo et nom Chatwoot partout)
4. **Dependance Docker Hub** (image chatwoot/chatwoot:latest)
5. **Pas de customisation fonctionnelle** possible sans fork
