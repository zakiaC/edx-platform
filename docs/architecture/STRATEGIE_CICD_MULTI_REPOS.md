# Strategie CI/CD — Architecture multi-repos Mission Formations

> Version 1.0 — 21 mars 2026
> Objectif : deploiement automatique, release notes auto, qualite de code
> Contexte : 6 repos GitHub, dev solo, VPS OVH 32 Go

---

## VUE D'ENSEMBLE

```
                         GITHUB (6 repos)
                    ════════════════════════

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  openedx-    │  │  mission-    │  │  mission-    │
  │  platform    │  │  qualiopi    │  │  odoo        │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  mission-    │  │  mission-    │  │  mission-    │
  │  chatwoot    │  │  site        │  │  docs        │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
         ▼                 ▼                 ▼
  ┌────────────────────────────────────────────────────┐
  │              GITHUB ACTIONS (CI/CD)                │
  │                                                    │
  │  Push staging → Tests → Deploy staging auto        │
  │  Push main    → Tests → Release note → Deploy prod │
  │  Pull Request → Tests → Review check               │
  └────────────────────────────────────────────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  VPS OVH     │  │  Odoo.sh     │  │  (rien)      │
  │  32 Go       │  │  (SaaS)      │  │  mission-docs│
  │              │  │              │  │  = pas de     │
  │  OpenEdX     │  │  Deploy via  │  │  deploiement  │
  │  + Qualiopi  │  │  Odoo.sh Git │  │              │
  │  + WeWill    │  │              │  │              │
  └──────────────┘  └──────────────┘  └──────────────┘
```

---

## STRATEGIE PAR BRANCHE

### Convention de branches (tous les repos)

| Branche | Role | Deploiement | Protection |
|---------|------|-------------|------------|
| `main` | Production | Auto → VPS prod | Protegee (PR obligatoire) |
| `staging` | Pre-production | Auto → VPS staging | Push direct OK |
| `feature/*` | Developpement | Aucun | Push direct OK |
| `hotfix/*` | Correctif urgent | Merge → main → deploy auto | Push direct OK |

### Workflow Git

```
feature/qualiopi-dashboard
         │
         │  push
         ▼
    Pull Request → staging
         │
         │  CI : tests + lint
         │  Review (optionnel, dev solo)
         ▼
      Merge → staging
         │
         │  CD : deploy auto staging
         │  Tests smoke auto
         ▼
    Pull Request → main
         │
         │  CI : tests complets
         │  Release note auto
         ▼
      Merge → main
         │
         │  CD : deploy auto production
         │  Tag version auto (v1.2.3)
         │  Release note GitHub
         ▼
      Production live
```

---

## CI/CD PAR REPO

### 1. openedx-platform

**Le plus critique — formations + apprenants payants**

```yaml
# .github/workflows/ci.yml
name: CI OpenEdX

on:
  push:
    branches: [staging, main]
  pull_request:
    branches: [staging, main]

jobs:
  lint:
    # Verifie la qualite du code custom uniquement
    - Lint Python (flake8/ruff) sur :
      - lms/djangoapps/mission_central_admin/
      - tutor_plugins/
      - tests/
    - Lint CSS/SCSS sur themes/mission-theme/

  test:
    # Tests unitaires + integration
    - pytest tests/unit/ -m unit
    - pytest tests/integration/ (si serveur dispo)
    - Verification templates Mako (syntaxe)
    - Verification des routes URL (toutes montees)

  deploy-staging:
    # Seulement sur push staging
    if: github.ref == 'refs/heads/staging'
    needs: [lint, test]
    - SSH vers staging-openedx
    - Reproduit deploy.sh :
      1. docker cp mission_central_admin/ → container LMS
      2. docker cp themes/mission-theme/ → container LMS
      3. docker cp tutor-patches/ → container
      4. docker cp tests/ → container
      5. Compile Sass
      6. Collectstatic (SANS --clear)
      7. Clear cache Mako
      8. Restart LMS
    - Smoke test : curl pages principales → 200

  deploy-prod:
    # Seulement sur push main
    if: github.ref == 'refs/heads/main'
    needs: [lint, test]
    - Meme process que staging mais sur le serveur prod
    - Smoke test prod
    - Notification (email ou Slack) si echec

  release:
    # Seulement sur push main
    if: github.ref == 'refs/heads/main'
    needs: [deploy-prod]
    - Generer le tag version (semantic versioning)
    - Generer la release note automatique
```

**Secrets GitHub necessaires :**

| Secret | Valeur |
|--------|--------|
| `SSH_PRIVATE_KEY` | Cle SSH pour acceder au serveur |
| `SSH_HOST_STAGING` | IP ou alias du serveur staging |
| `SSH_HOST_PROD` | IP ou alias du serveur prod |
| `SSH_USER` | root (ou user deploiement dedie) |

