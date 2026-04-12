# Process de deploiement — Mission Formations

## Architecture de rendu des pages

### LMS (ce que voit l'etudiant)
- Homepage, catalogue, dashboard : templates Mako (theme dans /openedx/themes/mission-theme/lms/)
- Pages de cours (learning) : MFE learning (apps.academie.staging.missionformations.com/learning)
- Account, profile, discussions : MFEs respectifs

### CMS / Studio (ce que voit le createur de cours)
- TOUTES les pages : MFE course-authoring (apps.academie.staging.missionformations.com/authoring)
- Les templates Mako dans cms/templates/ ne sont PAS utilises quand le MFE est actif
- Le header/footer visible dans Studio = composants React @edx/frontend-component-header et @edx/frontend-component-footer

### Comment customiser chaque couche

| Couche | Methode | Fichiers |
|--------|---------|----------|
| LMS templates Mako | themes/mission-theme/lms/ | deploy.sh staging |
| LMS CSS | SCSS partials + compile-sass | deploy.sh staging |
| MFE logo/favicon | MFE_CONFIG (LOGO_URL, FAVICON_URL) | tutor-patches/lms-production.py |
| MFE couleurs | PARAGON_THEME_URLS ou brand package | plugin Tutor |
| MFE header/footer structure | Brand package (@edx/brand) | rebuild MFE image |
| MFE footer liens | INDIGO_FOOTER_NAV_LINKS dans MFE_CONFIG | tutor-patches/lms-production.py |
| MFE texte "Powered by OpenEdX" | LOGO_POWERED_BY_OPEN_EDX_URL = False | mission_theme_lock.py |
| Multi-tenant branding | eox-tenant TenantConfig.MFE_CONFIG | Django admin |

## Deploiement LMS (./deploy.sh staging)

Depuis la machine locale :
```
git commit + git push origin staging
./deploy.sh staging
```

Le script fait :
0. Tag git + backup settings
1. Permissions theme
2. docker cp theme + plugin + patches → container LMS (/openedx/themes/)
3. Compilation Sass
4. Verification CSS
5. Collectstatic LMS + force-copy CSS
6. docker cp theme CMS → container CMS (/openedx/themes/)
7. Collectstatic CMS
8. Vider cache Mako + restart LMS + CMS
9. Commit CSS compiles
10. Smoke tests (homepage, login, catalogue, cours, CSS, Studio)

## Deploiement MFE (branding)

Pour modifier logo, favicon, couleurs, footer du MFE :

### Methode runtime (pas de rebuild)
1. Modifier MFE_CONFIG dans tutor-patches/lms-production.py
2. Sur le VPS : tutor config save && tutor local restart lms

### Methode build (changements structurels header/footer)
1. Modifier le brand package
2. Sur le VPS : tutor images build --no-cache mfe
3. tutor local stop && tutor local start -d

## Chemins dans les containers

| Container | Chemin theme | Chemin SCSS |
|-----------|-------------|-------------|
| tutor_local-lms-1 | /openedx/themes/mission-theme/ | /openedx/themes/mission-theme/lms/static/sass/ |
| tutor_local-cms-1 | /openedx/themes/mission-theme/ | /openedx/themes/mission-theme/cms/static/sass/ |

ATTENTION : le chemin est /openedx/themes/ PAS /openedx/edx-platform/themes/

## Verification post-deploy

1. Homepage LMS : https://academie.staging.missionformations.com/
2. Login : /login
3. Dashboard : /dashboard
4. Cours : /courses/course-v1:MissionFormations+MF-VTC-2025+2025/course/
5. Studio home : https://studio.staging.missionformations.com/
6. Studio cours : ouvrir un cours dans Studio
7. Chat WeWill : widget en bas a droite

## Rollback

```
git checkout $(git tag | grep pre-deploy | tail -1)
./deploy.sh staging
```

## Regles imperatives

- JAMAIS collectstatic --clear
- JAMAIS tutor images build openedx sans verifier OPENEDX_EXTRA_PIP_REQUIREMENTS
- JAMAIS tutor config save sans backup settings AVANT
- TOUJOURS docker cp vers /openedx/themes/ (pas /openedx/edx-platform/themes/)
- TOUJOURS vider le cache Mako apres modification de templates
- TOUJOURS tester les pages dans les 30 secondes apres deploy
