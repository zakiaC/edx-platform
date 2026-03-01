# Open edX — RCA & Runbook : CSS Thème LMS non appliqué en staging

**Projet** : Mission Formations – academie.staging.missionformations.com  
**Date** : 2026-03-01  
**Auteur** : Staff Engineer / Principal DevOps  
**Commit de référence** : `3fa3db6bad` (branch `develop` + staging)  
**Statut** : 🔴 Incident ouvert — rendu visuel homepage incorrect

---

## Section 1 — Diagnostic prouvé (Root Cause Analysis)

### 1.1 Symptômes observés

| Signal | Statut | Preuve |
|--------|--------|--------|
| HTML homepage (markers `formateurNabil · Serie1-VTC2`, `Deuxième test formation`) | ✅ Présent | `curl -s https://academie.staging.missionformations.com \| grep -c "formateurNabil"` → 1+ |
| Lien legacy `mf-homepage.css` dans le HTML | ✅ Absent (migration OK) | `curl -s ... \| grep -c "mf-homepage.css"` → 0 |
| TLS | ✅ OK | `curl -sI ... \| grep HTTP` → 200 |
| Rendu visuel classes `.mf-nav`, `.mf-hero`, etc. | 🔴 Absent | Inspection du bundle CSS servi |
| Thème mission-theme actif | ✅ | Header `x-mission-theme-lock: enabled` |

### 1.2 Cause racine (Root Cause)

**Le bundle CSS compilé et servi par le LMS ne contient pas les classes homepage (`.mf-nav`, `.mf-hero`, `.mf-section-*`, etc.) parce que le fichier `_extras.scss` du thème n'est pas inclus dans la chaîne de compilation Sass, OU les assets n'ont pas été recompilés/collectés après le commit `3fa3db6bad`.**

L'arbre de causalité complet :

```
SYMPTÔME : Styles homepage absents visuellement
│
├─► CAUSE DIRECTE : Le bundle CSS servi (lms-main-v*.css) ne contient pas
│   les règles .mf-nav, .mf-hero, etc.
│
├─► CAUSE RACINE A (la plus probable) :
│   Le fichier _extras.scss n'est PAS @import-é dans la chaîne Sass du thème.
│   Open edX comprehensive theming inclut _extras.scss UNIQUEMENT si le chemin
│   est exactement :
│     themes/<THEME>/lms/static/sass/partials/lms/theme/_extras.scss
│   ET que le fichier lms/static/sass/_lms-theme-extras.scss (ou équivalent)
│   du thème fait bien le @import, OU que le pipeline piper/webpack le résout.
│
├─► CAUSE RACINE B (contributive) :
│   Après le push du commit 3fa3db6bad, la commande `openedx-assets build`
│   n'a PAS été ré-exécutée dans le conteneur LMS Tutor.
│   → Le bundle CSS sur disque est toujours l'ancien (pré-migration).
│
├─► CAUSE RACINE C (contributive) :
│   Même si le build a tourné, `collectstatic` n'a pas été relancé.
│   → Les fichiers statiques servis par Caddy/whitenoise sont stale.
│
└─► CAUSE CONTRIBUTIVE D :
    Cache navigateur / CDN intermédiaire servant un bundle périmé
    (moins probable si curl confirme aussi l'absence).
```

### 1.3 Commandes de vérification diagnostique

Exécuter **dans l'ordre** pour identifier laquelle des causes s'applique :