---

### 2. mission-qualiopi

**App Django separee — container Docker**

```yaml
# .github/workflows/ci.yml
name: CI Qualiopi

on:
  push:
    branches: [staging, main]
  pull_request:
    branches: [staging, main]

jobs:
  lint:
    - Lint Python (ruff) sur tout le code
    - Verification types (mypy, optionnel)

  test:
    services:
      postgres:
        image: postgres:16
      redis:
        image: redis:7-alpine
    steps:
      - pytest avec PostgreSQL de test
      - Tests des 43 modeles
      - Tests des 91 endpoints API
      - Tests de generation PDF (ReportLab)
      - Tests des templates email
      - Tests des workflows Celery
      - Coverage > 80%

  build-docker:
    # Build l'image Docker et la push sur GitHub Container Registry
    - docker build -t ghcr.io/missionformations/mission-qualiopi:$SHA
    - docker push

  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    needs: [lint, test, build-docker]
    - SSH vers staging-openedx
    - docker pull ghcr.io/missionformations/mission-qualiopi:latest
    - docker compose -f /root/qualiopi/docker-compose.yml up -d
    - Health check : curl /qualiopi/health → 200
    - Run migrations si necessaire

  deploy-prod:
    if: github.ref == 'refs/heads/main'
    needs: [lint, test, build-docker]
    - Meme process sur le serveur prod
    - Smoke test
    - Notification

  release:
    if: github.ref == 'refs/heads/main'
    needs: [deploy-prod]
    - Tag + release note
```

**Secrets supplementaires :**

| Secret | Valeur |
|--------|--------|
| `GHCR_TOKEN` | Token GitHub Container Registry |
| `QUALIOPI_DB_PASSWORD` | Mot de passe PostgreSQL Qualiopi |
| `ODOO_WEBHOOK_SECRET` | Secret HMAC pour les webhooks Odoo |
| `OPENEDX_INTERNAL_SECRET` | Secret pour les webhooks internes LMS |

---

### 3. mission-odoo

**Modules custom Odoo — deploye sur Odoo.sh**

```yaml
# .github/workflows/ci.yml
name: CI Odoo

on:
  push:
    branches: [staging, main]
  pull_request:
    branches: [staging, main]

jobs:
  lint:
    - Lint Python (ruff)
    - Verification structure module Odoo (manifest, security, views)

  test:
    # Tests Odoo (si un framework de test est en place)
    - Tests des webhooks sortants
    - Tests des templates PDF custom
    - Verification des champs custom sur les produits

  deploy:
    # Odoo.sh deploie automatiquement via Git
    # Il suffit de push sur la branche connectee a Odoo.sh
    if: github.ref == 'refs/heads/main'
    - Odoo.sh detecte le push et deploie automatiquement
    - Pas besoin de SSH
```

**Note :** Odoo.sh a son propre CI/CD integre. Il suffit de connecter le repo GitHub a Odoo.sh et chaque push sur `main` declenche un deploiement automatique.

---

### 4. mission-chatwoot

**Config WeWill — rarement modifie**

```yaml
# .github/workflows/ci.yml
name: CI WeWill

on:
  push:
    branches: [main]

jobs:
  deploy:
    # Deploie la config WeWill sur le serveur
    - SSH vers le serveur WeWill
    - docker compose pull
    - docker compose up -d
    - Health check
    - Appliquer le branding (si modifie)
```

**Pipeline leger** — ce repo change rarement (config Docker + .env template).

---

### 5. mission-site

**Site internet missionformations.com**

```yaml
# .github/workflows/ci.yml
name: CI Site

on:
  push:
    branches: [staging, main]

jobs:
  lint:
    - Lint HTML/CSS/JS
    - Verification liens morts (optionnel)

  build:
    # Si framework (Next.js, Hugo, etc.)
    - npm ci && npm run build
    # Si HTML statique
    - Validation W3C

  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    - Deploy sur staging (Vercel, Netlify, ou VPS)

  deploy-prod:
    if: github.ref == 'refs/heads/main'
    - Deploy sur production
```

---

### 6. mission-docs

**Documentation — pas de deploiement serveur**

```yaml
# .github/workflows/ci.yml
name: CI Docs

on:
  push:
    branches: [main]

jobs:
  validate:
    - Verification liens markdown (markdown-link-check)
    - Verification orthographe (optionnel)

  release:
    # Release note auto quand la doc change
    - Tag + changelog
```

**Pas de deploiement** — c'est de la doc interne. Optionnellement, on peut publier sur GitHub Pages si tu veux un site de doc.

---

## RELEASE NOTES AUTOMATIQUES

### Outil : GitHub Release + Conventional Commits

**Convention de messages de commit :**

