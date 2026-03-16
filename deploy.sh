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
  # IMPORTANT: PAS de --clear sinon webpack-stats.json est supprime → 500 sur toutes les pages
  docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput 2>&1 | tail -3

elif [ "$ENV" = "staging" ]; then
  CONTAINER="tutor_local-lms-1"
  THEME_HOST="/root/edx-platform/themes/mission-theme"
  EDX_ROOT="/root/edx-platform"

  echo "--- 0/6 Permissions ---"
  ssh staging-openedx \
    "chown -R 1000:1000 $THEME_HOST && chmod -R 775 $THEME_HOST"

  echo "--- 1/6 Sync code disque → container ---"
  # CRITIQUE: le git pull met a jour /root/edx-platform (disque)
  # mais le container Docker a sa propre copie dans /openedx/edx-platform.
  # Sans ce docker cp, le container sert l'ancien code → pages manquantes.
  ssh staging-openedx "\
    docker cp $EDX_ROOT/lms/djangoapps/mission_central_admin/ \
      $CONTAINER:/openedx/edx-platform/lms/djangoapps/mission_central_admin/ && \
    docker cp $EDX_ROOT/themes/mission-theme/ \
      $CONTAINER:/openedx/themes/mission-theme/ && \
    docker cp $EDX_ROOT/tutor-patches/ \
      $CONTAINER:/openedx/edx-platform/tutor-patches/ && \
    echo 'Sync OK: plugin + theme + config copies dans le container'"

  echo "--- 2/6 Compilation Sass ---"
  ssh staging-openedx \
    "docker exec $CONTAINER bash -c \
    'npm run compile-sass -- --skip-default 2>&1 | tail -5'"

  echo "--- 3/6 Vérification CSS ---"
  COUNT=$(ssh staging-openedx \
    "grep -c 'mf-' $THEME_HOST/lms/static/css/lms-main-v1.css || echo 0")
  echo "mf- occurrences: $COUNT"
  [ "$COUNT" = "0" ] && echo "ERREUR: CSS vide" && exit 1

  echo "--- 4/6 Collectstatic ---"
  # IMPORTANT: PAS de --clear sinon webpack-stats.json est supprime → 500 sur toutes les pages
  ssh staging-openedx \
    "docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput 2>&1 | tail -3"

  echo "--- 5/6 Vider cache Mako + Restart ---"
  ssh staging-openedx "\
    docker exec $CONTAINER bash -c 'find /tmp -name \"*.mako.py\" -delete' && \
    docker restart $CONTAINER"

  echo "--- 6/6 Commit CSS compilés ---"
  ssh staging-openedx "cd $EDX_ROOT && \
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