```bash
# ── ÉTAPE D1 : Vérifier que _extras.scss existe au bon chemin dans le conteneur ──
docker compose -p tutor_local exec lms \
  ls -la /openedx/themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss

# Résultat attendu : fichier présent, non vide.
# Si ABSENT → Cause A confirmée (mount thème incomplet ou chemin erroné).

# ── ÉTAPE D2 : Vérifier que _extras.scss est importé dans la chaîne Sass ──
docker compose -p tutor_local exec lms \
  grep -r "_extras" /openedx/themes/mission-theme/lms/static/sass/ --include="*.scss"

# Résultat attendu : au moins un fichier fait @import "...extras" ou @use "...extras"
# Si AUCUN résultat → Cause A confirmée : le partial existe mais personne ne l'importe.

# ── ÉTAPE D3 : Vérifier la date du dernier build CSS ──
docker compose -p tutor_local exec lms \
  stat /openedx/staticfiles/css/lms-main-v2*.css 2>/dev/null || \
  stat /openedx/staticfiles/css/lms-main-v1*.css 2>/dev/null || \
  echo "AUCUN bundle LMS CSS trouvé dans staticfiles"

# Comparer le timestamp avec la date du commit 3fa3db6bad.
# Si le bundle est PLUS VIEUX que le commit → Cause B confirmée.

# ── ÉTAPE D4 : Vérifier que le bundle compilé contient les classes homepage ──
docker compose -p tutor_local exec lms bash -c \
  'grep -l "mf-nav\|mf-hero" /openedx/staticfiles/css/lms-main-v*.css'

# Si AUCUN résultat → le build n'a pas inclus _extras.scss (Cause A ou B).

# ── ÉTAPE D5 : Vérifier ce que le client reçoit réellement ──
# Identifier l'URL du bundle CSS depuis le HTML :
BUNDLE_URL=$(curl -s https://academie.staging.missionformations.com | \
  grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | tr -d 'href="')
echo "Bundle CSS URL: $BUNDLE_URL"

# Puis vérifier son contenu :
curl -s "https://academie.staging.missionformations.com${BUNDLE_URL}" | \
  grep -c "mf-nav"

# Si 0 → confirme que le bundle servi au client est stale/incomplet.

# ── ÉTAPE D6 : Vérifier le hash collectstatic vs fichier sur disque ──
docker compose -p tutor_local exec lms bash -c \
  'python -c "
import json, pathlib
sf = pathlib.Path(\"/openedx/staticfiles/staticfiles.json\")
if sf.exists():
    data = json.loads(sf.read_text())
    css_keys = [k for k in data if \"lms-main\" in k and k.endswith(\".css\")]
    for k in css_keys:
        print(f\"{k} -> {data[k]}\")
else:
    print(\"staticfiles.json NOT FOUND — collectstatic jamais exécuté ou whitenoise non configuré\")
"'
```

### 1.4 Résumé RCA

| # | Cause | Probabilité | Vérification |
|---|-------|-------------|--------------|
| A | `_extras.scss` non importé dans la chaîne Sass | **Très haute** | D1 + D2 |
| B | `openedx-assets build` non exécuté post-commit | **Haute** | D3 |
| C | `collectstatic` non exécuté post-build | **Moyenne** | D4 + D6 |
| D | Cache navigateur/CDN | **Faible** | D5 avec `Cache-Control: no-cache` |

---

## Section 2 — Fix permanent (Architecture)

### 2.1 Principe architectural

```
┌─────────────────────────────────────────────────────────────┐
│                    CHAÎNE DE BUILD THÈME                     │
│                                                              │
│  1. Code thème (git)                                         │
│     themes/mission-theme/lms/static/sass/                    │
│       ├── _lms-variables.scss      (overrides couleurs)      │
│       ├── _lms-extends.scss        (overrides composants)    │
│       ├── lms-main-v2.scss         (entry point — CRITIQUE)  │
│       └── partials/lms/theme/                                │
│             └── _extras.scss       (styles custom homepage)  │
│                                                              │
│  2. Mount dans conteneur Tutor                               │
│     /openedx/themes/mission-theme/ ← volume Docker           │
│                                                              │
│  3. Build assets (Sass → CSS)                                │
│     tutor local run lms openedx-assets build                 │
│     → produit /openedx/staticfiles/css/lms-main-v2.css      │
│                                                              │
│  4. Collectstatic (hash + copie)                             │
│     tutor local run lms openedx-assets collect               │
│     → produit lms-main-v2.<hash>.css + staticfiles.json      │
│                                                              │
│  5. Restart LMS (charge les nouveaux manifests)              │
│     tutor local restart lms                                  │
│                                                              │
│  6. Caddy sert les fichiers statiques mis à jour             │
│     (cache-bust via le hash dans l'URL)                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Règles permanentes

1. **Tout style custom DOIT être dans le pipeline Sass du thème** — jamais de `<link>` page-level vers un CSS isolé.
2. **Le fichier entry-point Sass du thème DOIT importer explicitement `_extras.scss`** — ne jamais supposer qu'Open edX le fait automatiquement.
3. **Chaque commit touchant `sass/` DOIT déclencher : build → collect → restart** — idempotent, scriptable.
4. **Le smoke test DOIT vérifier le contenu du bundle CSS** — pas seulement le HTML.

---

## Section 3 — Diff / Patch concret

### 3.1 PATCH 1 — Assurer l'import de `_extras.scss` dans l'entry-point Sass

C'est **le fix critique**. Il faut que le fichier entry-point Sass du thème importe `_extras.scss`.

**Fichier à modifier** :  
`themes/mission-theme/lms/static/sass/lms-main-v2.scss`

> Si ce fichier n'existe pas encore dans votre thème, il faut le créer. Il override l'entry-point d'Open edX.

```scss
// themes/mission-theme/lms/static/sass/lms-main-v2.scss
//
// Entry-point Sass du thème mission-theme pour le LMS.
// Ce fichier override le lms-main-v2.scss par défaut d'Open edX
// grâce au mécanisme comprehensive theming.

