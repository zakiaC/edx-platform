# Open edX Theme CSS RCA Runbook (Mission Formations)

## Scope
This runbook documents the root-cause analysis and permanent fix path for the incident where the LMS homepage HTML is updated but CSS theme changes are not visible in staging.

Target domains:
- LMS: `academie.staging.missionformations.com`
- CMS/Studio: `studio.staging.missionformations.com`

## Root Cause Analysis

### Symptom
- Homepage markers are present in HTML (`formateurNabil`, `Serie1-VTC2`, `Deuxième test formation`).
- Visual style remains old.
- Legacy CSS link (`mf-homepage.css`) must be absent.

### Cause racine
The homepage CSS classes were not effectively served from the compiled LMS bundle. In practice this can come from:
1. `_extras.scss` not imported in the active Sass chain (`lms-main-v2.scss` path issue).
2. `openedx-assets build` not run after theme changes.
3. `openedx-assets collect`/`collectstatic` not run after build.
4. Services not restarted, keeping stale manifests/caches.

## Technical verification checklist

Run from staging host:

```bash
# 1) Verify theme files in LMS container
docker compose -p tutor_local exec -T lms bash -lc \
  "ls -la /openedx/themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss"

# 2) Verify Sass references
docker compose -p tutor_local exec -T lms bash -lc \
  "grep -R --line-number '_extras' /openedx/themes/mission-theme/lms/static/sass"

# 3) Verify live HTML markers
curl -s https://academie.staging.missionformations.com/ | \
  grep -nE 'formateurNabil|Serie1-VTC2|Deuxième test formation|mf-homepage\.css'

# 4) Verify active CSS bundle and class presence
BUNDLE=$(curl -s https://academie.staging.missionformations.com/ \
  | grep -oE 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/^href="//;s/"$//')
curl -s "https://academie.staging.missionformations.com${BUNDLE}" | grep -c 'mf-nav'
```

## Permanent fix (no workaround)

### Rule 1
Do not use page-level CSS links for theme pages. Keep all homepage styles inside theme Sass pipeline (`_extras.scss`).

### Rule 2
Ensure the active theme entrypoint (`lms-main-v2.scss`) resolves/includes the theme extras path.

### Rule 3
For any Sass modification, enforce this deployment sequence:
1. `openedx-assets build --themes mission-theme`
2. `openedx-assets collect --settings=tutor.assets`
3. restart `lms`, `cms`, and reverse proxy (`caddy`)

### Rule 4
Gate deploy with smoke tests checking both HTML and compiled CSS bundle content.

## Standard deployment command

```bash
custom-infra/scripts/deploy-theme.sh /path/to/edx-platform
```

## Standard smoke command

```bash
custom-infra/scripts/smoke-test.sh academie.staging.missionformations.com studio.staging.missionformations.com
```

## Acceptance criteria
- LMS `/` returns HTTP 200.
- HTML contains expected homepage markers.
- HTML does not reference `mf-homepage.css`.
- `lms-main*.css` bundle contains mission selectors (`mf-nav`, `mf-hero`, `mf-section`, `mf-footer`, `mf-card`).
- TLS remains valid (> 7 days).

## Incident closure record template
- Date/time UTC:
- Branch/commit deployed:
- Build command output status:
- Collect command output status:
- Restart status:
- Smoke result:
- Residual risk:
