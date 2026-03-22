# Projet OpenEdX — Mission Formations

## Stack technique
- OpenEdX Tutor v21.0.1 sur Ubuntu 22.04
- Docker + Docker Compose
- OVH VPS (8 vCPU / 16 Go RAM)
- Staging: academie.staging.missionformations.com

## Architecture custom
- Theme: themes/mission-theme/ (Mako + CSS + JS)
- Plugin: lms/djangoapps/mission_central_admin/
- Templates Mako: utiliser <%page args="var=default"/> (PAS locals().get())
- Deploy: ./deploy.sh staging (inclut docker cp + cache Mako + collectstatic)
- Tests: pytest tests/unit/ -m unit (151+ tests)
- Diagnostic: python3 tests/diagnose.py

## Cahier des charges (academie multi-academies)
- Sprint 1: TERMINE (11 orgs, discovery, credentials, SSL wildcard)
- Sprint 2: TERMINE (Academy Manager — modeles, vues, templates)
- Sprint 3: TERMINE (Dashboard connecte aux donnees reelles)
- Sprint 4: A FAIRE (Pages publiques, portail B2B, middleware sous-domaine)
- Sprint 5: A FAIRE (Contenu, tests utilisateurs, prod)

## Regles IMPERATIVES (ne jamais enfreindre)

### Deploy et collectstatic
- Ne JAMAIS utiliser collectstatic --clear (supprime webpack-stats.json → 500)
- Toujours faire docker cp apres git pull (disque != container)
- Toujours vider le cache Mako apres deploy (find /tmp -name "*.mako.py" -delete)
- Secrets via os.environ.get(), jamais en dur

### Tutor config — CRITIQUE
- Ne JAMAIS faire `tutor config save` sans backup des settings AVANT
- Backup obligatoire : `ssh staging-openedx "cp ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py /tmp/production.py.backup"`
- Apres chaque `tutor config save` : diff les settings pour verifier ce qui a change
- CHAQUE setting custom DOIT etre dans un plugin Tutor (sinon ecrase au prochain config save)
- Ne JAMAIS installer un plugin Tutor (`tutor plugins enable`, `tutor local launch`) sans :
  1. Backup des settings
  2. Test des cours apres
  3. Diff des settings avant/apres

### Templates globaux — CRITIQUE
- body-extra.html, header.html, footer.html = templates charges sur TOUTES les pages
- Une erreur dans ces fichiers = 500 sur TOUT le site
- Toujours tester une page dans les 30 secondes apres un deploy de ces fichiers
- Toujours verifier les imports de namespace Mako (<%namespace name='static' file='static_content.html'/>)

### CSS et SCSS — OBLIGATOIRE
- Toujours utiliser le pipeline SCSS existant (partial dans partials/lms/theme/)
- Ne JAMAIS mettre de CSS inline dans un template Mako
- Ne JAMAIS creer de fichier CSS separe qui depend de static.url() (pas collecte)
- Pattern : creer _monfichier.scss → importer dans lms-main-v1.scss → compiler via npm run compile-sass

### Variables OpenEdX — OBLIGATOIRE
- Avant de modifier une variable de settings, LIRE LE CODE SOURCE qui l'utilise
- grep la variable dans le codebase pour comprendre comment elle est utilisee
- Ne JAMAIS deviner ce qu'une variable fait — lire le code

### Verification post-deploy — OBLIGATOIRE
Apres chaque deploy, verifier dans cet ordre :
1. Homepage : https://academie.staging.missionformations.com/
2. Login : /login
3. Dashboard : /dashboard
4. Un cours : /courses/course-v1:MissionFormations+MF-VTC-2025+2025/course/
5. Dashboard admin : /admin/mission-dashboard/
6. Chat WeWill : widget en bas a droite
Si un de ces tests echoue, rollback AVANT de continuer.

### Rollback
- Tag git avant chaque deploy : `git tag pre-deploy-$(date +%Y%m%d-%H%M)`
- Si un deploy casse le staging : `git checkout <tag>` + redeploy
- Garder le backup des settings serveur pendant 7 jours minimum

### Plugins Tutor OBLIGATOIRES (ne jamais desinstaller)
Ces plugins doivent TOUJOURS etre installes et actives sur le serveur :
- tutor-mfe (MFEs : Learning, Account, Discussions, etc.) — SANS LUI LES COURS NE FONCTIONNENT PAS
- tutor-forum (forum de discussion)
- Tous les plugins mission_* custom

Avant d'installer un nouveau plugin (`pip install tutor-xxx`) :
1. Lister les plugins actifs : `tutor plugins list`
2. Lister les packages installes : `pip list | grep tutor`
3. Apres l'install, VERIFIER que les plugins existants sont toujours la
4. Si un plugin a disparu : le reinstaller immediatement

### Settings qui DOIVENT etre dans les plugins Tutor
Ces variables sont ecrasees par `tutor config save` si elles ne sont pas dans un plugin :
- LEARNING_MICROFRONTEND_URL → mission_theme_lock.py
- MFE_CONFIG → tutor-mfe (plugin natif)
- ENABLE_MFE_CONFIG_API → tutor-mfe
- FEATURES['CERTIFICATES_HTML_VIEW'] → mission_certificates_policy.py
- FEATURES['CUSTOM_CERTIFICATE_TEMPLATES_ENABLED'] → mission_certificates_policy.py
- FEATURES['ENABLE_DISCUSSION_SERVICE'] → tutor-forum (plugin)
- MF_CERTIFICATES_MENU_ONLY_OBTAINED → mission_certificates_policy.py
- DEFAULT_SITE_THEME → mission_theme_lock.py
- FEATURES['ENABLE_AUTHN_MICROFRONTEND'] → mission_theme_lock.py