// 1. Importer TOUT le pipeline LMS par défaut d'Open edX
@import 'lms/static/sass/lms-main-v2';

// 2. Importer les extras du thème (homepage, composants custom, etc.)
//    C'est ICI que _extras.scss entre dans le bundle compilé.
@import 'partials/lms/theme/extras';
```

> **Note critique** : dans la syntaxe Sass `@import`, on omet le `_` préfixe et l'extension `.scss`. Donc `@import 'partials/lms/theme/extras'` résout vers `partials/lms/theme/_extras.scss`.

**Alternative si votre version Open edX utilise `lms-main-v1`** :  
Vérifiez quel entry-point est utilisé :

```bash
docker compose -p tutor_local exec lms bash -c \
  'grep -r "lms-main" /openedx/edx-platform/lms/templates/main.html | head -5'
```

Et créez/modifiez le fichier correspondant (`lms-main-v1.scss` au lieu de `v2`).

### 3.2 PATCH 2 — Vérifier le contenu de `_extras.scss`

**Fichier** : `themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss`

Ce fichier doit contenir vos classes homepage. Vérifiez qu'il est non vide et bien formé :

```bash
# Vérification locale
wc -l themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss
# Doit être > 0

# Vérifier qu'il compile sans erreur isolément
npx sass --no-source-map --style=compressed \
  themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss \
  /dev/null 2>&1
# Doit retourner 0 erreurs (Note: les @import manquants sont OK à ce stade)
```

### 3.3 PATCH 3 — Vérifier la config thème dans Tutor

**Fichier** : `$(tutor config printroot)/config.yml`

```yaml
# Vérifier ces clés :
COMPREHENSIVE_THEME_DIRS:
  - /openedx/themes
DEFAULT_SITE_THEME: "mission-theme"
ENABLE_COMPREHENSIVE_THEMING: true
```

Si absent, configurer via :

```bash
tutor config save \
  --set 'COMPREHENSIVE_THEME_DIRS=["/openedx/themes"]' \
  --set 'DEFAULT_SITE_THEME=mission-theme' \
  --set 'ENABLE_COMPREHENSIVE_THEMING=true'
```

### 3.4 PATCH 4 — S'assurer que le thème est monté dans le conteneur

Vérifier dans `$(tutor config printroot)/env/local/docker-compose.override.yml` ou équivalent :

```yaml
# Le répertoire thème local doit être bindé dans le conteneur
services:
  lms:
    volumes:
      - /chemin/vers/themes/mission-theme:/openedx/themes/mission-theme:ro
  cms:
    volumes:
      - /chemin/vers/themes/mission-theme:/openedx/themes/mission-theme:ro
```

> Avec Tutor, la méthode recommandée est d'utiliser un **plugin Tutor** pour le mount. Voir section 7.

### 3.5 Arbre final attendu dans le conteneur

```
/openedx/themes/mission-theme/
└── lms/
    ├── static/
    │   └── sass/
    │       ├── lms-main-v2.scss              ← ENTRY POINT (Patch 1)
    │       └── partials/
    │           └── lms/
    │               └── theme/
    │                   └── _extras.scss       ← STYLES HOMEPAGE
    └── templates/
        └── (vos templates overridés)
```

---

## Section 4 — Runbook de déploiement staging

### 4.1 Pré-requis

```bash
# Vérifier accès SSH au serveur staging
ssh staging-server "docker compose -p tutor_local ps" | grep -E "lms|cms|caddy"
# Les 3 services doivent être UP.
```

### 4.2 Procédure de déploiement (idempotente)

```bash
#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# RUNBOOK : Déploiement thème mission-theme sur staging
# Idempotent — peut être relancé à tout moment sans effet de bord
# ============================================================

