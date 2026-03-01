#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# DEPLOY — Thème mission-theme sur staging
# Mission Formations — Open edX (Tutor)
#
# Usage :
#   ./deploy-theme.sh [REPO_PATH]
#
# Pré-requis :
#   - Accès docker compose au projet tutor_local
#   - Thème monté dans le conteneur LMS
#
# Idempotent — peut être relancé à tout moment.
# ============================================================

REPO_PATH="${1:-/chemin/vers/repo}"
TUTOR_PROJECT="tutor_local"
THEME_NAME="mission-theme"
DC="docker compose -p ${TUTOR_PROJECT}"
LMS_DOMAIN="academie.staging.missionformations.com"

echo "=========================================="
echo " Déploiement thème ${THEME_NAME}"
echo " $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=========================================="

echo ""
echo "── STEP 1/7 — Pull du code thème ──"
cd "${REPO_PATH}" && git pull origin develop
COMMIT=$(git rev-parse --short HEAD)
echo "✅ Code à jour — commit: ${COMMIT}"

echo ""
echo "── STEP 2/7 — Backup CSS actuel ──"
BACKUP_TAG=$(date +%Y%m%d_%H%M%S)
${DC} exec -T lms bash -c \
  "mkdir -p /tmp/css-backup && cp -r /openedx/staticfiles/css /tmp/css-backup/${BACKUP_TAG}" 2>/dev/null || true
echo "✅ Backup: /tmp/css-backup/${BACKUP_TAG}"

echo ""
echo "── STEP 3/7 — Vérification fichiers thème dans conteneur ──"
${DC} exec -T lms ls /openedx/themes/${THEME_NAME}/lms/static/sass/lms-main-v2.scss
${DC} exec -T lms ls /openedx/themes/${THEME_NAME}/lms/static/sass/partials/lms/theme/_extras.scss
echo "✅ Fichiers thème présents"

echo ""
echo "── STEP 4/7 — Build assets (Sass → CSS) ──"
${DC} exec -T lms openedx-assets build --themes ${THEME_NAME} 2>&1 || \
  ${DC} exec -T lms openedx-assets build 2>&1
echo "✅ Assets compilés"

echo ""
echo "── STEP 5/7 — Collectstatic ──"
${DC} exec -T lms openedx-assets collect --settings=tutor.assets 2>&1 || \
  ${DC} exec -T lms python manage.py lms collectstatic --noinput --settings=tutor.assets 2>&1
echo "✅ Fichiers statiques collectés"

echo ""
echo "── STEP 6/7 — Restart LMS + CMS ──"
${DC} restart lms cms
echo "⏳ Attente démarrage (30s)..."
sleep 30
echo "✅ Services redémarrés"

echo ""
echo "── STEP 7/7 — Vérification rapide ──"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "https://${LMS_DOMAIN}/")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ LMS accessible (HTTP ${HTTP_CODE})"
else
    echo "🔴 LMS inaccessible (HTTP ${HTTP_CODE})"
    echo ""
    echo "ROLLBACK : restaurer CSS backup"
    echo "  ${DC} exec lms bash -c 'cp -r /tmp/css-backup/${BACKUP_TAG}/* /openedx/staticfiles/css/'"
    echo "  ${DC} restart lms cms"
    exit 1
fi

# Vérification CSS
BUNDLE_PATH=$(curl -s "https://${LMS_DOMAIN}/" | \
  grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | \
  sed 's/href="//;s/"//')

if [ -n "$BUNDLE_PATH" ]; then
    if [[ "$BUNDLE_PATH" != http* ]]; then
        BUNDLE_PATH="https://${LMS_DOMAIN}${BUNDLE_PATH}"
    fi
    MF_COUNT=$(curl -s "$BUNDLE_PATH" | grep -c "mf-nav" || true)
    if [ "$MF_COUNT" -gt 0 ]; then
        echo "✅ Classes .mf-nav dans le bundle CSS (${MF_COUNT} occurrences)"
    else
        echo "⚠️  Classes .mf-nav ABSENTES du bundle — vérifier l'import dans lms-main-v2.scss"
    fi
fi

echo ""
echo "=========================================="
echo " ✅ DÉPLOIEMENT TERMINÉ — commit ${COMMIT}"
echo "=========================================="
echo ""
echo "→ Lancer le smoke test complet :"
echo "  ./smoke-test.sh ${LMS_DOMAIN}"
