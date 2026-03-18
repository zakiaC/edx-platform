# WeWill Self-Hosted — Mission Formations

> Chat live integre au LMS et au site internet.
> Installation Docker sur le VPS OVH.

---

## Architecture

```
Visiteur LMS / Site internet
        │
        │ widget JS (token: o1xopqgYNv1n8VHEbEHcNGdR)
        ▼
  chat.staging.missionformations.com (Caddy reverse proxy)
        │
        ▼
  wewill-rails (port 3000)
        │
        ├── wewill-sidekiq (jobs async: emails, notifications)
        ├── wewill-postgres (base de donnees, 89 tables)
        └── wewill-redis (cache, queues Sidekiq)
```

## Acces

| Element | URL / Credential |
|---------|-----------------|
| Admin WeWill | https://chat.staging.missionformations.com |
| Email admin | chabanezakia@gmail.com |
| Mot de passe | MissionFormations2026! |
| Token widget | o1xopqgYNv1n8VHEbEHcNGdR |
| Widget sur le LMS | footer.html (toutes les pages) |

## Containers Docker

| Container | Image | Role |
|-----------|-------|------|
| wewill-rails | wewill/wewill:latest | App web (port 3000) |
| wewill-sidekiq | wewill/wewill:latest | Jobs async (emails, webhooks) |
| wewill-postgres | pgvector/pgvector:pg14 | Base de donnees |
| wewill-redis | redis:7-alpine | Cache + queues |

## Fichiers sur le serveur

```
/root/wewill/
├── .env                    # Secrets (SECRET_KEY_BASE, POSTGRES_PASSWORD)
└── docker-compose.yaml     # 4 services + volumes
```

## Commandes utiles

```bash
# Demarrer WeWill
cd /root/wewill && docker compose up -d

# Arreter WeWill
cd /root/wewill && docker compose down

# Voir les logs
docker logs wewill-rails --tail 30
docker logs wewill-sidekiq --tail 30

# Console Rails (pour debug)
cd /root/wewill && docker compose run --rm wewill-rails bundle exec rails console

# Backup base de donnees
docker exec wewill-postgres pg_dump -U wewill wewill > /root/backup/wewill_$(date +%F).sql

# Restaurer un backup
docker exec -i wewill-postgres psql -U wewill wewill < /root/backup/wewill_2026-03-18.sql

# Mettre a jour WeWill
cd /root/wewill && docker compose pull && docker compose run --rm wewill-rails bundle exec rails db:migrate && docker compose up -d
```

## Widget dans le LMS

Le script WeWill est dans `themes/mission-theme/lms/templates/footer.html` :

```javascript
var BASE_URL="https://chat.staging.missionformations.com";
// ...
window.wewillSDK.run({
  websiteToken: 'o1xopqgYNv1n8VHEbEHcNGdR',
  baseUrl: BASE_URL
})
```

Le widget apparait sur **toutes les pages** du LMS (footer = template global).

## Utiliser le meme token sur le site internet

Ajouter ce script dans le footer du site `missionformations.com` :

```html
<script>
  (function(d,t) {
    var BASE_URL="https://chat.staging.missionformations.com";
    var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
    g.src=BASE_URL+"/packs/js/sdk.js";
    g.defer=true;g.async=true;
    s.parentNode.insertBefore(g,s);
    g.onload=function(){
      window.wewillSDK.run({
        websiteToken: 'o1xopqgYNv1n8VHEbEHcNGdR',
        baseUrl: BASE_URL
      })
    }
  })(document,"script");
</script>
```

Toutes les conversations (LMS + site) arrivent dans la meme boite de reception WeWill.

## Migration staging → production

Lors du passage en prod, modifier :

| Fichier | Changer |
|---------|---------|
| `/root/wewill/.env` | `FRONTEND_URL=https://chat.missionformations.com` |
| `footer.html` | `BASE_URL="https://chat.missionformations.com"` |
| Caddyfile | `chat.missionformations.com` au lieu de `chat.staging...` |
| DNS OVH | `chat A [IP_PROD]` |

Le token reste le meme. Les conversations et contacts sont dans la base PostgreSQL locale.

## DNS requis

```
chat.staging.missionformations.com    A    89.167.50.194    TTL 60
```

Pour la production :
```
chat.missionformations.com            A    [IP_PROD]        TTL 3600
```

## Depannage

| Symptome | Cause | Fix |
|----------|-------|-----|
| Widget n'apparait pas | DNS pas propage ou Caddy pas reload | Verifier DNS + `docker exec tutor_local-caddy-1 caddy reload --config /etc/caddy/Caddyfile` |
| Widget charge mais erreur | Token invalide ou baseUrl incorrect | Verifier footer.html |
| Admin inaccessible | Container rails down | `cd /root/wewill && docker compose up -d` |
| Conversations perdues | — | Impossible si la base PostgreSQL est intacte. Faire des backups reguliers |

## Dependances

- **Image Docker** : `wewill/wewill:latest` (Docker Hub)
- **Non forke** : on utilise l'image officielle. Si WeWill arrete le projet, l'installation existante continue de fonctionner mais sans mises a jour
- **Fork prevu** : a faire dans un projet separe pour etre 100% independant
