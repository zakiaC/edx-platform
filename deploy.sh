#!/bin/bash
# deploy.sh — Mission Formations OpenEdX
# Usage: ./deploy.sh [local|staging]
set -e

ENV=${1:-local}
echo "=== DÉPLOIEMENT $ENV — $(date '+%Y-%m-%d %H:%M:%S') ==="

if [ "$ENV" = "local" ]; then
  CONTAINER="tutor_local-lms-1"
  THEME_PATH="/openedx/themes/mission-theme"

  echo "--- 1/3 Compilation Sass ---"
  docker exec $CONTAINER \
    bash -c 'npm run compile-sass -- --skip-default 2>&1 | tail -5'

  echo "--- 2/3 Vérification CSS ---"
  COUNT=$(docker exec $CONTAINER \
    bash -c "grep -c 'mf-' $THEME_PATH/lms/static/css/lms-main-v1.css")
  echo "mf- occurrences: $COUNT"
  [ "$COUNT" = "0" ] && echo "ERREUR: CSS vide" && exit 1

  echo "--- 3/3 Collectstatic ---"
  docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput --clear 2>&1 | tail -3

elif [ "$ENV" = "staging" ]; then
  CONTAINER="tutor_local-lms-1"
  THEME_HOST="/root/edx-platform/themes/mission-theme"

  echo "--- 0/4 Permissions ---"
  ssh staging-openedx \
    "chown -R 1000:1000 $THEME_HOST && chmod -R 775 $THEME_HOST"

  echo "--- 1/4 Compilation Sass ---"
  ssh staging-openedx \
    "docker exec $CONTAINER bash -c \
    'npm run compile-sass -- --skip-default 2>&1 | tail -5'"

  echo "--- 2/4 Vérification CSS ---"
  COUNT=$(ssh staging-openedx \
    "grep -c 'mf-' $THEME_HOST/lms/static/css/lms-main-v1.css || echo 0")
  echo "mf- occurrences: $COUNT"
  [ "$COUNT" = "0" ] && echo "ERREUR: CSS vide" && exit 1

  echo "--- 3/4 Collectstatic --clear ---"
  ssh staging-openedx \
    "docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput --clear 2>&1 | tail -3"

  echo "--- 4/4 Commit CSS compilés ---"
  ssh staging-openedx "cd /root/edx-platform && \
    git config user.email 'deploy@missionformations.com' && \
    git config user.name 'Deploy Bot' && \
    git add -f themes/mission-theme/lms/static/css/ && \
    git diff --cached --stat && \
    git commit -m 'build: CSS compilés mission-theme [$(date +%Y-%m-%d)]' || \
    echo 'Rien à commiter'"

else
  echo "Usage: ./deploy.sh [local|staging]"
  exit 1
fi

echo "=== DÉPLOIEMENT TERMINÉ ✅ ==="
