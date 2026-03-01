#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# SMOKE TEST — Post-déploiement thème mission-theme
# Mission Formations — Open edX (Tutor)
#
# Usage :
#   ./smoke-test.sh [LMS_DOMAIN] [CMS_DOMAIN]
#   ./smoke-test.sh academie.staging.missionformations.com studio.staging.missionformations.com
#
# Exit code : 0 = ALL PASS, 1 = au moins 1 FAIL
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
    local result="$2"
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

BUNDLE_HREF=$(echo "$HOMEPAGE_HTML" | \
  grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | \
  sed 's/href="//;s/"//')

if [ -z "$BUNDLE_HREF" ]; then
    check "Bundle CSS lms-main trouvé dans HTML" "1" "Aucun lien lms-main*.css détecté"
else
    check "Bundle CSS lms-main trouvé dans HTML" "0"

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
    # Portable date parsing (Linux vs macOS)
    if date -d "$TLS_EXPIRY" +%s >/dev/null 2>&1; then
        EXPIRY_EPOCH=$(date -d "$TLS_EXPIRY" +%s)
    elif date -j -f "%b %d %T %Y %Z" "$TLS_EXPIRY" +%s >/dev/null 2>&1; then
        EXPIRY_EPOCH=$(date -j -f "%b %d %T %Y %Z" "$TLS_EXPIRY" +%s)
    else
        EXPIRY_EPOCH=0
    fi
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
    echo "║  ✅  ALL PASS  (${PASS}/${TOTAL} checks)                       ║"
    echo "╚════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "║  🔴  FAIL  (${PASS} pass / ${FAIL} fail / ${TOTAL} total)             ║"
    echo "╚════════════════════════════════════════════════════════╝"
    exit 1
fi
