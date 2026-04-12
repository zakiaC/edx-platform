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

  echo "--- 3/4 Collectstatic ---"
  # IMPORTANT: PAS de --clear sinon webpack-stats.json est supprime → 500 sur toutes les pages
  docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput 2>&1 | tail -3

  echo "--- 4/4 Force-copy theme CSS → staticfiles ---"
  # FIX regression 2026-03-22: collectstatic ne remplace pas les CSS si le hash
  # Django n'a pas change. On force la copie du CSS theme par-dessus staticfiles.
  docker exec $CONTAINER bash -c '\
    for f in /openedx/themes/mission-theme/lms/static/css/lms-main-v1*.css; do \
      bn=$(basename "$f"); \
      cp -f "$f" /openedx/staticfiles/css/"$bn"; \
      for hf in /openedx/staticfiles/css/$(echo "$bn" | sed "s/\.css$//").*.css; do \
        [ -f "$hf" ] && cp -f "$f" "$hf"; \
      done; \
    done && echo "Force-copy OK"'

elif [ "$ENV" = "staging" ]; then
  CONTAINER="tutor_local-lms-1"
  CMS_CONTAINER="tutor_local-cms-1"
  THEME_HOST="/root/edx-platform/themes/mission-theme"
  EDX_ROOT="/root/edx-platform"
  STAGING_URL="https://academie.staging.missionformations.com"

  # PRE-DEPLOY: tag git + backup settings serveur
  echo "--- 0/11 Pre-deploy: tag git + backup settings ---"
  git tag "pre-deploy-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
  ssh staging-openedx "\
    cp ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py \
       /tmp/production.py.pre-deploy-$(date +%Y%m%d) 2>/dev/null || true"
  echo "Tag git cree + settings sauvegardes"

  echo "--- 1/11 Permissions ---"
  ssh staging-openedx \
    "chown -R 1000:1000 $THEME_HOST && chmod -R 775 $THEME_HOST"

  echo "--- 2/11 Sync code disque → LMS container ---"
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
    docker exec -u root $CONTAINER rm -rf /openedx/edx-platform/tests/ && \
    docker cp $EDX_ROOT/tests/ \
      $CONTAINER:/openedx/edx-platform/tests/ && \
    docker exec -u root $CONTAINER chown -R 1000:1000 /openedx/edx-platform/tests/ && \
    docker exec $CONTAINER pip install pytest -q 2>/dev/null && \
    echo 'Sync OK: plugin + theme + config + tests copies dans le container'"

  echo "--- 3/11 Compilation Sass ---"
  ssh staging-openedx \
    "docker exec $CONTAINER bash -c \
    'npm run compile-sass -- --skip-default 2>&1 | tail -5'"

  echo "--- 4/11 Vérification CSS ---"
  COUNT=$(ssh staging-openedx \
    "grep -c 'mf-' $THEME_HOST/lms/static/css/lms-main-v1.css || echo 0")
  echo "mf- occurrences: $COUNT"
  [ "$COUNT" = "0" ] && echo "ERREUR: CSS vide" && exit 1

  echo "--- 5/11 Collectstatic LMS + force-copy theme CSS ---"
  # IMPORTANT: PAS de --clear sinon webpack-stats.json est supprime → 500 sur toutes les pages
  ssh staging-openedx \
    "docker exec $CONTAINER \
    ./manage.py lms collectstatic --noinput 2>&1 | tail -3"

  # Force-copy : copier le CSS du theme par-dessus les fichiers collectstatic
  # Necessaire car collectstatic ne remplace pas si le hash Django n'a pas change
  echo "    Force-copy theme CSS → staticfiles..."
  ssh staging-openedx "docker exec $CONTAINER bash -c 'cp -f /openedx/themes/mission-theme/lms/static/css/lms-main-v1.css /openedx/staticfiles/css/lms-main-v1.css 2>/dev/null; cp -f /openedx/themes/mission-theme/lms/static/css/lms-main-v1-rtl.css /openedx/staticfiles/css/lms-main-v1-rtl.css 2>/dev/null; echo Force-copy OK'"

  # Copier aussi vers les fichiers hashes (si ils existent)
  ssh staging-openedx "docker exec $CONTAINER bash -c 'for hf in /openedx/staticfiles/css/lms-main-v1.*.css; do [ -f \"\$hf\" ] && cp -f /openedx/themes/mission-theme/lms/static/css/lms-main-v1.css \"\$hf\"; done 2>/dev/null; echo Hash-copy OK'"

  # Verification post-copy
  POST_COUNT=$(ssh staging-openedx "docker exec $CONTAINER bash -c 'grep -c mf-hero /openedx/staticfiles/css/lms-main-v1.css 2>/dev/null || echo 0'")
  echo "    mf-hero in staticfiles: $POST_COUNT"
  [ "$POST_COUNT" = "0" ] && echo "ERREUR: CSS theme absent de staticfiles apres force-copy" && exit 1

  echo "--- 6/11 Sync theme → CMS container ---"
  ssh staging-openedx "\
    docker exec $CMS_CONTAINER mkdir -p /openedx/edx-platform/themes/mission-theme/cms/templates/widgets/ \
      /openedx/edx-platform/themes/mission-theme/cms/static/images/ 2>/dev/null; \
    docker cp $EDX_ROOT/themes/mission-theme/cms/ \
      $CMS_CONTAINER:/openedx/edx-platform/themes/mission-theme/cms/ && \
    echo 'Sync CMS OK: theme copie dans le container CMS'"

  echo "--- 7/11 Collectstatic CMS ---"
  ssh staging-openedx \
    "docker exec $CMS_CONTAINER \
    ./manage.py cms collectstatic --noinput 2>&1 | tail -3"

  echo "--- 8/11 Vider cache Mako + Restart LMS + CMS ---"
  ssh staging-openedx "\
    docker exec $CONTAINER bash -c 'find /tmp -name \"*.mako.py\" -delete' && \
    docker exec $CMS_CONTAINER bash -c 'find /tmp -name \"*.mako.py\" -delete' && \
    docker restart $CONTAINER && \
    docker restart $CMS_CONTAINER"

  echo "--- 9/11 Commit CSS compilés ---"
  ssh staging-openedx "cd $EDX_ROOT && \
    git config user.email 'deploy@missionformations.com' && \
    git config user.name 'Deploy Bot' && \
    git add -f themes/mission-theme/lms/static/css/ && \
    git diff --cached --stat && \
    git commit -m 'build: CSS compilés mission-theme [$(date +%Y-%m-%d)]' || \
    echo 'Rien à commiter'"

  echo "--- 10/11 Tests post-deploy (smoke) ---"
  FAIL=0

  # Test homepage
  HTTP_HOME=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' -L '$STAGING_URL/' 2>/dev/null")
  echo "    Homepage: $HTTP_HOME"
  [ "$HTTP_HOME" != "200" ] && echo "    ERREUR: Homepage $HTTP_HOME" && FAIL=1

  # Test login
  HTTP_LOGIN=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' -L '$STAGING_URL/login' 2>/dev/null")
  echo "    Login: $HTTP_LOGIN"
  [ "$HTTP_LOGIN" != "200" ] && echo "    ERREUR: Login $HTTP_LOGIN" && FAIL=1

  # Test catalogue
  HTTP_CATALOGUE=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' -L '$STAGING_URL/catalogue/' 2>/dev/null")
  echo "    Catalogue: $HTTP_CATALOGUE"
  [ "$HTTP_CATALOGUE" != "200" ] && echo "    ERREUR: Catalogue $HTTP_CATALOGUE" && FAIL=1

  # Test cours about (pas besoin d'auth)
  HTTP_ABOUT=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' -L '$STAGING_URL/courses/course-v1:MissionFormations+MF-VTC-2025+2025/about' 2>/dev/null")
  echo "    Cours about: $HTTP_ABOUT"
  [ "$HTTP_ABOUT" != "200" ] && echo "    ERREUR: Cours about $HTTP_ABOUT" && FAIL=1

  # Test static CSS (pas de 404)
  HTTP_CSS=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' '$STAGING_URL/static/css/lms-main-v1.css' 2>/dev/null")
  echo "    CSS principal: $HTTP_CSS"
  [ "$HTTP_CSS" = "404" ] && echo "    ERREUR: CSS introuvable" && FAIL=1

  # Test Studio
  STUDIO_URL="https://studio.staging.missionformations.com"
  HTTP_STUDIO=$(ssh staging-openedx "curl -s -o /dev/null -w '%{http_code}' -L '$STUDIO_URL/' 2>/dev/null")
  echo "    Studio: $HTTP_STUDIO"
  [ "$HTTP_STUDIO" != "200" ] && [ "$HTTP_STUDIO" != "302" ] && echo "    ERREUR: Studio $HTTP_STUDIO" && FAIL=1

  if [ "$FAIL" = "1" ]; then
    echo ""
    echo "⚠️  REGRESSION DETECTEE — Verifier les logs et rollback si necessaire"
    echo "    Rollback: git checkout \$(git tag | grep pre-deploy | tail -1) && ./deploy.sh staging"
    exit 1
  else
    echo "    Tous les tests OK ✅"
  fi

else
  echo "Usage: ./deploy.sh [local|staging]"
  exit 1
fi

echo "=== DÉPLOIEMENT TERMINÉ ✅ ==="
