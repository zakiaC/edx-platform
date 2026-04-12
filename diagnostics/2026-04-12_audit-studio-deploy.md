# Audit Studio & Deploiement — 2026-04-12

## Contexte
Tentative de customisation du header/footer Studio (CMS) qui a echoue.
Plusieurs regressions en cascade : perte du theme LMS, crash eox-tenant, modifications invisibles.

## Diagnostic principal
Le Studio utilise le MFE course-authoring (React app sur apps.academie.staging.missionformations.com).
Les templates Mako (header.html, footer.html) ne sont jamais rendus — bypasses par le MFE.
Toutes les modifications Mako etaient invisibles pour cette raison.

## Problemes critiques identifies

### 1. URLs staging hardcodees (BLOQUANT prod)
- tutor-patches/lms-production.py : 15+ URLs en dur
- tutor_plugins/mission_multi_tenant.py : 9 sous-domaines hardcodes
- Solution : passer par tutor config et variables d'environnement

### 2. Duplication settings patch vs plugin
- DEFAULT_SITE_THEME, ENABLE_AUTHN_MICROFRONTEND, LEARNING_MICROFRONTEND_URL
  definis dans le patch ET dans le plugin Tutor
- Solution : garder uniquement dans les plugins Tutor

### 3. deploy.sh ne gerait que le LMS
- Aucune etape pour le CMS/Studio
- Corrige ce jour : ajout etapes 6-8 pour CMS (sync, collectstatic, restart)

### 4. Dossiers imbriques en boucle
- mission-theme/mission-theme/mission-theme/... (9 niveaux dans le container)
- Cause : docker cp repetes mal cibles
- Solution : nettoyer dans le container, corriger le docker cp

### 5. eox-tenant fragile
- Se perdait a chaque rebuild d'image Docker
- Corrige ce jour : ajoute dans OPENEDX_EXTRA_PIP_REQUIREMENTS

### 6. Secrets dans le repo
- tutor-patches/.secrets.env contient cles privees RSA, API keys
- Protege par .gitignore mais risque si git add -f
- Solution : secrets manager ou variables d'env serveur uniquement

## Etat des fichiers theme CMS

### Presents dans le container (/openedx/themes/mission-theme/cms/)
- templates/widgets/header.html (modifie : logo 42px + lien missionformations.com)
- templates/widgets/footer.html (modifie : logo image + slogan)
- templates/widgets/user_dropdown.html
- templates/widgets/sock_links.html
- templates/widgets/sock_links_extra.html
- static/images/studio-logo.png

### SiteTheme en base de donnees
- academie.staging.missionformations.com -> mission-theme
- studio.staging.missionformations.com -> mission-theme
- COMPREHENSIVE_THEME_DIRS: ['/openedx/themes']
- DEFAULT_SITE_THEME: mission-theme

### Conclusion : theme correctement configure mais MFE bypass les templates

## Process de deploiement actuel

### LMS (fonctionne)
git commit > git push > ssh VPS > git pull > ./deploy.sh staging
deploy.sh gere : docker cp, compile-sass, collectstatic, force-copy CSS, cache Mako, restart, smoke tests

### CMS/Studio (a corriger)
Le MFE rend toute l'interface Studio.
Templates Mako non utilises.
Customisation = modifier le MFE (build React) ou le desactiver.

## Decision a prendre
- Option A : Garder le MFE et le customiser (build React)
- Option B : Desactiver le MFE Studio et utiliser les templates Mako

## Actions correctives effectuees ce jour
1. eox-tenant ajoute dans OPENEDX_EXTRA_PIP_REQUIREMENTS
2. deploy.sh mis a jour avec etapes CMS (6-8) + test Studio (smoke)
3. Theme LMS restaure via deploy.sh staging

## Participants
- Zakia (PM)
- Claude (DevOps Mission)
- Allyah (Specialiste OpenEdX)
- Ishaq (Specialiste DevOps)
