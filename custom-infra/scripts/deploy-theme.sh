#!/usr/bin/env bash
set -euo pipefail

# Deploy mission-theme on staging Tutor stack.
# Usage:
#   custom-infra/scripts/deploy-theme.sh [REPO_PATH]
# Optional env vars:
#   DEPLOY_BRANCH=staging
#   THEME_NAME=mission-theme
#   LMS_DOMAIN=academie.staging.missionformations.com
#   TUTOR_PROJECT=tutor_local
#   TUTOR_ENV_DIR=$HOME/.local/share/tutor/env/local

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_PATH="${1:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-staging}"
THEME_NAME="${THEME_NAME:-mission-theme}"
LMS_DOMAIN="${LMS_DOMAIN:-academie.staging.missionformations.com}"
TUTOR_PROJECT="${TUTOR_PROJECT:-tutor_local}"
TUTOR_ENV_DIR="${TUTOR_ENV_DIR:-$HOME/.local/share/tutor/env/local}"

if [[ -f "${TUTOR_ENV_DIR}/docker-compose.yml" && -f "${TUTOR_ENV_DIR}/docker-compose.prod.yml" ]]; then
  DC=(docker compose -f "${TUTOR_ENV_DIR}/docker-compose.yml" -f "${TUTOR_ENV_DIR}/docker-compose.prod.yml" --project-name "${TUTOR_PROJECT}")
else
  DC=(docker compose -p "${TUTOR_PROJECT}")
fi

dc() {
  "${DC[@]}" "$@"
}

run_lms() {
  dc exec -T lms bash -lc "$*"
}

run_url="https://${LMS_DOMAIN}"

echo "=========================================="
echo " Deploy theme ${THEME_NAME}"
echo " $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=========================================="

echo ""
echo "-- STEP 1/7: sync git branch (${DEPLOY_BRANCH})"
git -C "${REPO_PATH}" rev-parse --is-inside-work-tree >/dev/null
if git -C "${REPO_PATH}" show-ref --verify --quiet "refs/heads/${DEPLOY_BRANCH}"; then
  git -C "${REPO_PATH}" checkout "${DEPLOY_BRANCH}"
fi
git -C "${REPO_PATH}" fetch origin "${DEPLOY_BRANCH}"
git -C "${REPO_PATH}" pull --ff-only origin "${DEPLOY_BRANCH}"
COMMIT="$(git -C "${REPO_PATH}" rev-parse --short HEAD)"
echo "OK git sync -> ${COMMIT}"

echo ""
echo "-- STEP 2/7: backup current CSS"
BACKUP_TAG="$(date +%Y%m%d_%H%M%S)"
run_lms "mkdir -p /tmp/css-backup/${BACKUP_TAG} && cp -r /openedx/staticfiles/css /tmp/css-backup/${BACKUP_TAG}/" || true
echo "OK backup /tmp/css-backup/${BACKUP_TAG}"

echo ""
echo "-- STEP 3/7: verify theme files"
run_lms "ls -l /openedx/themes/${THEME_NAME}/lms/templates/index.html"
run_lms "ls -l /openedx/themes/${THEME_NAME}/lms/static/sass/partials/lms/theme/_extras.scss"
run_lms "grep -R --line-number '_extras' /openedx/themes/${THEME_NAME}/lms/static/sass || true"
echo "OK theme files visible from LMS container"

echo ""
echo "-- STEP 4/7: build assets"
if ! run_lms "openedx-assets build --themes ${THEME_NAME}"; then
  run_lms "openedx-assets build"
fi
echo "OK build"

echo ""
echo "-- STEP 5/7: collect static"
if ! run_lms "openedx-assets collect --settings=tutor.assets"; then
  run_lms "python manage.py lms collectstatic --noinput --settings=tutor.assets"
fi
echo "OK collect"

echo ""
echo "-- STEP 6/7: restart services"
dc restart lms cms caddy
sleep 20
echo "OK restart"

echo ""
echo "-- STEP 7/7: smoke verification"
HTTP_CODE="$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "${run_url}/" || echo 000)"
if [[ "${HTTP_CODE}" != "200" ]]; then
  echo "FAIL LMS homepage unreachable: HTTP ${HTTP_CODE}"
  echo "Rollback hint: restore /tmp/css-backup/${BACKUP_TAG} then restart lms/cms/caddy"
  exit 1
fi

HOMEPAGE_HTML="$(curl -s --max-time 20 "${run_url}/")"
BUNDLE_HREF="$(echo "${HOMEPAGE_HTML}" | grep -oE 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/^href="//;s/"$//')"
if [[ -z "${BUNDLE_HREF}" ]]; then
  echo "FAIL no lms-main css bundle found in homepage html"
  exit 1
fi

if [[ "${BUNDLE_HREF}" == http* ]]; then
  BUNDLE_URL="${BUNDLE_HREF}"
else
  BUNDLE_URL="${run_url}${BUNDLE_HREF}"
fi

MF_COUNT="$(curl -s --max-time 30 "${BUNDLE_URL}" | grep -c 'mf-nav' || true)"
if [[ "${MF_COUNT}" -eq 0 ]]; then
  echo "FAIL bundle does not contain .mf-nav -> ${BUNDLE_URL}"
  exit 1
fi

echo "OK homepage HTTP 200"
echo "OK bundle contains .mf-nav (${MF_COUNT})"
echo ""
echo "=========================================="
echo " DONE deploy theme ${THEME_NAME} @ ${COMMIT}"
echo "=========================================="
echo ""
echo "Next: custom-infra/scripts/smoke-test.sh ${LMS_DOMAIN}"
