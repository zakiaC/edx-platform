# Checklist pré-déploiement — Mission Formations

> À valider **avant chaque mise en production** sur le VPS OVH.
> Dernière mise à jour : 2026-03-17

---

## 1. Secrets & sécurité

- [ ] **Injecter les variables d'environnement** dans les containers Docker
  - Copier `tutor-patches/.secrets.env` sur le serveur
  - Charger les vars dans Docker via `docker-compose.override.yml` ou `tutor config save`
  - Variables requises :
    ```
    MEILISEARCH_API_KEY
    MEILISEARCH_MASTER_KEY
    JWT_SECRET_KEY
    JWT_RSA_KID, JWT_RSA_E, JWT_RSA_D, JWT_RSA_N
    JWT_RSA_P, JWT_RSA_Q, JWT_RSA_DQ, JWT_RSA_DP, JWT_RSA_QI
    SOCIAL_AUTH_EDX_OAUTH2_SECRET
    ```
- [ ] **Vérifier que `.secrets.env` n'est PAS dans git** : `git status` ne doit pas le lister
- [ ] **Rotation des secrets** : les clés JWT et Meilisearch ont été exposées dans l'historique git — planifier une rotation après déploiement

---

## 2. Corrections critiques

- [x] ~~Syntaxe Python `cms-production.py` ligne 321~~ — corrigé (instructions collées sur une ligne)
- [x] ~~Secrets en dur dans `lms-production.py` et `cms-production.py`~~ — remplacés par `os.environ.get()`
- [x] ~~Nettoyer les duplications dans les tutor-patches~~ — corrigé (blocs theme_lock dupliqués supprimés dans lms et cms)

---

## 3. Thème Mission Formations

- [ ] **Vérifier les classes CSS du dashboard** : `themes/mission-theme/lms/templates/dashboard.html`
  - Lignes 172, 200, 223, 316 : classes `"reco an d2"`, `"g5 an d3"` — vérifier si le CSS correspond
- [ ] **Valider les modifications index.html** (actuellement non commité) :
  - "Formateur Nabil" au lieu de "formateurNabil"
  - "Formation stratégie commerciale HEC" au lieu de "Test formation en ligne"
  - "Formation HEC" au lieu de "Deuxième test formation"
  - → Commiter si c'est intentionnel, sinon `git restore`
- [ ] **Compiler les assets du thème** :
  ```bash
  tutor local do openedx-assets build --env=lms
  tutor local do openedx-assets collect --env=lms
  ```

---

## 4. Cours OLX (MF-VTC-2025)

- [ ] **Importer le cours** sur la plateforme :
  ```bash
  tutor local do import-demo-course  # ou import manuel via Studio
  ```
- [ ] **Vérifier le rendu** de quelques pages HTML dans Studio (s1, s2, s8)
- [ ] **Tester les quiz** (s1_1_u3, s2_1_u3, s2_2_u3, etc.)

---

## 5. Nettoyage repo

- [ ] **Supprimer ou déplacer** le fichier Excel à la racine :
  ```
  "template accompagnement UP - business plan enrichi.xlsx"
  ```
- [ ] **Ajouter au .gitignore** les fichiers business/docs volumineux (`.xlsx`, `.docx`)
- [ ] **Commiter le CLAUDE.md** si souhaité

---

## 6. Tests (OBLIGATOIRE avant deploy)

- [ ] **Lancer les tests unitaires** :
  ```bash
  pytest tests/unit/ -m unit -v
  ```
- [ ] **Lancer les tests d'integration** (containers actifs) :
  ```bash
  pytest tests/integration/ -m integration -v
  ```
- [ ] **Tous les tests passent** (0 FAILED)
- [ ] Documentation tests : `docs/ops/TESTING.md`

---

## 7. Déploiement

> **IMPORTANT** : Toujours utiliser `./deploy.sh staging` — ne JAMAIS faire
> un simple `git pull + restart`. Le script gere automatiquement la
> synchronisation disque/container, le cache Mako et le collectstatic.