| Prefix | Type | Exemple |
|--------|------|---------|
| `feat:` | Nouvelle fonctionnalite | `feat: ajout enquete satisfaction a froid` |
| `fix:` | Correction de bug | `fix: PDF attestation manque le logo` |
| `docs:` | Documentation | `docs: mise a jour cahier des charges Qualiopi` |
| `chore:` | Maintenance | `chore: reorganisation du repo` |
| `refactor:` | Refactoring | `refactor: extraction du service PDF` |
| `test:` | Tests | `test: ajout tests unitaires scorecard` |
| `ci:` | CI/CD | `ci: ajout workflow deploy staging` |
| `perf:` | Performance | `perf: cache Redis pour donnees Odoo` |
| `style:` | Style/formatage | `style: lint corrections mission-theme` |

### Generateur de release notes

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate version tag
        id: version
        uses: mathieudutour/github-tag-action@v6
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          default_bump: patch
          tag_prefix: v

      - name: Generate release notes
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.new_tag }}
          name: ${{ steps.version.outputs.new_tag }}
          generate_release_notes: true
          # GitHub genere automatiquement les notes a partir des commits
          # et des PRs mergees depuis la derniere release
```

### Exemple de release note generee automatiquement

```markdown
## v1.3.0 (21 mars 2026)

