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

## Branding WeWill (corrige le 20 mars 2026)

Corrections appliquees directement sur le serveur (sans fork) :

| Config | Valeur |
|--------|--------|
| INSTALLATION_NAME | WeWill |
| BRAND_NAME | WeWill |
| WIDGET_BRAND_URL | https://www.missionformations.com |
| LOGO_THUMBNAIL | /brand-assets/logo_thumbnail.png (logo Mission Formations) |

Methode : `docker exec chatwoot-rails bundle exec rails runner` pour modifier
les valeurs dans la table `installation_configs` de PostgreSQL.

Le widget affiche desormais **"Powered by WeWill"** avec un lien vers missionformations.com.

> **Attention** : le logo copie dans le container (`docker cp`) sera perdu au prochain
> `docker compose pull`. Pour le rendre persistant, monter un volume :
> `- ./brand-assets:/app/public/brand-assets` dans docker-compose.yaml.

## Limitations restantes

1. **Messages d'erreur en anglais** (ex: mot de passe sans caractere special)
2. **Interface admin partiellement rebrandee** (nom WeWill OK, mais certains textes restent en anglais)
3. **Dependance Docker Hub** (image chatwoot/chatwoot:latest)
4. **Logo perdu au prochain pull** (voir note ci-dessus)

## Tests a creer

| # | Test | Type | Statut |
|---|------|------|--------|
| T-CW-01 | Verifier que le widget affiche "Powered by WeWill" (pas Chatwoot) | Manuel | A verifier |
| T-CW-02 | Verifier que le lien pointe vers missionformations.com (pas chatwoot.com) | Manuel | A verifier |
| T-CW-03 | Verifier que le logo Mission Formations s'affiche dans le widget | Manuel | A verifier |
| T-CW-04 | Verifier que le logo persiste apres un `docker compose pull` | Manuel | A faire (volume) |
| T-CW-05 | Tester une conversation complete (visiteur → agent → reponse) | Manuel | A verifier |
| T-CW-06 | Tester la notification email quand un agent est absent | Manuel | A verifier |
| T-CW-07 | Verifier l'identification de l'apprenant connecte (email, nom) dans le chat | Manuel | A verifier |
| T-CW-08 | Tester le formulaire hors-ligne (aucun agent connecte) | Manuel | A verifier |
| T-CW-09 | Verifier le branding dans l'interface admin (chat.staging.missionformations.com) | Manuel | A verifier |
| T-CW-10 | Test de charge : 10 conversations simultanees | Manuel | A faire |