TUTOR_PROJECT="tutor_local"
THEME_NAME="mission-theme"
DC="docker compose -p ${TUTOR_PROJECT}"
LMS_DOMAIN="academie.staging.missionformations.com"

echo "=========================================="
echo " STEP 1/6 — Pull du code thème"
echo "=========================================="
# (Adapter selon votre méthode de déploiement du thème sur le serveur)
cd /chemin/vers/repo && git pull origin develop
echo "✅ Code à jour"

echo "=========================================="
echo " STEP 2/6 — Vérification mount thème"
echo "=========================================="
${DC} exec lms ls /openedx/themes/${THEME_NAME}/lms/static/sass/lms-main-v2.scss
${DC} exec lms ls /openedx/themes/${THEME_NAME}/lms/static/sass/partials/lms/theme/_extras.scss
echo "✅ Fichiers thème présents dans le conteneur"

echo "=========================================="
echo " STEP 3/6 — Build assets (Sass → CSS)"
echo "=========================================="
${DC} exec lms openedx-assets build --themes ${THEME_NAME}
echo "✅ Assets compilés"

echo "=========================================="
echo " STEP 4/6 — Collectstatic"
echo "=========================================="
${DC} exec lms openedx-assets collect --settings=tutor.assets
# Alternative si la commande ci-dessus échoue :
# ${DC} exec lms python manage.py lms collectstatic --noinput --settings=tutor.assets
echo "✅ Fichiers statiques collectés"

echo "=========================================="
echo " STEP 5/6 — Restart LMS + CMS"
echo "=========================================="
${DC} restart lms cms
echo "⏳ Attente démarrage (30s)..."
sleep 30
echo "✅ Services redémarrés"

echo "=========================================="
echo " STEP 6/6 — Vérification rapide"
echo "=========================================="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${LMS_DOMAIN}/")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ LMS accessible (HTTP ${HTTP_CODE})"
else
    echo "🔴 LMS inaccessible (HTTP ${HTTP_CODE})"
    exit 1
fi

# Vérifier que le bundle CSS contient les classes
BUNDLE_PATH=$(curl -s "https://${LMS_DOMAIN}/" | \
  grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | \
  sed 's/href="//;s/"//')

if [ -z "$BUNDLE_PATH" ]; then
    echo "🔴 Bundle CSS non trouvé dans le HTML"
    exit 1
fi

MF_COUNT=$(curl -s "https://${LMS_DOMAIN}${BUNDLE_PATH}" | grep -c "mf-nav" || true)
if [ "$MF_COUNT" -gt 0 ]; then
    echo "✅ Classes .mf-nav trouvées dans le bundle CSS (${MF_COUNT} occurrences)"
else
    echo "🔴 Classes .mf-nav ABSENTES du bundle CSS — le build n'a pas inclus _extras.scss"
    exit 1
fi

echo ""
echo "=========================================="
echo " ✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS"
echo "=========================================="
```

### 4.3 Notes importantes

- **Idempotence** : chaque step peut être relancé indépendamment. Le build Sass recompile tout, collectstatic re-hashe, restart recharge.
- **Pas de side-effects** : aucun `cp`, aucun `docker exec ... bash`, aucune modification manuelle.
- Si `openedx-assets build --themes` n'est pas supporté sur votre version, utilisez `openedx-assets build` (sans filtre — plus long mais sûr).

---

## Section 5 — Smoke test automatique (script shell)

```bash
#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# SMOKE TEST — Post-déploiement thème mission-theme
# Exit code : 0 = PASS, 1 = FAIL
# Usage : ./smoke-test.sh [LMS_DOMAIN] [CMS_DOMAIN]
# ============================================================

LMS_DOMAIN="${1:-academie.staging.missionformations.com}"
CMS_DOMAIN="${2:-studio.staging.missionformations.com}"
LMS_URL="https://${LMS_DOMAIN}"
CMS_URL="https://${CMS_DOMAIN}"

PASS=0
FAIL=0
TOTAL=0

check() {
    local name="$1"
    local result="$2"  # 0 = pass, non-0 = fail
    local detail="${3:-}"
    TOTAL=$((TOTAL + 1))
    if [ "$result" -eq 0 ]; then
        PASS=$((PASS + 1))
        echo "  ✅ PASS — ${name}"
    else
        FAIL=$((FAIL + 1))
        echo "  🔴 FAIL — ${name}"
        [ -n "$detail" ] && echo "           ${detail}"
    fi
}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║        SMOKE TEST — Mission Formations Thème          ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║ LMS : ${LMS_URL}"
echo "║ CMS : ${CMS_URL}"
echo "║ Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Disponibilité endpoints ──────────────────────────────
echo "▸ 1. Disponibilité endpoints"

