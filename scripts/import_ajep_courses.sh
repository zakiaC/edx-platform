#!/bin/bash
# import_ajep_courses.sh — Crée et importe les 24 cours AJEP sur staging
# Usage: ./scripts/import_ajep_courses.sh
set -e

STAGING="staging-openedx"
CONTAINER="tutor_local-lms-1"
CMS_CONTAINER="tutor_local-cms-1"
REMOTE_DIR="/tmp/ajep_courses"
LOCAL_DIR="$(dirname "$0")/../ajep_courses"
STUDIO_URL="https://studio.staging.missionformations.com"

# Identifiants admin Studio (à adapter)
ADMIN_USER="${STUDIO_ADMIN_USER:-admin}"
ADMIN_EMAIL="${STUDIO_ADMIN_EMAIL:-admin@missionformations.com}"

ORG="AJEP"
SESSION="2026"

# Liste des 24 cours : CODE|DISPLAY_NAME
COURSES=(
  "MATH-CM2|Mathematiques CM2 -- Soutien Scolaire"
  "FR-CM2|Francais CM2 -- Soutien Scolaire"
  "ANG-CM2|Anglais CM2 -- Soutien Scolaire"
  "MATH-6E|Mathematiques 6eme -- Soutien Scolaire"
  "FR-6E|Francais 6eme -- Soutien Scolaire"
  "ANG-6E|Anglais 6eme -- Soutien Scolaire"
  "MATH-5E|Mathematiques 5eme -- Soutien Scolaire"
  "FR-5E|Francais 5eme -- Soutien Scolaire"
  "ANG-5E|Anglais 5eme -- Soutien Scolaire"
  "MATH-4E|Mathematiques 4eme -- Soutien Scolaire"
  "FR-4E|Francais 4eme -- Soutien Scolaire"
  "ANG-4E|Anglais 4eme -- Soutien Scolaire"
  "MATH-3E|Mathematiques 3eme -- Soutien Scolaire (Brevet)"
  "FR-3E|Francais 3eme -- Soutien Scolaire (Brevet)"
  "ANG-3E|Anglais 3eme -- Soutien Scolaire (Brevet)"
  "MATH-2NDE|Mathematiques Seconde -- Soutien Scolaire"
  "FR-2NDE|Francais Seconde -- Soutien Scolaire"
  "ANG-2NDE|Anglais Seconde -- Soutien Scolaire"
  "MATH-1ERE|Mathematiques Premiere -- Soutien Scolaire"
  "FR-1ERE|Francais Premiere -- Soutien Scolaire (EAF)"
  "ANG-1ERE|Anglais Premiere -- Soutien Scolaire"
  "MATH-TERM|Mathematiques Terminale -- Soutien Scolaire (Bac)"
  "FR-TERM|Francais Terminale -- Soutien Scolaire (Bac)"
  "ANG-TERM|Anglais Terminale -- Soutien Scolaire (Bac)"
)

echo "=============================================="
echo " IMPORT 24 COURS AJEP — $(date '+%Y-%m-%d %H:%M')"
echo "=============================================="

# ------------------------------------------------------------------
# Étape 1 : Copier les .tar.gz sur le serveur staging
# ------------------------------------------------------------------
echo ""
echo "--- 1/4 Copie des fichiers OLX sur staging ---"
ssh $STAGING "mkdir -p $REMOTE_DIR"
scp "$LOCAL_DIR"/*.tar.gz "$STAGING:$REMOTE_DIR/"
echo "  -> 24 fichiers copiés sur $STAGING:$REMOTE_DIR/"

# ------------------------------------------------------------------
# Étape 2 : Copier les .tar.gz dans le container CMS
# ------------------------------------------------------------------
echo ""
echo "--- 2/4 Copie dans le container CMS ---"
ssh $STAGING "docker exec $CMS_CONTAINER mkdir -p /tmp/ajep_import"
ssh $STAGING "docker cp $REMOTE_DIR/. $CMS_CONTAINER:/tmp/ajep_import/"
echo "  -> Fichiers copiés dans le container CMS"

# ------------------------------------------------------------------
# Étape 3 : Créer les 24 cours vides via manage.py CMS
# ------------------------------------------------------------------
echo ""
echo "--- 3/4 Création des cours dans le modulestore ---"

CREATED=0
SKIPPED=0
FAILED=0

for entry in "${COURSES[@]}"; do
  CODE="${entry%%|*}"
  DISPLAY="${entry##*|}"
  COURSE_KEY="course-v1:${ORG}+${CODE}+${SESSION}"

  # Vérifier si le cours existe déjà
  EXISTS=$(ssh $STAGING "docker exec $CMS_CONTAINER python manage.py cms shell -c \"
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
ck = CourseKey.from_string('${COURSE_KEY}')
c = modulestore().get_course(ck)
print('yes' if c else 'no')
\" 2>/dev/null" | tail -1)

  if [ "$EXISTS" = "yes" ]; then
    echo "  [SKIP] $COURSE_KEY (existe déjà)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Créer le cours via manage.py
  RESULT=$(ssh $STAGING "docker exec $CMS_CONTAINER python manage.py cms shell -c \"
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.exceptions import DuplicateCourseError

store = modulestore()
ck = CourseKey.from_string('${COURSE_KEY}')
try:
    with store.default_store(ModuleStoreEnum.Type.split):
        course = store.create_course(
            org=ck.org,
            course=ck.course,
            run=ck.run,
            user_id=ModuleStoreEnum.UserID.mgmt_command,
            fields={'display_name': '${DISPLAY}'},
        )
    print('created')
except DuplicateCourseError:
    print('duplicate')
except Exception as e:
    print(f'error:{e}')
\" 2>/dev/null" | tail -1)

  case "$RESULT" in
    created)
      echo "  [OK]   $COURSE_KEY — $DISPLAY"
      CREATED=$((CREATED + 1))
      ;;
    duplicate)
      echo "  [SKIP] $COURSE_KEY (duplicate)"
      SKIPPED=$((SKIPPED + 1))
      ;;
    *)
      echo "  [FAIL] $COURSE_KEY — $RESULT"
      FAILED=$((FAILED + 1))
      ;;
  esac
done

echo ""
echo "  Résultat: $CREATED créés, $SKIPPED existants, $FAILED erreurs"

# ------------------------------------------------------------------
# Étape 4 : Importer le contenu OLX dans chaque cours
# ------------------------------------------------------------------
echo ""
echo "--- 4/4 Import OLX dans chaque cours ---"

IMPORTED=0
IMPORT_FAILED=0

for entry in "${COURSES[@]}"; do
  CODE="${entry%%|*}"
  COURSE_KEY="course-v1:${ORG}+${CODE}+${SESSION}"
  TAR_FILE="AJEP_${CODE}_${SESSION}.tar.gz"

  RESULT=$(ssh $STAGING "docker exec $CMS_CONTAINER python manage.py cms shell -c \"
import os
from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import CourseKey
from cms.djangoapps.contentstore.tasks import import_olx

User = get_user_model()
try:
    admin = User.objects.filter(is_superuser=True).first()
    course_key = CourseKey.from_string('${COURSE_KEY}')

    # Extraire le tar.gz
    import tarfile, tempfile
    extract_dir = tempfile.mkdtemp(prefix='ajep_')
    tar_path = '/tmp/ajep_import/${TAR_FILE}'

    if not os.path.exists(tar_path):
        print(f'missing:{tar_path}')
    else:
        with tarfile.open(tar_path, 'r:gz') as t:
            t.extractall(extract_dir)

        # Import via modulestore
        from xmodule.modulestore.django import modulestore
        from xmodule.modulestore.xml_importer import import_course_from_xml
        from xmodule.modulestore import ModuleStoreEnum

        store = modulestore()
        course_items = import_course_from_xml(
            store,
            ModuleStoreEnum.UserID.mgmt_command,
            extract_dir,
            source_dirs=['course'],
            target_id=course_key,
            create_if_not_present=True,
            static_content_store=None,
        )
        print('imported')
except Exception as e:
    print(f'error:{e}')
\" 2>/dev/null" | tail -1)

  case "$RESULT" in
    imported)
      echo "  [OK]   $COURSE_KEY — importé"
      IMPORTED=$((IMPORTED + 1))
      ;;
    missing*)
      echo "  [MISS] $COURSE_KEY — fichier non trouvé"
      IMPORT_FAILED=$((IMPORT_FAILED + 1))
      ;;
    *)
      echo "  [FAIL] $COURSE_KEY — $RESULT"
      IMPORT_FAILED=$((IMPORT_FAILED + 1))
      ;;
  esac
done

echo ""
echo "  Import: $IMPORTED réussis, $IMPORT_FAILED erreurs"

# ------------------------------------------------------------------
# Résumé final
# ------------------------------------------------------------------
echo ""
echo "=============================================="
echo " TERMINÉ"
echo "=============================================="
echo " Cours créés:   $CREATED"
echo " Cours importés: $IMPORTED"
echo " Vérifier sur Studio: $STUDIO_URL"
echo ""
echo " Prochaine étape:"
echo "   1. Vérifier les cours sur Studio"
echo "   2. Créer l'académie AJEP via /academy-manager/create/"
echo "   3. Attacher les cours à l'académie"
echo "=============================================="