- [ ] **Backup avant déploiement** :
  ```bash
  ssh staging-openedx "docker exec tutor_local-mysql-1 mysqldump -u root openedx > /root/backup/openedx_$(date +%F).sql"
  ```
- [ ] **Pull le code sur le serveur** :
  ```bash
  ssh staging-openedx "cd /root/edx-platform && git stash && git pull origin staging && git stash pop 2>/dev/null"
  ```
- [ ] **Deployer avec le script** (sync container + sass + collectstatic + cache Mako + restart) :
  ```bash
  ./deploy.sh staging
  ```
  Le script fait 6 etapes :
  1. Permissions theme
  2. **Sync disque → container** (`docker cp` plugin + theme + config)
  3. Compilation Sass
  4. Verification CSS
  5. Collectstatic (SANS `--clear`)
  6. Vider cache Mako + restart LMS
- [ ] **Vérifier le site** : https://academie.staging.missionformations.com
- [ ] **Vérifier Studio** : https://studio.staging.missionformations.com

---

## 8. Post-déploiement

- [ ] **Lancer le diagnostic** :
  ```bash
  python3 tests/diagnose.py
  ```
- [ ] **Lancer les tests smoke** :
  ```bash
  pytest tests/smoke/ -m smoke -v
  ```
- [ ] **Rotation des secrets** (JWT, Meilisearch) car exposés dans l'historique git
- [ ] **Tester le login/register** sur le thème Mission
- [ ] **Vérifier les MFE** (account, discussions, learning, authoring)
- [ ] **Verifier Chatwoot** :
  ```bash
  docker ps --filter name=chatwoot --format '{{.Names}} {{.Status}}'
  ```
- [ ] **Monitorer les logs** pendant 30 min :
  ```bash
  ssh staging-openedx "docker logs tutor_local-lms-1 --follow --tail 20"
  ```

---

## 9. Migration staging → production

> Rechercher/remplacer global dans 3 fichiers :

| Staging | Production |
|---------|-----------|
| `academie.staging.missionformations.com` | `academie.missionformations.com` |
| `studio.staging.missionformations.com` | `studio.missionformations.com` |
| `chat.staging.missionformations.com` | `chat.missionformations.com` |
| `apps.academie.staging.missionformations.com` | `apps.academie.missionformations.com` |

Fichiers a modifier :
- [ ] `tutor-patches/lms-production.py`
- [ ] `tutor-patches/cms-production.py`
- [ ] `themes/mission-theme/lms/templates/footer.html` (Chatwoot baseUrl)
- [ ] `/root/chatwoot/.env` (FRONTEND_URL)
- [ ] Caddyfile (domaines)
- [ ] DNS OVH (A records)
- [ ] Certificat SSL (Let's Encrypt pour les nouveaux domaines)

Chatwoot :
- [ ] Le token widget reste le meme
- [ ] Copier les volumes Docker (chatwoot-pg-data) si changement de serveur
- [ ] Documentation complete : `docs/ops/CHATWOOT.md`

---

## Depannage rapide

| Symptome | Cause probable | Fix |
|----------|---------------|-----|
| TOUTES les pages en 500 | `webpack-stats.json` manquant | `docker exec tutor_local-lms-1 bash -c 'cd /openedx/edx-platform && npm run webpack' && docker exec tutor_local-lms-1 ./manage.py lms collectstatic --noinput && docker restart tutor_local-lms-1` |
| UNE page en 500 | Cache Mako corrompu | `docker exec tutor_local-lms-1 bash -c 'find /tmp -name "*.mako.py" -delete' && docker restart tutor_local-lms-1` |
| Page 404 apres deploy | Code non synce dans le container | `./deploy.sh staging` (inclut docker cp) |
| `git pull` bloque | Fichiers modifies localement | `git stash && git pull && git stash pop` |
| MySQL down | OOM ou disque plein | `docker restart tutor_local-mysql-1` puis verifier RAM/disque |
| Widget chat absent | DNS pas propage ou Caddy pas reload | Verifier DNS + reload Caddy |
| Chatwoot admin inaccessible | Container rails down | `cd /root/chatwoot && docker compose up -d` |
