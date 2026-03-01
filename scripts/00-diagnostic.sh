#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# DIAGNOSTIC RCA — Mission Theme CSS non appliqué
# À exécuter depuis la racine du repo edx-platform
# ============================================================

REPO_ROOT="${1:-.}"
THEME="mission-theme"
THEME_SASS="${REPO_ROOT}/themes/${THEME}/lms/static/sass"
LMS_DOMAIN="academie.staging.missionformations.com"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           DIAGNOSTIC RCA — Theme CSS Pipeline            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── D1: Fichier _extras.scss existe ? ──
echo "▸ D1: Existence de _extras.scss"
EXTRAS="${THEME_SASS}/partials/lms/theme/_extras.scss"
if [ -f "$EXTRAS" ]; then
    LINES=$(wc -l < "$EXTRAS")
    echo "  ✅ EXISTE — ${LINES} lignes"
else
    echo "  🔴 ABSENT — ${EXTRAS}"
fi
echo ""

# ── D2: Sélecteur body.view-index dans _extras.scss ? ──
echo "▸ D2: Sélecteur body.view-index dans _extras.scss"
if [ -f "$EXTRAS" ]; then
    VIEW_INDEX_COUNT=$(grep -c "body\.view-index" "$EXTRAS" 2>/dev/null || true)
    echo "  Occurrences de 'body.view-index': ${VIEW_INDEX_COUNT}"
    if [ "$VIEW_INDEX_COUNT" -gt 0 ]; then
        echo "  🔴 CAUSE RACINE 1 CONFIRMÉE:"
        echo "     Les styles sont sous body.view-index { ... }"
        echo "     Mais le body réel est: <body class=\"ltr lang_fr\">"
        echo "     → Sélecteur ne matche JAMAIS → styles jamais appliqués"
        echo ""
        echo "  Lignes concernées:"
        grep -n "body\.view-index" "$EXTRAS" | head -10 | sed 's/^/     /'
    else
        echo "  ✅ Pas de body.view-index"
    fi
fi
echo ""

# ── D3: Quel entry-point Sass est utilisé (v1 ou v2) ? ──
echo "▸ D3: Entry-point Sass (v1 vs v2)"
echo "  Fichiers entry-point dans le thème:"
ls -la "${THEME_SASS}"/lms-main-v*.scss 2>/dev/null | sed 's/^/     /' || echo "     AUCUN entry-point trouvé"
echo ""
echo "  Fichiers entry-point dans edx-platform core:"
ls -la "${REPO_ROOT}"/lms/static/sass/lms-main-v*.scss 2>/dev/null | sed 's/^/     /' || echo "     (non trouvé localement)"
echo ""

# ── D4: _extras.scss est-il importé quelque part ? ──
echo "▸ D4: Import de _extras.scss dans la chaîne Sass"
echo "  Recherche @import|@use contenant 'extras' dans le thème:"
IMPORT_COUNT=$(grep -r "@import\|@use" "${THEME_SASS}/" --include="*.scss" 2>/dev/null | grep -i "extras" | wc -l || true)
if [ "$IMPORT_COUNT" -gt 0 ]; then
    grep -rn "@import\|@use" "${THEME_SASS}/" --include="*.scss" 2>/dev/null | grep -i "extras" | sed 's/^/     /'
    echo "  ✅ Import trouvé (${IMPORT_COUNT})"
else
    echo "  🔴 CAUSE RACINE 2 POTENTIELLE: _extras.scss n'est importé NULLE PART"
    echo "     → Le fichier existe mais n'entre jamais dans le bundle compilé"
fi
echo ""

# ── D5: Vérifier le bundle CSS servi en staging ──
echo "▸ D5: Bundle CSS servi en staging"
HOMEPAGE_HTML=$(curl -s --max-time 15 "https://${LMS_DOMAIN}/" 2>/dev/null || echo "FETCH_FAILED")

if [ "$HOMEPAGE_HTML" = "FETCH_FAILED" ]; then
    echo "  ⚠️  Impossible de fetch la homepage staging"
else
    # Extraire le body class
    BODY_CLASS=$(echo "$HOMEPAGE_HTML" | grep -oP '<body[^>]*class="[^"]*"' | head -1)
    echo "  Body tag: ${BODY_CLASS}"

    # Extraire le bundle CSS
    BUNDLE_HREF=$(echo "$HOMEPAGE_HTML" | grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/href="//;s/"//')
    echo "  Bundle CSS: ${BUNDLE_HREF}"

    if [ -n "$BUNDLE_HREF" ]; then
        if [[ "$BUNDLE_HREF" != http* ]]; then
            BUNDLE_URL="https://${LMS_DOMAIN}${BUNDLE_HREF}"
        else
            BUNDLE_URL="$BUNDLE_HREF"
        fi

        echo ""
        echo "  Vérification classes mf-* dans le bundle:"
        BUNDLE_CSS=$(curl -s --max-time 30 "$BUNDLE_URL" 2>/dev/null || echo "")
        for CLASS in "mf-nav" "mf-hero" "mf-section" "mf-footer" "mf-card" "mf-home"; do
            COUNT=$(echo "$BUNDLE_CSS" | grep -c "${CLASS}" || true)
            if [ "$COUNT" -gt 0 ]; then
                echo "     ✅ .${CLASS} — ${COUNT} occurrence(s)"
            else
                echo "     🔴 .${CLASS} — ABSENT"
            fi
        done

        # Vérifier si body.view-index est dans le bundle compilé
        echo ""
        VIEW_IN_BUNDLE=$(echo "$BUNDLE_CSS" | grep -c "view-index" || true)
        echo "  Sélecteur 'view-index' dans le bundle compilé: ${VIEW_IN_BUNDLE} occurrence(s)"
        if [ "$VIEW_IN_BUNDLE" -gt 0 ]; then
            echo "  🔴 CONFIRME: les styles SONT compilés dans le bundle"
            echo "     MAIS encapsulés sous body.view-index qui ne matche pas le body réel"
            echo "     → Les styles existent dans le CSS mais sont INACTIFS"
        fi
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    RÉSUMÉ RCA                            ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  CAUSE RACINE PRIMAIRE:                                  ║"
echo "║  Les styles mf-* sont encapsulés sous body.view-index    ║"
echo "║  dans _extras.scss. Le body réel de la homepage LMS      ║"
echo "║  a class='ltr lang_fr' (PAS view-index).                 ║"
echo "║  → Sélecteur ne matche jamais → styles jamais appliqués. ║"
echo "║                                                          ║"
echo "║  CAUSE CONTRIBUTIVE (si D4 = 0 imports):                 ║"
echo "║  _extras.scss n'est pas @import dans l'entry-point       ║"
echo "║  lms-main-v1.scss du thème.                              ║"
echo "║                                                          ║"
echo "║  FIX REQUIS:                                             ║"
echo "║  1. Remplacer body.view-index par .mf-home (scope HTML)  ║"
echo "║  2. Assurer l'import dans lms-main-v1.scss               ║"
echo "║  3. Ajouter class='mf-home' au template homepage         ║"
echo "║  4. Build → collect → restart                            ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
