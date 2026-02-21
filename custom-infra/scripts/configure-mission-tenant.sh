#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [[ -d "/openedx/edx-platform/themes" ]]; then
  DEFAULT_THEME_DIR="/openedx/edx-platform/themes"
elif [[ -d "/edx/app/edxapp/edx-platform/themes" ]]; then
  DEFAULT_THEME_DIR="/edx/app/edxapp/edx-platform/themes"
else
  DEFAULT_THEME_DIR="${PROJECT_ROOT}/themes"
fi

TENANT_KEY="${TENANT_KEY:-missionformations.com}"
LMS_DOMAIN="${LMS_DOMAIN:-lms.missionformations.com}"
CMS_DOMAIN="${CMS_DOMAIN:-studio.missionformations.com}"
PREVIEW_DOMAIN="${PREVIEW_DOMAIN:-preview.lms.missionformations.com}"
PLATFORM_NAME="${PLATFORM_NAME:-Mission Formations}"
THEME_NAME="${THEME_NAME:-mission-theme}"
THEME_DIR="${THEME_DIR:-$DEFAULT_THEME_DIR}"
MARKETING_SITE_URL="${MARKETING_SITE_URL:-https://missionformations.com}"
OVERRIDE_CONFIG="${OVERRIDE_CONFIG:-false}"

MANAGE_PY="${MANAGE_PY:-${PROJECT_ROOT}/manage.py}"
if [[ -x "${PROJECT_ROOT}/venv/bin/python" ]]; then
  PYTHON_BIN="${PYTHON_BIN:-${PROJECT_ROOT}/venv/bin/python}"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

if [[ ! -f "${MANAGE_PY}" ]]; then
  echo "manage.py not found: ${MANAGE_PY}"
  exit 1
fi

if [[ ! -d "${THEME_DIR}" ]]; then
  echo "Theme directory not found: ${THEME_DIR}"
  echo "Set THEME_DIR to a valid absolute path containing mission-theme."
  exit 1
fi

TMP_CONFIG="$(mktemp)"
cleanup() {
  rm -f "${TMP_CONFIG}"
}
trap cleanup EXIT

cat > "${TMP_CONFIG}" <<EOF
{
  "lms_configs": {
    "EDNX_USE_SIGNAL": true,
    "PLATFORM_NAME": "${PLATFORM_NAME}",
    "platform_name": "${PLATFORM_NAME}",
    "SITE_NAME": "${LMS_DOMAIN}",
    "LMS_BASE": "${LMS_DOMAIN}",
    "CMS_BASE": "${CMS_DOMAIN}",
    "DEFAULT_SITE_THEME": "${THEME_NAME}",
    "ENABLE_COMPREHENSIVE_THEMING": true,
    "COMPREHENSIVE_THEME_DIRS": ["${THEME_DIR}"],
    "MKTG_URLS": {
      "ROOT": "${MARKETING_SITE_URL}"
    },
    "FEATURES": {
      "PREVIEW_LMS_BASE": "${PREVIEW_DOMAIN}"
    }
  },
  "studio_configs": {
    "EDNX_USE_SIGNAL": true,
    "PLATFORM_NAME": "${PLATFORM_NAME}",
    "SITE_NAME": "${CMS_DOMAIN}",
    "LMS_BASE": "${LMS_DOMAIN}",
    "CMS_BASE": "${CMS_DOMAIN}",
    "DEFAULT_SITE_THEME": "${THEME_NAME}",
    "ENABLE_COMPREHENSIVE_THEMING": true,
    "COMPREHENSIVE_THEME_DIRS": ["${THEME_DIR}"],
    "FEATURES": {
      "PREVIEW_LMS_BASE": "${PREVIEW_DOMAIN}"
    }
  },
  "theming_configs": {},
  "meta": {
    "owner": "mission-formation"
  }
}
EOF

echo "Applying tenant configuration:"
echo "  tenant_key: ${TENANT_KEY}"
echo "  lms_domain: ${LMS_DOMAIN}"
echo "  cms_domain: ${CMS_DOMAIN}"
echo "  preview_domain: ${PREVIEW_DOMAIN}"
echo "  theme_name: ${THEME_NAME}"
echo "  theme_dir: ${THEME_DIR}"
echo

CMD=(
  "${PYTHON_BIN}" "${MANAGE_PY}" lms create_or_update_tenant_config
  --external-key "${TENANT_KEY}"
  --config-file "${TMP_CONFIG}"
)

if [[ "${OVERRIDE_CONFIG}" == "true" ]]; then
  CMD+=(--override)
fi

CMD+=("${LMS_DOMAIN}" "${CMS_DOMAIN}" "${PREVIEW_DOMAIN}")

"${CMD[@]}"

echo
echo "Tenant configuration applied."