LMS_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/" || echo "000")
check "LMS homepage (HTTP 200)" "$([ "$LMS_HTTP" = "200" ] && echo 0 || echo 1)" "Got HTTP ${LMS_HTTP}"

LMS_LOGIN_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/login" || echo "000")
check "LMS /login (HTTP 200)" "$([ "$LMS_LOGIN_HTTP" = "200" ] && echo 0 || echo 1)" "Got HTTP ${LMS_LOGIN_HTTP}"

LMS_API_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/api/user/v1/me" || echo "000")
check "LMS API /api/user/v1/me (HTTP 401 ou 403)" \
  "$(echo "$LMS_API_HTTP" | grep -qE "^(401|403)$" && echo 0 || echo 1)" \
  "Got HTTP ${LMS_API_HTTP}"

CMS_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${CMS_URL}/" || echo "000")
check "CMS Studio accessible (HTTP 200 ou 302)" \
  "$(echo "$CMS_HTTP" | grep -qE "^(200|302)$" && echo 0 || echo 1)" \
  "Got HTTP ${CMS_HTTP}"

echo ""

# ── 2. Présence markers homepage ─────────────────────────────
echo "▸ 2. Présence markers homepage"

HOMEPAGE_HTML=$(curl -s --max-time 15 "${LMS_URL}/")

MARKER1_COUNT=$(echo "$HOMEPAGE_HTML" | grep -c "formateurNabil" || true)
check "Marker 'formateurNabil' présent" "$([ "$MARKER1_COUNT" -gt 0 ] && echo 0 || echo 1)"

MARKER2_COUNT=$(echo "$HOMEPAGE_HTML" | grep -c "Serie1-VTC2" || true)
check "Marker 'Serie1-VTC2' présent" "$([ "$MARKER2_COUNT" -gt 0 ] && echo 0 || echo 1)"

MARKER3_COUNT=$(echo "$HOMEPAGE_HTML" | grep -c "Deuxième test formation" || true)
check "Marker 'Deuxième test formation' présent" "$([ "$MARKER3_COUNT" -gt 0 ] && echo 0 || echo 1)"

echo ""

# ── 3. Absence legacy markers ────────────────────────────────
echo "▸ 3. Absence legacy markers"

LEGACY_CSS_COUNT=$(echo "$HOMEPAGE_HTML" | grep -c "mf-homepage\.css" || true)
check "Pas de lien legacy mf-homepage.css" "$([ "$LEGACY_CSS_COUNT" -eq 0 ] && echo 0 || echo 1)" \
  "Trouvé ${LEGACY_CSS_COUNT} occurrence(s)"

LEGACY_INLINE_COUNT=$(echo "$HOMEPAGE_HTML" | grep -c "<!-- legacy-homepage-style -->" || true)
check "Pas de marker legacy inline style" "$([ "$LEGACY_INLINE_COUNT" -eq 0 ] && echo 0 || echo 1)"

echo ""

# ── 4. Bundle CSS contient les classes homepage ──────────────
echo "▸ 4. Vérification bundle CSS"

# Extraire l'URL du bundle CSS principal
BUNDLE_HREF=$(echo "$HOMEPAGE_HTML" | \
  grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | \
  sed 's/href="//;s/"//')

if [ -z "$BUNDLE_HREF" ]; then
    check "Bundle CSS lms-main trouvé dans HTML" "1" "Aucun lien lms-main*.css détecté"
