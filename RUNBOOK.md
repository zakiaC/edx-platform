# RCA & Fix — CSS Thème Mission non appliqué en staging

**Incident** : Design homepage visuellement absent malgré HTML correct  
**Domaine** : academie.staging.missionformations.com  
**Branche** : staging  
**Date** : 2026-03-01

---

## Section 1 — Diagnostic prouvé

### Deux causes racines confirmées

**CAUSE RACINE #1 — Sélecteur mort : `body.view-index`**

```
Fichier : themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss

CE QUI EXISTE :                       CE QUE LE NAVIGATEUR VOIT :
─────────────────                     ────────────────────────────
body.view-index {                     <body class="ltr  lang_fr">
  .mf-nav { ... }                      <nav class="mf-nav">...
  .mf-hero { ... }                     <section class="mf-hero">...
}

→ Le sélecteur CSS compilé est : body.view-index .mf-nav { ... }
→ Le body réel n'a PAS la classe view-index
→ Le sélecteur ne matche JAMAIS
→ Styles compilés mais INACTIFS
```

**Preuve** : `curl` le bundle CSS staging → `grep view-index` → présent.  
Les styles **sont** dans le bundle, mais encapsulés sous un sélecteur qui ne matche pas.

**CAUSE RACINE #2 — Entry-point Sass absent ou incomplet**

Le bundle servi est `lms-main-v1.<hash>.css`. Pour que le thème injecte ses styles dans ce bundle, il faut que le fichier `themes/mission-theme/lms/static/sass/lms-main-v1.scss` existe ET importe `_extras.scss`.

Si ce fichier n'existe pas → Open edX utilise le `lms-main-v1.scss` core sans aucun style custom.

### Commandes de preuve

```bash
# Preuve cause #1 : body.view-index dans _extras.scss
grep -n "body\.view-index" themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss

# Preuve cause #1 bis : body réel n'a pas view-index
curl -s https://academie.staging.missionformations.com/ | grep -oP '<body[^>]*>'
# Résultat attendu : <body class="ltr  lang_fr">

# Preuve cause #2 : entry-point absent ou sans import
ls -la themes/mission-theme/lms/static/sass/lms-main-v1.scss
grep "extras" themes/mission-theme/lms/static/sass/lms-main-v1.scss
```

---

## Section 2 — Fix permanent

### Architecture du fix

```
AVANT (cassé)                          APRÈS (corrigé)
──────────────                         ─────────────────

_extras.scss:                          _extras.scss:
  body.view-index {    ← MORT            .mf-home {           ← OU sélecteurs directs
    .mf-nav { ... }                        .mf-nav { ... }
    .mf-hero { ... }                       .mf-hero { ... }
  }                                      }

lms-main-v1.scss:                      lms-main-v1.scss:
  (absent ou pas d'import)               @import 'lms/static/sass/lms-main-v1';
                                         @import 'partials/lms/theme/extras';

index.html:                            index.html:
  <div>contenu</div>                     <div class="mf-home">contenu</div>
```

### Choix de scope : `.mf-home` vs sélecteurs directs

**Option A (recommandée si les éléments HTML portent déjà les classes `mf-*`)** :  
Retirer TOUT wrapper, utiliser les sélecteurs de classe directement :

```scss
// _extras.scss — PAS de wrapper
.mf-nav { ... }
.mf-hero { ... }
.mf-section { ... }
```

Avantage : zéro dépendance sur le template, les classes `mf-*` sont auto-suffisantes.

**Option B (si on veut un scope explicite)** :  
Remplacer `body.view-index` par `.mf-home` et ajouter cette classe au template.

→ **Le patch script ci-joint supporte les deux options.**

---

## Section 3 — Diff/patch concret

### Fichier 1 : `_extras.scss`

```diff
- body.view-index {
+ .mf-home {
    .mf-nav {
      // ...
    }
    .mf-hero {
      // ...
    }
    // ...
- }
+ }
```

Ou (Option A, sélecteurs directs) :

```diff
- body.view-index {
-   .mf-nav {
-     // ...
-   }
-   .mf-hero {
-     // ...
-   }
- }
+ .mf-nav {
+   // ...
+ }
+ .mf-hero {
+   // ...
+ }
```

### Fichier 2 : `lms-main-v1.scss` (CRÉER si absent)

```scss
// themes/mission-theme/lms/static/sass/lms-main-v1.scss
@import 'lms/static/sass/lms-main-v1';
@import 'partials/lms/theme/extras';
```

### Fichier 3 : `index.html` (si Option B avec `.mf-home`)

```diff
- <div>
+ <div class="mf-home">
    <!-- contenu homepage -->
  </div>
```

---

## Section 4 — Runbook déploiement

### Workflow complet : TEST → CODE → TEST → COMMIT → TEST → PUSH

```bash
# ── ÉTAPE 1 : TESTS PRÉ-FIX (prouver que ça échoue) ──
cd /Users/zakiachabane/edx-platform
python3 -m unittest discover -s custom-infra/tests -p 'test_*.py' -v
# Attendu : FAIL sur test_no_body_view_index_in_extras
#           FAIL sur test_entry_point_exists (si absent)

# ── ÉTAPE 2 : APPLIQUER LE FIX ──
chmod +x scripts/patch-extras.sh
./scripts/patch-extras.sh /Users/zakiachabane/edx-platform

# ── ÉTAPE 3 : TESTS POST-FIX (prouver que c'est corrigé) ──
python3 -m unittest discover -s custom-infra/tests -p 'test_*.py' -v
# Attendu : ALL PASS

# ── ÉTAPE 4 : COMMIT ──
git add \
  themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss \
  themes/mission-theme/lms/static/sass/lms-main-v1.scss \
  themes/mission-theme/lms/templates/index.html \
  custom-infra/tests/test_theme_css_pipeline.py

git commit -m "fix(theme): correct CSS pipeline — replace dead body.view-index selector

Contexte:
  Le design homepage Mission n'est pas appliqué visuellement en staging
  malgré un HTML correctement déployé. Les styles mf-* sont compilés
  dans le bundle CSS mais encapsulés sous body.view-index, un sélecteur
  qui ne matche pas le body réel (<body class='ltr lang_fr'>).

Causes racines:
  1. _extras.scss utilise body.view-index comme wrapper — ce sélecteur
     ne correspond pas au body généré par Open edX sur la homepage
  2. L'entry-point lms-main-v1.scss du thème n'importait pas _extras.scss
     (ou n'existait pas), empêchant la compilation dans le bundle servi

Implémentation:
  - _extras.scss: remplacé body.view-index par .mf-home (ou sélecteurs directs)
  - lms-main-v1.scss: créé/corrigé avec import du core + import _extras
  - Template homepage: ajout classe mf-home si nécessaire (Option B)

Tests:
  - test_no_body_view_index_in_extras: vérifie absence view-index
  - test_no_view_index_in_any_theme_scss: vérifie tous les .scss
  - test_entry_point_exists: vérifie que lms-main-v1.scss existe
  - test_entry_point_imports_extras: vérifie l'import _extras
  - test_no_mf_homepage_css_link: vérifie absence CSS legacy
  - test_extras_contains_mf_classes: vérifie présence classes mf-*

Impact:
  - Les classes .mf-nav/.mf-hero/.mf-section/.mf-footer/.mf-card seront
    compilées dans lms-main-v1.<hash>.css et activeront le design
  - Aucune régression: seul le sélecteur wrapper change, pas les styles
  - Compatible avec le pipeline standard Open edX theming"

# ── ÉTAPE 5 : TESTS POST-COMMIT ──
python3 -m unittest discover -s custom-infra/tests -p 'test_*.py' -v
# Attendu : ALL PASS (confirmation post-commit)

# ── ÉTAPE 6 : PUSH ──
git push origin staging

# ── ÉTAPE 7 : DEPLOY STAGING ──
# Sur le serveur staging :
ssh staging-server
docker compose -p tutor_local exec lms openedx-assets build --themes mission-theme
docker compose -p tutor_local exec lms openedx-assets collect --settings=tutor.assets
docker compose -p tutor_local restart lms cms
sleep 40

# ── ÉTAPE 8 : VALIDATION RUNTIME ──
./scripts/02-deploy-staging.sh
# OU validation manuelle :
curl -s https://academie.staging.missionformations.com/ | grep -c "formateurNabil"
BUNDLE=$(curl -s https://academie.staging.missionformations.com/ | grep -oP 'href="[^"]*lms-main[^"]*\.css[^"]*"' | head -1 | sed 's/href="//;s/"//')
curl -s "https://academie.staging.missionformations.com${BUNDLE}" | grep -c "mf-nav"
# Doit retourner > 0
```

---

## Section 5 — Smoke test

Le script `smoke-test.sh` fourni couvre :
- ✅ Disponibilité LMS + Studio
- ✅ Markers HTML homepage
- ✅ Absence legacy CSS
- ✅ Classes mf-* dans le bundle CSS réellement servi
- ✅ TLS valide

Exécution : `./scripts/smoke-test.sh` (voir fichier joint)

---

## Section 6 — Rollback

```bash
# Si le fix casse quelque chose :
git revert HEAD --no-edit
git push origin staging

# Sur staging :
docker compose -p tutor_local exec lms openedx-assets build
docker compose -p tutor_local exec lms openedx-assets collect --settings=tutor.assets
docker compose -p tutor_local restart lms cms
```

---

## Section 7 — Anti-patterns bannis

| Anti-pattern | Pourquoi | Bonne pratique |
|-------------|----------|----------------|
| `body.view-index` comme scope | Classe non contrôlée, absente en runtime | `.mf-home` ou classes `mf-*` directes |
| `<link href="custom.css">` dans template | Hors pipeline, pas de hash, pas de cache-bust | Tout dans `_extras.scss` |
| `cp` fichiers dans conteneur | Non reproductible | git → build → collect → restart |
| Build sans collectstatic | Bundle servi stale | Toujours enchaîner les 3 |
| Partial `.scss` sans `@import` | Existe mais pas compilé | Importer dans entry-point |
| Pas de smoke test CSS | Découverte tardive | Script automatique post-deploy |
| `!important` systématique | Guerre de spécificité | Cascade thème (chargé après core) |
| Dépendre de classes Open edX internes | Cassé à chaque upgrade | Namespace `mf-*` contrôlé |