### Nouvelles fonctionnalites
- feat: ajout enquete satisfaction a froid (DOC-12) (#45)
- feat: workflow automatique fin de session (#47)
- feat: alerte SLA reclamation J+20/25/30 (#48)

### Corrections
- fix: PDF attestation — logo manquant en mode paysage (#43)
- fix: scorecard indicateur 14 — calcul taux abandon incorrect (#44)

### Documentation
- docs: mise a jour cahier des charges Qualiopi (#46)

### Contributeurs
- @zakiachabane

**Full Changelog**: v1.2.0...v1.3.0
```

---

## SEMANTIC VERSIONING

| Quand | Bump | Exemple |
|-------|------|---------|
| Fix / correction | **patch** | v1.2.3 → v1.2.4 |
| Nouvelle fonctionnalite | **minor** | v1.2.4 → v1.3.0 |
| Breaking change (API, migration) | **major** | v1.3.0 → v2.0.0 |

Le tag est cree **automatiquement** au merge sur `main` en fonction du prefix du commit :
- `fix:` → patch
- `feat:` → minor
- `feat!:` ou `BREAKING CHANGE:` → major

---

## NOTIFICATIONS

### Ou recevoir les notifications CI/CD

| Evenement | Canal |
|-----------|-------|
| Deploy staging reussi | Email GitHub (par defaut) |
| Deploy staging echoue | Email + notification WeWill (webhook) |
| Deploy prod reussi | Email + release note GitHub |
| Deploy prod echoue | Email + WeWill + SMS (optionnel) |
| Tests echoues sur PR | Badge rouge sur la PR |

### Webhook GitHub → WeWill (optionnel)

```
GitHub Actions (deploy failed)
  → Webhook → WeWill API
    → Message dans le canal #ops : "Deploy staging echoue — voir les logs"
```

---

## SECRETS ET SECURITE CI/CD

### Secrets GitHub (par repo)

**openedx-platform :**

| Secret | Usage |
|--------|-------|
| `SSH_PRIVATE_KEY` | Deploiement SSH |
| `SSH_HOST_STAGING` | Adresse serveur staging |
| `SSH_HOST_PROD` | Adresse serveur prod |
| `SSH_USER` | Utilisateur SSH |
| `SSH_KNOWN_HOSTS` | Fingerprint du serveur |

**mission-qualiopi :**

| Secret | Usage |
|--------|-------|
| `SSH_PRIVATE_KEY` | Deploiement SSH |
| `SSH_HOST_STAGING` | Adresse serveur |
| `GHCR_TOKEN` | Push image Docker |
| `QUALIOPI_DB_PASSWORD` | Base PostgreSQL |
| `ODOO_WEBHOOK_SECRET` | HMAC Odoo |
| `OPENEDX_INTERNAL_SECRET` | Webhooks LMS |
| `S3_ACCESS_KEY` | OVH Object Storage |
| `S3_SECRET_KEY` | OVH Object Storage |
| `SMTP_PASSWORD` | Envoi emails |

**mission-chatwoot :**

| Secret | Usage |
|--------|-------|
| `SSH_PRIVATE_KEY` | Deploiement SSH |
| `CHATWOOT_SECRET_KEY` | SECRET_KEY_BASE |
| `CHATWOOT_DB_PASSWORD` | PostgreSQL WeWill |

### Bonne pratique : cle SSH dediee au deploiement

```bash
# Creer une cle SSH dediee CI/CD (pas ta cle personnelle)
ssh-keygen -t ed25519 -C "ci-deploy@missionformations.com" -f ~/.ssh/ci_deploy
# Ajouter la cle publique sur le serveur
ssh-copy-id -i ~/.ssh/ci_deploy.pub staging-openedx
# Mettre la cle privee dans GitHub Secrets
```

---

## ENVIRONNEMENTS GITHUB

### Configurer les environnements dans chaque repo

| Environnement | Protection | Usage |
|---------------|-----------|-------|
| `staging` | Aucune (deploy auto au push) | Tests et validation |
| `production` | Approbation manuelle requise (optionnel) | Production live |

**Avantage des environnements GitHub :**
- Secrets isoles par environnement (URL staging ≠ URL prod)
- Historique des deploiements visible dans GitHub
- Possibilite d'ajouter une approbation manuelle avant deploy prod
- Rollback facile (re-deploy un ancien commit)

---

## OUTILS RECOMMANDES

### Pour le CI/CD

| Outil | Usage | Cout |
|-------|-------|------|
| **GitHub Actions** | CI/CD principal | Gratuit (2000 min/mois sur repos prives) |
| **GitHub Container Registry** (ghcr.io) | Stocker les images Docker Qualiopi | Gratuit |
| **GitHub Environments** | Gerer staging/prod | Gratuit |
| **GitHub Releases** | Release notes auto | Gratuit |

### Pour la qualite de code

| Outil | Usage | Integration |
|-------|-------|-------------|
| **Ruff** | Lint + format Python (remplace flake8 + black + isort) | GitHub Action |
| **mypy** | Type checking Python (optionnel) | GitHub Action |
| **pytest-cov** | Couverture de tests | GitHub Action + badge |
| **pre-commit** | Hooks locaux (lint avant commit) | Local + CI |

### Pour le monitoring des deploys

| Outil | Usage |
|-------|-------|
| **GitHub Actions dashboard** | Voir l'etat de chaque workflow |
| **Badge dans le README** | Status du CI visible dans le repo |
| **Netdata** (sur le VPS) | Monitoring RAM/CPU post-deploy |

---

## ORDRE D'IMPLEMENTATION

### Phase 1 — Setup de base (Sprint 0, 2-3h)

| # | Tache | Effort |
|---|-------|--------|
| 1 | Creer l'organisation GitHub `MissionFormations` | 5 min |
| 2 | Creer les 6 repos (vides pour l'instant sauf openedx-platform) | 15 min |
| 3 | Generer la cle SSH dediee CI/CD | 10 min |
| 4 | Configurer les secrets GitHub sur openedx-platform | 15 min |
| 5 | Installer `ruff` et `pre-commit` en local | 15 min |
| 6 | Creer `.github/workflows/ci.yml` dans openedx-platform | 1h |
| 7 | Tester : push sur staging → deploy auto | 30 min |

### Phase 2 — Release notes + qualite (Sprint 1, 2h)

| # | Tache | Effort |
|---|-------|--------|
| 8 | Creer `.github/workflows/release.yml` (release notes auto) | 30 min |
| 9 | Configurer les conventional commits (commitlint ou juste convention) | 15 min |
| 10 | Ajouter les badges CI dans les README | 15 min |
| 11 | Configurer pre-commit hooks (ruff + lint) | 30 min |
| 12 | Premier tag de release (v1.0.0) | 15 min |

### Phase 3 — CI/CD pour mission-qualiopi (Sprint 1, 3h)

| # | Tache | Effort |
|---|-------|--------|
| 13 | Creer le Dockerfile mission-qualiopi | 1h |
| 14 | Creer `.github/workflows/ci.yml` (test + build + deploy) | 1h |
| 15 | Configurer GitHub Container Registry | 30 min |
| 16 | Tester le pipeline complet (push → test → build → deploy) | 30 min |

### Phase 4 — Les autres repos (quand ils sont prets)

| # | Tache | Effort |
|---|-------|--------|
| 17 | CI/CD mission-chatwoot (leger) | 30 min |
| 18 | CI/CD mission-odoo (connecter a Odoo.sh) | 30 min |
| 19 | CI/CD mission-site (quand le site est pret) | 1h |
| 20 | CI/CD mission-docs (validation markdown) | 15 min |

**Effort total CI/CD : ~10-12h reparties sur les sprints**

---

## RESUME

| Composant | Outil | Deploy staging | Deploy prod | Release notes |
|-----------|-------|---------------|-------------|---------------|
| openedx-platform | GitHub Actions | Auto (push staging) | Auto (push main) | Auto (conventional commits) |
| mission-qualiopi | GitHub Actions + GHCR | Auto (Docker pull) | Auto (Docker pull) | Auto |
| mission-odoo | Odoo.sh natif | Auto (push staging) | Auto (push main) | Auto |
| mission-chatwoot | GitHub Actions | Auto (SSH) | Auto (SSH) | Auto |
| mission-site | GitHub Actions | Auto | Auto | Auto |
| mission-docs | GitHub Actions | N/A | N/A | Auto (changelog) |
