# Staging DNS Records (Mission Formations)

Authoritative target VPS IP: `89.167.50.194`

## A records

- `staging.missionformations.com` -> `89.167.50.194`
- `academie.staging.missionformations.com` -> `89.167.50.194`
- `studio.staging.missionformations.com` -> `89.167.50.194`
- `api.staging.missionformations.com` -> `89.167.50.194`
- `apps.academie.staging.missionformations.com` -> `89.167.50.194`
- `meilisearch.academie.staging.missionformations.com` -> `89.167.50.194`

## CNAME records

- `preview.staging.missionformations.com` -> `staging.missionformations.com`
- `apps.staging.missionformations.com` -> `staging.missionformations.com`

## Fixes applied

- Removed duplicated domain suffix on `apps.academie.staging` record.
- Added missing `academie.staging` record.
