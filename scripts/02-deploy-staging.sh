#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# DEPLOY + VALIDATE — Staging theme deployment
#
# Usage:
#   ./02-deploy-staging.sh
#
# Pré-requis: être sur le serveur staging avec accès docker compose
# ============================================================

TUTOR_PROJECT="tutor_local"
THEME_NAME="mission-theme"
DC="docker compose -p ${TUTOR_PROJECT}"
LMS_DOMAIN="academie.staging.missionformations.com"
CMS_DOMAIN="studio.staging.missionformations.com"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      DEPLOY STAGING — Theme ${THEME_NAME}               ║"
echo "║      $(date -u +%Y-%m-%dT%H:%M:%SZ)                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── PRE-CHECK ──
echo "▸ Pre-check: services en cours"
${DC} ps --format "table {{.Name}}\t{{.Status}}" | grep -E "lms|cms|caddy" || {
    echo "🔴 Services non trouvés — vérifier le projet docker compose"
    exit 1
}
echo ""

# ── STEP 1: Vérifier les fichiers thème dans le conteneur ──
echo "▸ Step 1/5 — Vérification fichiers thème dans le conteneur"

EXTRAS_PATH="/openedx/themes/${THEME_NAME}/lms/static/sass/partials/lms/theme/_extras.scss"
ENTRY_PATH="/openedx/themes/${THEME_NAME}/lms/static/sass/lms-main-v1.scss"

${DC} exec -T lms test -f "$EXTRAS_PATH" && \
    echo "  ✅ _extras.scss présent" || \
    { echo "  🔴 _extras.scss ABSENT dans le conteneur"; exit 1; }

${DC} exec -T lms test -f "$ENTRY_PATH" && \
    echo "  ✅ lms-main-v1.scss entry-point présent" || \
    { echo "  🔴 lms-main-v1.scss ABSENT — le thème n'override pas l'entry-point"; exit 1; }

# Vérifier que view-index n'est plus dans _extras.scss
VIEW_INDEX_COUNT=$(${DC} exec -T lms grep -c "body\.view-index" "$EXTRAS_PATH" 2>/dev/null || echo "0")
if [ "$VIEW_INDEX_COUNT" != "0" ]; then
    echo "  🔴 body.view-index encore présent dans _extras.scss (${VIEW_INDEX_COUNT} occurrences)"
    echo "     Le fix n'a pas été appliqué correctement"
    exit 1
fi
echo "  ✅ Pas de body.view-index dans _extras.scss"

# Vérifier l'import
IMPORT_OK=$(${DC} exec -T lms grep -c "extras" "$ENTRY_PATH" 2>/dev/null || echo "0")
if [ "$IMPORT_OK" = "0" ]; then
    echo "  🔴 lms-main-v1.scss n'importe pas _extras"
    exit 1
fi
echo "  ✅ lms-main-v1.scss importe _extras"
echo ""

# ── STEP 2: Build assets ──
echo "▸ Step 2/5 — Build assets (Sass → CSS)"
echo "  Cela peut prendre 2-5 minutes..."
${DC} exec -T lms openedx-assets build --themes "${THEME_NAME}" 2>&1 | tail -5
# Fallback si --themes non supporté
if [ $? -ne 0 ]; then
    echo "  ⚠️  --themes non supporté, build complet..."
    ${DC} exec -T lms openedx-assets build 2>&1 | tail -5
fi
echo "  ✅ Build terminé"
echo ""

# ── STEP 3: Collectstatic ──
echo "▸ Step 3/5 — Collectstatic (hash + copie)"
${DC} exec -T lms openedx-assets collect --settings=tutor.assets 2>&1 | tail -5 || \
    ${DC} exec -T lms python manage.py lms collectstatic --noinput 2>&1 | tail -5
echo "  ✅ Collectstatic terminé"
echo ""

# ── STEP 4: Vérifier le bundle compilé AVANT restart ──
echo "▸ Step 4/5 — Vérification bundle compilé sur disque"

# Trouver le bundle
BUNDLE_FILE=$(${DC} exec -T lms bash -c \
    'find /openedx/staticfiles/ -name "lms-main-v1*.css" -not -name "*.map" | head -1' 2>/dev/null || echo "")

if [ -z "$BUNDLE_FILE" ]; then
    echo "  🔴 Aucun bundle lms-main-v1*.css trouvé dans staticfiles"
    echo "  Tentative avec un pattern plus large..."
    BUNDLE_FILE=$(${DC} exec -T lms bash -c \
        'find /openedx/staticfiles/ -name "lms-main*.css" -not -name "*.map" | head -1' 2>/dev/null || echo "")
fi

if [ -n "$BUNDLE_FILE" ]; then
    BUNDLE_FILE=$(echo "$BUNDLE_FILE" | tr -d '\r\n')
    echo "  Bundle trouvé: ${BUNDLE_FILE}"

    echo "  Vérification classes mf-* dans le bundle compilé:"
    for CLASS in "mf-nav" "mf-hero" "mf-section" "mf-footer" "mf-card"; do
        COUNT=$(${DC} exec -T lms grep -c "${CLASS}" "${BUNDLE_FILE}" 2>/dev/null || echo "0")
        COUNT=$(echo "$COUNT" | tr -d '\r\n')
        if [ "$COUNT" -gt 0 ]; then
            echo "     ✅ .${CLASS} — ${COUNT} occurrence(s)"
        else
            echo "     🔴 .${CLASS} — ABSENT du bundle compilé"
        fi
    done

    # Vérifier absence de view-index dans le bundle
    VI_COUNT=$(${DC} exec -T lms grep -c "view-index" "${BUNDLE_FILE}" 2>/dev/null || echo "0")
    VI_COUNT=$(echo "$VI_COUNT" | tr -d '\r\n')
    if [ "$VI_COUNT" = "0" ]; then
        echo "     ✅ Pas de view-index dans le bundle"
    else
        echo "     ⚠️  view-index trouvé dans le bundle (${VI_COUNT}) — vérifier"
    fi
else
    echo "  🔴 Aucun bundle CSS trouvé — problème de build"
    exit 1
fi
echo ""

# ── STEP 5: Restart ──
echo "▸ Step 5/5 — Restart LMS + CMS"
${DC} restart lms cms
echo "  ⏳ Attente démarrage (40s)..."
sleep 40
echo "  ✅ Services redémarrés"
echo ""

# ══════════════════════════════════════════
# VALIDATION RUNTIME
# ══════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              VALIDATION RUNTIME                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

check() {
    if [ "$2" -eq 0 ]; then
        PASS=$((PASS + 1))
        echo "  ✅ $1"
    else
        FAIL=$((FAIL + 1))
        echo "  🔴 $1"
        [ -n "${3:-}" ] && echo "     ${3}"
    fi
}

# V1: HTTP 200 homepage
echo "▸ V1: Disponibilité"
HTTP_LMS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "https://${LMS_DOMAIN}/" || echo "000")
check "LMS homepage HTTP 200" "$([ "$HTTP_LMS" = "200" ] && echo 0 || echo 1)" "Got: ${HTTP_LMS}"

HTTP_CMS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "https://${CMS_DOMAIN}/" || echo "000")
check "CMS Studio accessible" "$(echo "$HTTP_CMS" | grep -qE "^(200|302)$" && echo 0 || echo 1)" "Got: ${HTTP_CMS}"
echo ""

# V2: Markers HTML
echo "▸ V2: Markers HTML homepage"
HOMEPAGE=$(curl -s --max-time 15 "https://${LMS_DOMAIN}/")

for MARKER in "formateurNabil" "Serie1-VTC2" "Deuxième test formation"; do
    COUNT=$(echo "$HOMEPAGE" | grep -c "$MARKER" || true)
    check "Marker '${MARKER}' présent" "$([ "$COUNT" -gt 0 ] && echo 0 || echo 1)"
done
echo ""

# V3: Pas de legacy
echo "▸ V3: Absence legacy"
LEGACY_COUNT=$(echo "$HOMEPAGE" | grep -c "mf-homepage\.css" || true)
check "Pas de mf-homepage.css legacy" "$([ "$LEGACY_COUNT" -eq 0 ] && echo 0 || echo 1)" "${LEGACY_COUNT} occurrence(s)"
echo ""

# V4: Bundle CSS avec classes mf-*
echo "▸ V4: Bundle CSS servi contient les classes mf-*"

BUNDLE_HREF=$(echo "$HOMEPAGE" | grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/href="//;s/"//')
echo "  Bundle URL: ${BUNDLE_HREF:-INTROUVABLE}"

if [ -n "$BUNDLE_HREF" ]; then
    if [[ "$BUNDLE_HREF" != http* ]]; then
        BUNDLE_URL="https://${LMS_DOMAIN}${BUNDLE_HREF}"
    else
        BUNDLE_URL="$BUNDLE_HREF"
    fi

    BUNDLE_CONTENT=$(curl -s --max-time 30 "$BUNDLE_URL")
    BUNDLE_SIZE=${#BUNDLE_CONTENT}
    check "Bundle téléchargeable (>${BUNDLE_SIZE} bytes)" "$([ "$BUNDLE_SIZE" -gt 1000 ] && echo 0 || echo 1)"

    for CLASS in "mf-nav" "mf-hero" "mf-section" "mf-footer" "mf-card"; do
        COUNT=$(echo "$BUNDLE_CONTENT" | grep -c "${CLASS}" || true)
        check "Classe .${CLASS} dans bundle CSS (${COUNT})" "$([ "$COUNT" -gt 0 ] && echo 0 || echo 1)"
    done
else
    FAIL=$((FAIL + 5))
    echo "  🔴 Bundle CSS non trouvé dans le HTML"
fi
echo ""

# ── RÉSULTAT ──
TOTAL=$((PASS + FAIL))
echo "╔══════════════════════════════════════════════════════════╗"
if [ "$FAIL" -eq 0 ]; then
    echo "║  ✅  ALL PASS  (${PASS}/${TOTAL})                              ║"
    echo "║  Le design Mission est actif en staging.                 ║"
else
    echo "║  🔴  FAIL  (${PASS} pass / ${FAIL} fail / ${TOTAL} total)            ║"
    echo "║  Le design n'est PAS complètement actif.                 ║"
fi
echo "╚══════════════════════════════════════════════════════════╝"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