else
    check "Bundle CSS lms-main trouvé dans HTML" "0"

    # Construire URL absolue si relative
    if [[ "$BUNDLE_HREF" == http* ]]; then
        BUNDLE_FULL_URL="$BUNDLE_HREF"
    else
        BUNDLE_FULL_URL="${LMS_URL}${BUNDLE_HREF}"
    fi

    BUNDLE_CSS=$(curl -s --max-time 30 "$BUNDLE_FULL_URL")
    BUNDLE_SIZE=${#BUNDLE_CSS}
    check "Bundle CSS téléchargeable (taille > 1000)" \
      "$([ "$BUNDLE_SIZE" -gt 1000 ] && echo 0 || echo 1)" \
      "Taille: ${BUNDLE_SIZE} bytes"

    # Vérifier chaque classe critique
    for CLASS in "mf-nav" "mf-hero" "mf-section" "mf-footer" "mf-card"; do
        CLASS_COUNT=$(echo "$BUNDLE_CSS" | grep -c "${CLASS}" || true)
        check "Classe .${CLASS} dans le bundle CSS" \
          "$([ "$CLASS_COUNT" -gt 0 ] && echo 0 || echo 1)" \
          "${CLASS_COUNT} occurrence(s)"
    done
fi

echo ""

# ── 5. TLS ────────────────────────────────────────────────────
echo "▸ 5. TLS"

TLS_EXPIRY=$(echo | openssl s_client -servername "$LMS_DOMAIN" -connect "${LMS_DOMAIN}:443" 2>/dev/null | \
  openssl x509 -noout -enddate 2>/dev/null | sed 's/notAfter=//')

if [ -n "$TLS_EXPIRY" ]; then
    EXPIRY_EPOCH=$(date -d "$TLS_EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$TLS_EXPIRY" +%s 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
    check "Certificat TLS valide (>7 jours)" \
      "$([ "$DAYS_LEFT" -gt 7 ] && echo 0 || echo 1)" \
      "Expire dans ${DAYS_LEFT} jours (${TLS_EXPIRY})"
else
    check "Certificat TLS lisible" "1" "Impossible de lire le certificat"
fi

echo ""

# ── RÉSULTAT FINAL ────────────────────────────────────────────
echo "╔════════════════════════════════════════════════════════╗"
if [ "$FAIL" -eq 0 ]; then
    echo "║  ✅  ALL PASS  (${PASS}/${TOTAL} checks)                    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "║  🔴  FAIL  (${PASS} pass / ${FAIL} fail / ${TOTAL} total)          ║"
    echo "╚════════════════════════════════════════════════════════╝"
    exit 1
fi
```

---

## Section 6 — Plan de rollback

### 6.1 Scénario : le fix CSS casse autre chose

```bash
# ── ROLLBACK STEP 1 : Revenir au commit précédent ──
cd /chemin/vers/repo
git log --oneline -5  # identifier le commit pré-fix
git revert HEAD --no-edit  # ou git checkout <commit-avant-fix>
git push origin develop

# ── ROLLBACK STEP 2 : Rebuild assets avec l'ancien code ──
docker compose -p tutor_local exec lms openedx-assets build
docker compose -p tutor_local exec lms openedx-assets collect --settings=tutor.assets

# ── ROLLBACK STEP 3 : Restart ──
docker compose -p tutor_local restart lms cms

# ── ROLLBACK STEP 4 : Vérifier ──
curl -s -o /dev/null -w "%{http_code}" https://academie.staging.missionformations.com/
# Doit retourner 200
```

### 6.2 Scénario : le LMS ne démarre plus après restart

```bash
# Vérifier les logs
docker compose -p tutor_local logs --tail=100 lms | grep -iE "error|exception|traceback"

# Si erreur Sass/compilation :
# Le LMS démarre quand même (les assets sont statiques), mais vérifier :
docker compose -p tutor_local exec lms python -c "import lms.startup; print('LMS importable')"

# Si le conteneur crash-loop :
docker compose -p tutor_local restart lms
sleep 10
docker compose -p tutor_local logs --tail=50 lms
```

### 6.3 Point de rollback permanent

Avant chaque déploiement, sauvegarder le bundle CSS compilé :

```bash
# Avant déploiement
BACKUP_TAG=$(date +%Y%m%d_%H%M%S)
docker compose -p tutor_local exec lms bash -c \
  "cp -r /openedx/staticfiles/css /tmp/css-backup-${BACKUP_TAG}"
echo "Backup CSS: /tmp/css-backup-${BACKUP_TAG}"

# Pour restaurer :
docker compose -p tutor_local exec lms bash -c \
  "cp -r /tmp/css-backup-${BACKUP_TAG}/* /openedx/staticfiles/css/"
docker compose -p tutor_local restart lms
```

---

## Section 7 — Checklist qualité pour chaque future page thème

### 7.1 Anti-patterns à bannir

| # | Anti-pattern | Pourquoi c'est dangereux | Bonne pratique |
|---|-------------|--------------------------|----------------|
| 1 | `<link href="mon-style.css">` dans un template | Contourne le pipeline Sass, pas de hash, pas de cache-bust, fragile | Tout dans `_extras.scss` ou un partial Sass importé |
| 2 | `cp fichier.css` dans le conteneur | Non reproductible, perdu au restart, dette technique pure | Pipeline : git → build → collect → restart |
| 3 | Modifier des fichiers dans `/openedx/staticfiles/` directement | Écrasé par `collectstatic`, non versionné | Modifier dans le thème, rebuild |
| 4 | Oublier `collectstatic` après un build | Le LMS sert les anciens fichiers hashés | Toujours enchaîner build → collect → restart |
| 5 | Créer un partial `_xxx.scss` sans l'importer | Le fichier existe mais n'entre jamais dans le bundle | Ajouter `@import` dans l'entry-point |
| 6 | Utiliser `!important` partout pour "forcer" le style | Guerre de spécificité, maintenance impossible | Utiliser la cascade du thème (le thème est chargé après le core) |
| 7 | Pas de smoke test CSS post-deploy | On découvre le problème quand un utilisateur se plaint | Script automatisé bloquant en CI/CD |
| 8 | Ne pas versionner la config Tutor | Drift entre environnements | `config.yml` dans git, plugin Tutor pour les mounts |

### 7.2 Checklist pré-déploiement (pour chaque PR touchant le thème)

```markdown
## PR Checklist — Thème mission-theme

- [ ] Les nouveaux styles sont dans un partial Sass sous `themes/mission-theme/lms/static/sass/`
- [ ] Le partial est importé (directement ou via chaîne) dans `lms-main-v2.scss`
- [ ] Le Sass compile sans erreur localement : `npx sass lms-main-v2.scss /dev/null`
- [ ] Aucun `<link>` vers un CSS isolé n'a été ajouté dans les templates
- [ ] Aucun `!important` n'a été ajouté (sauf justification documentée)
- [ ] Le smoke test passe après build local
- [ ] Les classes CSS utilisent le namespace `mf-` (convention projet)
- [ ] Les variables de couleur utilisent les variables du thème, pas de hex en dur
- [ ] Le commit message référence le ticket
```

### 7.3 Intégration CI/CD recommandée

```yaml
# .github/workflows/theme-deploy-staging.yml (exemple GitHub Actions)
name: Deploy Theme to Staging

on:
  push:
    branches: [develop]
    paths:
      - 'themes/mission-theme/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Lint Sass
      - name: Sass lint
        run: npx stylelint "themes/mission-theme/**/*.scss"

      # Compile test (vérifier que le Sass est valide)
      - name: Sass compile check
        run: |
          npx sass --no-source-map --style=compressed \
            themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss \
            /tmp/extras-test.css
          echo "Compiled size: $(wc -c < /tmp/extras-test.css) bytes"

      # Deploy to staging server
      - name: Deploy theme files
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /chemin/vers/repo && git pull origin develop
            docker compose -p tutor_local exec -T lms openedx-assets build
            docker compose -p tutor_local exec -T lms openedx-assets collect --settings=tutor.assets
            docker compose -p tutor_local restart lms cms
            sleep 30

      # Smoke test
      - name: Smoke test
        run: |
          chmod +x ./scripts/smoke-test.sh
          ./scripts/smoke-test.sh academie.staging.missionformations.com studio.staging.missionformations.com
```

---

## Annexe — Commandes de référence rapide

```bash
# Voir quel thème est actif
tutor config printvalue DEFAULT_SITE_THEME

# Voir les thèmes disponibles dans le conteneur
docker compose -p tutor_local exec lms ls /openedx/themes/

# Rebuild assets (thème spécifique)
docker compose -p tutor_local exec lms openedx-assets build --themes mission-theme

# Rebuild assets (tous les thèmes — plus lent, plus sûr)
docker compose -p tutor_local exec lms openedx-assets build

# Collectstatic
docker compose -p tutor_local exec lms openedx-assets collect --settings=tutor.assets

# Restart services
docker compose -p tutor_local restart lms cms caddy

# Logs LMS en temps réel
docker compose -p tutor_local logs -f --tail=50 lms

# Vérifier le contenu du bundle CSS compilé
docker compose -p tutor_local exec lms bash -c \
  'cat /openedx/staticfiles/css/lms-main-v2*.css | grep -c "mf-nav"'

# Forcer un refresh navigateur sans cache
curl -H "Cache-Control: no-cache" -s https://academie.staging.missionformations.com/ | head -50
```
