#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PATCH PRÉCIS — Correction _extras.scss
#
# Ce script effectue la transformation exacte:
#   body.view-index { ... }  →  .mf-home { ... }
#
# Et crée/corrige lms-main-v1.scss si nécessaire.
#
# Usage: ./patch-extras.sh /path/to/edx-platform
# ============================================================

REPO="${1:-.}"
EXTRAS="${REPO}/themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss"
ENTRY="${REPO}/themes/mission-theme/lms/static/sass/lms-main-v1.scss"

# ── Vérifications ──
[ -f "$EXTRAS" ] || { echo "🔴 ${EXTRAS} introuvable"; exit 1; }

echo "═══ PATCH _extras.scss ═══"
echo ""
echo "AVANT (lignes contenant view-index):"
grep -n "view-index" "$EXTRAS" 2>/dev/null | sed 's/^/  /' || echo "  (aucune — déjà nettoyé?)"
echo ""

# ── Transformation ──
# Remplacer TOUTES les variantes de body.view-index par .mf-home
sed -i.bak \
    -e 's/body\.view-index/.mf-home/g' \
    -e 's/body\s*\.view-index/.mf-home/g' \
    "$EXTRAS"

echo "APRÈS (lignes contenant mf-home):"
grep -n "mf-home" "$EXTRAS" | head -5 | sed 's/^/  /'
echo ""

# Vérification propre
REMAINING=$(grep -c "view-index" "$EXTRAS" || true)
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ _extras.scss: toutes les références view-index supprimées"
    rm -f "${EXTRAS}.bak"
else
    echo "🔴 ${REMAINING} références view-index restantes — correction manuelle requise:"
    grep -n "view-index" "$EXTRAS" | sed 's/^/   /'
    exit 1
fi

echo ""
echo "═══ PATCH lms-main-v1.scss ═══"
echo ""

if [ -f "$ENTRY" ]; then
    echo "Fichier existant. Contenu actuel:"
    cat "$ENTRY" | sed 's/^/  /'
    echo ""

    # Vérifier si extras est importé
    if grep -q "extras" "$ENTRY"; then
        echo "✅ lms-main-v1.scss: import _extras déjà présent"
    else
        echo "Ajout de l'import _extras..."
        echo "" >> "$ENTRY"
        echo "// Mission theme custom styles" >> "$ENTRY"
        echo "@import 'partials/lms/theme/extras';" >> "$ENTRY"
        echo "✅ Import ajouté"
    fi
else
    echo "Fichier absent — création..."
    mkdir -p "$(dirname "$ENTRY")"
    cat > "$ENTRY" << 'SCSS'
// themes/mission-theme/lms/static/sass/lms-main-v1.scss
//
// Entry-point Sass thème mission-theme — override lms-main-v1.scss core.
// Le comprehensive theming d'Open edX utilise ce fichier à la place
// du lms-main-v1.scss par défaut quand le thème est actif.

// 1. Importer le pipeline LMS complet
@import 'lms/static/sass/lms-main-v1';

// 2. Ajouter les styles custom Mission (homepage, composants)
@import 'partials/lms/theme/extras';
SCSS
    echo "✅ Fichier créé"
fi

echo ""
echo "═══ VÉRIFICATION TEMPLATE HOMEPAGE ═══"
echo ""

# Chercher le template
INDEX_TPL="${REPO}/themes/mission-theme/lms/templates/index.html"
if [ -f "$INDEX_TPL" ]; then
    MF_HOME_COUNT=$(grep -c "mf-home" "$INDEX_TPL" || true)
    if [ "$MF_HOME_COUNT" -gt 0 ]; then
        echo "✅ Template index.html contient déjà class mf-home"
    else
        echo "⚠️  Template index.html ne contient PAS la classe mf-home"
        echo ""
        echo "   ACTIONS POSSIBLES (choisir UNE):"
        echo ""
        echo "   A) Ajouter un wrapper dans le template:"
        echo "      <div class=\"mf-home\">"
        echo "        ... contenu homepage ..."
        echo "      </div>"
        echo ""
        echo "   B) Si les classes .mf-* sont directement sur les éléments HTML"
        echo "      (ex: <nav class=\"mf-nav\">, <section class=\"mf-hero\">),"
        echo "      alors retirer le wrapper .mf-home de _extras.scss et"
        echo "      utiliser les sélecteurs de classe directs:"
        echo "        .mf-nav { ... }   au lieu de   .mf-home .mf-nav { ... }"
        echo ""
        echo "   Vérification de la structure actuelle du template:"
        grep -n "mf-nav\|mf-hero\|mf-section\|mf-home\|class=" "$INDEX_TPL" | head -15 | sed 's/^/   /'
    fi
else
    echo "ℹ️  Template index.html non trouvé à: ${INDEX_TPL}"
    echo "   Recherche d'alternatives..."
    find "${REPO}/themes/mission-theme/lms/templates/" -name "*.html" 2>/dev/null | head -10 | sed 's/^/   /'
fi

echo ""
echo "═══════════════════════════════════════════"
echo " PATCH TERMINÉ"
echo ""
echo " Fichiers modifiés:"
echo "   1. ${EXTRAS}"
echo "   2. ${ENTRY}"
echo ""
echo " Prochaines étapes:"
echo "   1. Vérifier le template homepage (option A ou B ci-dessus)"
echo "   2. Lancer les tests:"
echo "      python3 -m unittest discover -s custom-infra/tests -p 'test_*.py' -v"
echo "   3. Commit + push"
echo "   4. Deploy staging: ./02-deploy-staging.sh"
echo "═══════════════════════════════════════════"
