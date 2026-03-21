# PROCESS COMPLET — MISSION FORMATIONS OPENEDX
## Guide opérationnel — Solo-fondatrice, version 1.0, mars 2026

---

## TABLE DES MATIÈRES

1. [Architecture & environnements](#1-architecture--environnements)
2. [Règles Git — branchement et commits](#2-règles-git--branchement-et-commits)
3. [Règles Codex — garde-fous obligatoires](#3-règles-codex--garde-fous-obligatoires)
4. [Workflow développement local](#4-workflow-développement-local)
5. [Workflow déploiement staging](#5-workflow-déploiement-staging)
6. [Workflow déploiement production](#6-workflow-déploiement-production)
7. [Fichiers protégés — jamais toucher sans validation](#7-fichiers-protégés--jamais-toucher-sans-validation)
8. [Script de déploiement deploy.sh](#8-script-de-déploiement-deploysh)
9. [Checklist avant chaque déploiement](#9-checklist-avant-chaque-déploiement)
10. [Procédures de rollback](#10-procédures-de-rollback)
11. [Diagnostic rapide — problèmes courants](#11-diagnostic-rapide--problèmes-courants)

---

## 1. ARCHITECTURE & ENVIRONNEMENTS

### Trois environnements, trois règles

| Environnement | URL | Branche Git | Rebuild image requis |
|---|---|---|---|
| **Local** | http://local.openedx.io | `staging` | Non (bind mount) |
| **Staging** | https://academie.staging.missionformations.com | `staging` | Oui |
| **Production** | https://academie.missionformations.com | `main` | Oui |

### Infrastructure

- **Serveur staging** : Hetzner, SSH alias `staging-openedx`
- **TUTOR_ROOT** : `/root/.local/share/tutor`
- **Repo edx-platform** : `github.com/zakiaC/edx-platform`
- **Thème actif** : `mission-theme` (monté via bind mount)
- **Stack** : Tutor 21.0.1-indigo, Python 3.11, Django 5.2, uv pip, Node 18

### Bind mounts Docker (staging)

```
/root/edx-platform/themes/mission-theme → /openedx/themes/mission-theme
/root/edx-platform/lms/djangoapps/mission_central_admin → /openedx/edx-platform/lms/djangoapps/mission_central_admin
```

---

## 2. RÈGLES GIT — BRANCHEMENT ET COMMITS

### Structure des branches

```
main          ← production uniquement, jamais de commit direct
staging       ← développement et tests
feature/xxx   ← fonctionnalités isolées (merge vers staging après tests)
hotfix/xxx    ← corrections urgentes production
```

### Règle des commits

**Format obligatoire :**
```
type: description courte en français

Types autorisés:
fix:      correction de bug
feat:     nouvelle fonctionnalité
build:    assets compilés, requirements
ops:      scripts, config déploiement
docs:     documentation
refactor: refactoring sans changement fonctionnel
```

**Exemples corrects :**
```
fix: fallback UserCreationForm pour compatibilité Django 4.x/5.x
feat: ajout tableau de bord formateur
build: CSS compilés mission-theme lms-main-v1
ops: add deploy.sh pour déploiements reproductibles
```

### Avant chaque push — vérification obligatoire

```bash
git diff --stat HEAD          # voir tous les fichiers modifiés
git diff HEAD                 # voir les changements ligne par ligne
```

**Si plus de 5 fichiers modifiés** → relire chaque diff individuellement avant de pousser.

---

## 3. RÈGLES CODEX — GARDE-FOUS OBLIGATOIRES

### Prompt à coller en début de chaque session Codex

```
CONTEXTE: Fork OpenEdX custom (Tutor Indigo 21.0.1, Python 3.11, Django 5.2, uv pip).
Projet extrêmement sensible. Une modification incorrecte casse le déploiement entier.

FICHIERS INTERDITS — STOP si ta tâche touche l'un de ces fichiers:
- requirements/edx/*.txt
- lms/envs/*.py / cms/envs/*.py
- openedx/core/storage.py
- */apps.py / */forms.py
- Dockerfile* / docker-compose*
- package.json / package-lock.json

RÈGLES:
1. Un seul fichier par demande sauf instruction explicite contraire
2. Afficher le diff complet avant tout commit
3. Imports Django: toujours utiliser try/except pour compatibilité
4. Requirements: vérifier existence PyPI + compatibilité uv avant ajout
5. Settings Django: toujours FEATURES.get('CLE', '') jamais FEATURES['CLE']
6. Déploiement: toujours ./deploy.sh [local|staging] jamais de commandes manuelles

FORMAT DE RÉPONSE OBLIGATOIRE:
FICHIER(S): [liste]
FICHIERS INTERDITS TOUCHÉS: [oui → STOP / non → continuer]
DIFF: [diff complet]
RISQUE: [aucun/faible/moyen/élevé]
ROLLBACK: [commande exacte]

MA DEMANDE: [COLLE TA DEMANDE ICI]
```

### Périmètre autorisé pour Codex

```
✅ themes/mission-theme/lms/templates/
✅ themes/mission-theme/lms/static/sass/
✅ themes/mission-theme/lms/static/js/
✅ lms/djangoapps/mission_central_admin/   (sauf apps.py et forms.py)
✅ lms/djangoapps/mission_*/              (sauf apps.py et forms.py)
✅ deploy.sh

❌ Tout le reste → validation manuelle obligatoire
```

---

## 4. WORKFLOW DÉVELOPPEMENT LOCAL

### Démarrage environnement local

```bash
# 1. S'assurer que Docker Desktop est lancé
docker info > /dev/null 2>&1 || open -a Docker && sleep 10

# 2. Démarrer Tutor local
cd /Users/zakiachabane/edx-platform
docker compose -p tutor_local up -d

# 3. Vérifier que tout est up
docker compose -p tutor_local ps
```

### Cycle de développement local

```bash
# Modifier des templates ou SCSS dans themes/mission-theme/
# Puis compiler et collecter:

./deploy.sh local
```

### Premier démarrage ou après git pull majeur

```bash
# 1. Webpack (uniquement si webpack-stats.json absent ou corrompu)
docker compose -p tutor_local exec lms bash -c \
  'cd /openedx/edx-platform && NODE_OPTIONS="--max-old-space-size=4096" npm run webpack > /tmp/webpack.log 2>&1 &'

# Suivre la progression (attendre "compiled successfully")
docker compose -p tutor_local exec lms bash -c 'tail -f /tmp/webpack.log'

# 2. Déployer assets
./deploy.sh local
```

### Vérification locale

```bash
# HTTP check
curl -sk -o /dev/null -w "%{http_code}" http://local.openedx.io

# Classes mf- présentes
curl -sk http://local.openedx.io | grep -c "mf-"
```

---

## 5. WORKFLOW DÉPLOIEMENT STAGING

### Pré-requis avant tout déploiement staging

```bash
# Sur Mac — vérifier l'état du repo
git status
git diff --stat HEAD

# Aucun fichier non commité autorisé
# Si des fichiers sont en attente → commiter ou stash avant de continuer
```

### Déploiement standard (changements templates/SCSS/JS uniquement)

```bash
# 1. Commiter et pousser
git add themes/mission-theme/
git commit -m "feat: description du changement"
git push origin staging

# 2. Sur staging — pull et déployer
ssh staging-openedx "cd /root/edx-platform && git pull origin staging"
ssh staging-openedx "cd /root/edx-platform && ./deploy.sh staging"
```

### Déploiement avec rebuild d'image (changements Python/requirements)

```bash
# 1. Commiter et pousser
git push origin staging

# 2. Sur staging — rebuild complet
ssh staging-openedx "cd /root/edx-platform && git pull origin staging"

ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor images build openedx \
  --build-arg EDX_PLATFORM_REPOSITORY=https://github.com/zakiaC/edx-platform.git \
  --build-arg EDX_PLATFORM_VERSION=staging \
  2>&1 | tee /root/build.log"

# 3. Redémarrer et déployer assets
ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor local stop && \
  TUTOR_ROOT=/root/.local/share/tutor tutor local start -d && \
  sleep 30"

ssh staging-openedx "cd /root/edx-platform && ./deploy.sh staging"

# 4. Vérifier
ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor local logs lms --tail=10"
```

### Quand le rebuild est obligatoire

| Type de changement | Rebuild requis |
|---|---|
| Templates HTML | ❌ Non |
| SCSS / CSS | ❌ Non |
| JavaScript custom | ❌ Non |
| `requirements/edx/*.txt` | ✅ Oui |
| `lms/envs/*.py` | ✅ Oui |
| `openedx/core/*.py` | ✅ Oui |
| `*/apps.py` | ✅ Oui |

---

## 6. WORKFLOW DÉPLOIEMENT PRODUCTION

### Règle absolue

**Jamais de déploiement production sans avoir testé staging pendant au moins 24h.**

### Procédure

```bash
# 1. Merger staging → main après validation staging
git checkout main
git merge staging --no-ff -m "release: déploiement production [date]"
git push origin main

# 2. Sur serveur production
ssh production-openedx "cd /root/edx-platform && git pull origin main"

# 3. Si rebuild requis
ssh production-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor images build openedx \
  --build-arg EDX_PLATFORM_REPOSITORY=https://github.com/zakiaC/edx-platform.git \
  --build-arg EDX_PLATFORM_VERSION=main \
  2>&1 | tee /root/build.log"

# 4. Déployer
ssh production-openedx "cd /root/edx-platform && ./deploy.sh production"

# 5. Smoke test
curl -sk -o /dev/null -w "%{http_code}" https://academie.missionformations.com
```

---

## 7. FICHIERS PROTÉGÉS — JAMAIS TOUCHER SANS VALIDATION

### Niveau 1 — CRITIQUE (casse le déploiement immédiatement)

```
requirements/edx/base.txt          → compatibilité uv pip stricte
requirements/edx/assets.txt        → dépendances assets
lms/envs/production.py             → settings Django production
cms/envs/production.py
openedx/core/storage.py            → pipeline staticfiles
```

### Niveau 2 — SENSIBLE (régression silencieuse possible)

```
lms/djangoapps/*/apps.py           → AppConfig, import au démarrage
lms/djangoapps/*/forms.py          → imports version-dépendants Django
lms/startup.py / cms/startup.py    → initialisation Django
*/migrations/*.py                  → base de données
```

### Niveau 3 — ATTENTION (impact visuel global)

```
themes/mission-theme/lms/static/sass/lms-main-v1.scss   → CSS principal LMS
themes/mission-theme/lms/templates/index.html            → homepage
themes/mission-theme/lms/templates/header/header.html   → navigation
themes/mission-theme/lms/templates/footer.html           → pied de page
```

---

## 8. SCRIPT DE DÉPLOIEMENT deploy.sh

Placer à la racine du repo : `/Users/zakiachabane/edx-platform/deploy.sh`

```bash
#!/bin/bash
# deploy.sh — Mission Formations OpenEdX
# Usage: ./deploy.sh [local|staging|production]
# Ce script est la SEULE façon autorisée de déployer les assets.

set -e
ENV=${1:-local}

echo ""
echo "======================================"
echo " DÉPLOIEMENT MISSION FORMATIONS"
echo " Environnement : $ENV"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================"

# Configuration par environnement
if [ "$ENV" = "local" ]; then
  CONTAINER="tutor_local-lms-1"
  THEME_PATH="/Users/zakiachabane/edx-platform/themes/mission-theme"
  RUN_CMD="docker exec $CONTAINER"
  MANAGE="docker exec $CONTAINER ./manage.py lms"
  GREP_CMD="grep"
elif [ "$ENV" = "staging" ]; then
  CONTAINER="tutor_local-lms-1"
  THEME_PATH="/root/edx-platform/themes/mission-theme"
  RUN_CMD="ssh staging-openedx docker exec $CONTAINER"
  MANAGE="ssh staging-openedx docker exec $CONTAINER ./manage.py lms"
  GREP_CMD="ssh staging-openedx grep"
  GIT_CMD="ssh staging-openedx bash -c 'cd /root/edx-platform &&"
else
  echo "ERREUR: environnement inconnu. Utilisez local, staging ou production."
  exit 1
fi

# Étape 1 — Permissions thème
echo ""
echo "--- Étape 1/4 : Permissions thème ---"
if [ "$ENV" != "local" ]; then
  ssh staging-openedx "chown -R 1000:1000 $THEME_PATH && chmod -R 775 $THEME_PATH"
fi
echo "OK"

# Étape 2 — Compilation Sass
echo ""
echo "--- Étape 2/4 : Compilation Sass ---"
$RUN_CMD bash -c 'npm run compile-sass -- --skip-default 2>&1 | tail -5'

# Vérification CSS compilé
MF_COUNT=$($GREP_CMD -c 'mf-' "$THEME_PATH/lms/static/css/lms-main-v1.css" 2>/dev/null || echo "0")
if [ "$MF_COUNT" = "0" ]; then
  echo "ERREUR: CSS non compilé (0 occurrences mf-). Arrêt."
  exit 1
fi
echo "CSS validé : $MF_COUNT occurrences mf- trouvées"

# Étape 3 — Collectstatic
echo ""
echo "--- Étape 3/4 : Collectstatic ---"
$MANAGE collectstatic --noinput 2>&1 | tail -3

# Étape 4 — Commit CSS compilés
echo ""
echo "--- Étape 4/4 : Commit CSS compilés ---"
if [ "$ENV" = "local" ]; then
  cd /Users/zakiachabane/edx-platform
  git add themes/mission-theme/lms/static/css/
  git diff --cached --stat
  git commit -m "build: update compiled CSS mission-theme $(date '+%Y-%m-%d')" || echo "Rien à commiter"
elif [ "$ENV" = "staging" ]; then
  ssh staging-openedx "cd /root/edx-platform && \
    git add themes/mission-theme/lms/static/css/ && \
    git diff --cached --stat && \
    git commit -m 'build: update compiled CSS mission-theme $(date +%Y-%m-%d)' || echo 'Rien à commiter'"
fi

echo ""
echo "======================================"
echo " DÉPLOIEMENT TERMINÉ ✅"
echo " Testez : https://academie.$ENV.missionformations.com"
echo "======================================"
```

```bash
chmod +x /Users/zakiachabane/edx-platform/deploy.sh
git add deploy.sh
git commit -m "ops: add deploy.sh script"
git push origin staging
```

---

## 9. CHECKLIST AVANT CHAQUE DÉPLOIEMENT

### Checklist locale (30 secondes)

- [ ] `docker compose -p tutor_local ps` → tous les services Up
- [ ] `git status` → aucun fichier non commité
- [ ] `./deploy.sh local` → pas d'erreur
- [ ] `http://local.openedx.io` → 200 en navigation privée

### Checklist staging (2 minutes)

- [ ] Testé en local sans erreur
- [ ] Tous les fichiers commités et poussés
- [ ] `ssh staging-openedx "TUTOR_ROOT=... tutor local status"` → tous Up
- [ ] `./deploy.sh staging` → pas d'erreur
- [ ] `https://academie.staging.missionformations.com` → 200, design correct
- [ ] Login/logout fonctionnel
- [ ] Catalogue visible

### Checklist production (5 minutes)

- [ ] Staging stable depuis 24h minimum
- [ ] Heure de déploiement : hors des heures de pointe (avant 8h ou après 20h)
- [ ] Backup base de données effectué
- [ ] Tag Git créé : `git tag v$(date +%Y%m%d)`
- [ ] Smoke test post-déploiement effectué

---

## 10. PROCÉDURES DE ROLLBACK

### Rollback rapide — image Docker précédente

```bash
# Identifier les images disponibles
ssh staging-openedx "docker images | grep openedx"

# Retagger l'image précédente
ssh staging-openedx "docker tag overhangio/openedx:[TAG_PRÉCÉDENT] \
  overhangio/openedx:21.0.1-indigo"

# Redémarrer
ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor local stop && \
  TUTOR_ROOT=/root/.local/share/tutor tutor local start -d"
```

### Rollback Git — revenir au commit précédent

```bash
# Voir les derniers commits
git log --oneline -10

# Revenir au commit précédent (sans supprimer l'historique)
git revert HEAD
git push origin staging

# Sur staging
ssh staging-openedx "cd /root/edx-platform && git pull origin staging"
```

### Rollback permissions thème

```bash
ssh staging-openedx "chmod -R 755 /root/edx-platform/themes/mission-theme"
```

### Rollback settings Tutor (production.py)

```bash
# Supprimer la ligne ajoutée manuellement
ssh staging-openedx "sed -i \"/PIPELINE\['JS_COMPRESSOR'\] = None/d\" \
  /root/.local/share/tutor/env/apps/openedx/settings/lms/production.py"
```

---

## 11. DIAGNOSTIC RAPIDE — PROBLÈMES COURANTS

### 502 Bad Gateway

```bash
ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor local status"
ssh staging-openedx "TUTOR_ROOT=/root/.local/share/tutor tutor local logs lms --tail=20"
```
→ LMS en boucle = erreur Python au démarrage. Lire les logs pour trouver l'exception.

### 500 Internal Server Error en local

```bash
docker compose -p tutor_local logs lms --tail=20
```
→ `webpack-stats.json` manquant = relancer `npm run webpack` avec `NODE_OPTIONS=--max-old-space-size=4096`

### Design non appliqué (CSS sans styles)

```bash
# Vérifier que les règles mf- sont dans le CSS collecté
grep -c "mf-" /openedx/staticfiles/mission-theme/css/lms-main-v1.css
```
→ Si 0 : relancer `./deploy.sh [env]`

### collectstatic échoue avec SuspiciousFileOperation

→ Thème orphelin dans l'image. Vérifier `/openedx/themes/` et supprimer les thèmes non actifs du Dockerfile.

### collectstatic échoue avec UglifyJS

```bash
# Vérifier settings production
grep "JS_COMPRESSOR" /root/.local/share/tutor/env/apps/openedx/settings/lms/production.py
```
→ Si absent : `echo "\nPIPELINE['JS_COMPRESSOR'] = None" >> [fichier]`

### Rebuild échoue sur requirements

```bash
# Vérifier la compatibilité uv des packages
# Interdit: -e git+https://...
# Obligatoire: package==version ou package @ git+https://...
grep "^-e" requirements/edx/base.txt
```

### KeyError au démarrage LMS

→ Un settings accède à `FEATURES['CLE']` sans `.get()`. Chercher dans `production.py` et remplacer par `FEATURES.get('CLE', '')`.

---

## ANNEXE — CONTACTS ET RESSOURCES

- **Documentation Tutor** : https://docs.tutor.edly.io
- **Forum OpenEdX** : https://discuss.openedx.org
- **Repo custom** : https://github.com/zakiaC/edx-platform
- **Staging** : ssh staging-openedx
- **TUTOR_ROOT** : /root/.local/share/tutor

---

*Document créé le 10 mars 2026 — à mettre à jour après chaque incident résolu.*
