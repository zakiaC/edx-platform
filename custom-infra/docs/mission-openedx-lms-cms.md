# Mission Formations LMS/CMS Setup

This repository already includes:

- A Mission theme at `themes/mission-theme`
- eox-tenant plugin sources at `eox-tenant/`

Use the helper script below to configure LMS and CMS domains plus theme settings
for the Mission tenant.

## 1. Prerequisites

- Open edX dependencies installed (Django/manage.py runnable)
- `eox-tenant` plugin installed/enabled in your Open edX runtime
- `themes/mission-theme` available on the runtime filesystem

## 2. Run the setup script

```bash
cd /Users/zakiachabane/edx-platform
chmod +x custom-infra/scripts/configure-mission-tenant.sh
custom-infra/scripts/configure-mission-tenant.sh
```

## 3. Optional overrides

By default the script uses:

- `TENANT_KEY=missionformations.com`
- `LMS_DOMAIN=lms.missionformations.com`
- `CMS_DOMAIN=studio.missionformations.com`
- `PREVIEW_DOMAIN=preview.lms.missionformations.com`
- `THEME_NAME=mission-theme`

Override any value as needed:

```bash
TENANT_KEY=missionformations.com \
LMS_DOMAIN=courses.missionformations.com \
CMS_DOMAIN=studio.missionformations.com \
PREVIEW_DOMAIN=preview.courses.missionformations.com \
THEME_DIR=/openedx/edx-platform/themes \
custom-infra/scripts/configure-mission-tenant.sh
```

By default, the script merges keys into the existing tenant config. If you need
to replace existing JSON values, run with:

```bash
OVERRIDE_CONFIG=true custom-infra/scripts/configure-mission-tenant.sh
```

## 4. Validate

1. Open LMS domain and check Mission footer/logo are visible.
2. Open CMS domain and check Studio resolves LMS links correctly.
3. Confirm route mapping in admin:
   - `EDUNEXT OPENEDX MULTITENANCY > Routes`
   - `EDUNEXT OPENEDX MULTITENANCY > Tenant configs`

## 5. Theme deploy and smoke (staging)

Use the standardized scripts for theme deployment and post-deploy checks:

```bash
cd /Users/zakiachabane/edx-platform
custom-infra/scripts/deploy-theme.sh /Users/zakiachabane/edx-platform
custom-infra/scripts/smoke-test.sh academie.staging.missionformations.com studio.staging.missionformations.com
```

RCA and troubleshooting details are documented in:

- `custom-infra/docs/openedx-theme-css-rca-runbook.md`
