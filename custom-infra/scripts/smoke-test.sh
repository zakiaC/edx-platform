#!/usr/bin/env bash
set -euo pipefail

# Post-deploy smoke test for Mission theme on Open edX staging.
# Usage:
#   custom-infra/scripts/smoke-test.sh [LMS_DOMAIN] [CMS_DOMAIN]

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
  if [[ "$result" -eq 0 ]]; then
    PASS=$((PASS + 1))
    echo "  PASS  - ${name}"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL  - ${name}"
    [[ -n "$detail" ]] && echo "         ${detail}"
  fi
}

echo ""
echo "========================================"
echo "SMOKE TEST | $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "LMS=${LMS_URL}"
echo "CMS=${CMS_URL}"
echo "========================================"

echo ""
echo "[1/5] endpoint availability"
LMS_HTTP="$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/" || echo 000)"
check "LMS homepage HTTP 200" "$( [[ "$LMS_HTTP" == "200" ]] && echo 0 || echo 1 )" "HTTP ${LMS_HTTP}"

LMS_LOGIN_HTTP="$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/login" || echo 000)"
check "LMS /login HTTP 200" "$( [[ "$LMS_LOGIN_HTTP" == "200" ]] && echo 0 || echo 1 )" "HTTP ${LMS_LOGIN_HTTP}"

LMS_API_HTTP="$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${LMS_URL}/api/user/v1/me" || echo 000)"
check "LMS API /api/user/v1/me HTTP 401|403" "$( echo "$LMS_API_HTTP" | grep -qE '^(401|403)$' && echo 0 || echo 1 )" "HTTP ${LMS_API_HTTP}"

CMS_HTTP="$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${CMS_URL}/" || echo 000)"
check "CMS root HTTP 200|302" "$( echo "$CMS_HTTP" | grep -qE '^(200|302)$' && echo 0 || echo 1 )" "HTTP ${CMS_HTTP}"

HOMEPAGE_HTML="$(curl -s --max-time 20 "${LMS_URL}/")"

echo ""
echo "[2/5] homepage markers"
check "Marker formateurNabil" "$( echo "${HOMEPAGE_HTML}" | grep -q 'formateurNabil' && echo 0 || echo 1 )"
check "Marker Serie1-VTC2" "$( echo "${HOMEPAGE_HTML}" | grep -q 'Serie1-VTC2' && echo 0 || echo 1 )"
check "Marker Deuxième test formation" "$( echo "${HOMEPAGE_HTML}" | grep -q 'Deuxième test formation' && echo 0 || echo 1 )"

echo ""
echo "[3/5] legacy markers absent"
LEGACY_COUNT="$(echo "${HOMEPAGE_HTML}" | grep -c 'mf-homepage\.css' || true)"
check "No legacy mf-homepage.css link" "$( [[ "$LEGACY_COUNT" -eq 0 ]] && echo 0 || echo 1 )" "occurrences=${LEGACY_COUNT}"

INLINE_LEGACY_COUNT="$(echo "${HOMEPAGE_HTML}" | grep -c '<!-- legacy-homepage-style -->' || true)"
check "No legacy inline marker" "$( [[ "$INLINE_LEGACY_COUNT" -eq 0 ]] && echo 0 || echo 1 )" "occurrences=${INLINE_LEGACY_COUNT}"

echo ""
echo "[4/5] css bundle contains mission classes"
BUNDLE_HREF="$(echo "${HOMEPAGE_HTML}" | grep -oE 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/^href="//;s/"$//')"
if [[ -z "$BUNDLE_HREF" ]]; then
  check "Found lms-main bundle" 1 "no lms-main*.css href in homepage"
else
  check "Found lms-main bundle" 0
  if [[ "$BUNDLE_HREF" == http* ]]; then
    BUNDLE_URL="$BUNDLE_HREF"
  else
    BUNDLE_URL="${LMS_URL}${BUNDLE_HREF}"
  fi

  BUNDLE_CSS="$(curl -s --max-time 30 "${BUNDLE_URL}")"
  BUNDLE_SIZE=${#BUNDLE_CSS}
  check "Bundle size > 1000" "$( [[ "$BUNDLE_SIZE" -gt 1000 ]] && echo 0 || echo 1 )" "size=${BUNDLE_SIZE}"

  for CLASS in mf-nav mf-hero mf-section mf-footer mf-card; do
    CLASS_COUNT="$(echo "$BUNDLE_CSS" | grep -c "$CLASS" || true)"
    check "Class .${CLASS} exists" "$( [[ "$CLASS_COUNT" -gt 0 ]] && echo 0 || echo 1 )" "occurrences=${CLASS_COUNT}"
  done
fi

echo ""
echo "[5/5] tls certificate"
TLS_EXPIRY="$(echo | openssl s_client -servername "$LMS_DOMAIN" -connect "${LMS_DOMAIN}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | sed 's/notAfter=//')"
if [[ -n "$TLS_EXPIRY" ]]; then
  if date -d "$TLS_EXPIRY" +%s >/dev/null 2>&1; then
    EXPIRY_EPOCH="$(date -d "$TLS_EXPIRY" +%s)"
  elif date -j -f "%b %d %T %Y %Z" "$TLS_EXPIRY" +%s >/dev/null 2>&1; then
    EXPIRY_EPOCH="$(date -j -f "%b %d %T %Y %Z" "$TLS_EXPIRY" +%s)"
  else
    EXPIRY_EPOCH=0
  fi
  NOW_EPOCH="$(date +%s)"
  DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
  check "TLS valid > 7 days" "$( [[ "$DAYS_LEFT" -gt 7 ]] && echo 0 || echo 1 )" "days_left=${DAYS_LEFT}, expiry=${TLS_EXPIRY}"
else
  check "TLS certificate readable" 1 "unable to parse certificate"
fi

echo ""
echo "========================================"
if [[ "$FAIL" -eq 0 ]]; then
  echo "RESULT: PASS (${PASS}/${TOTAL})"
  echo "========================================"
  exit 0
fi

echo "RESULT: FAIL (${PASS} pass / ${FAIL} fail / ${TOTAL} total)"
echo "========================================"
exit 1
