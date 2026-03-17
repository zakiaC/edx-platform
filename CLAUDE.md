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

## Regles importantes
- Ne JAMAIS utiliser collectstatic --clear (supprime webpack-stats.json → 500)
- Toujours faire docker cp apres git pull (disque != container)
- Toujours vider le cache Mako apres deploy (find /tmp -name "*.mako.py" -delete)
- Ne pas toucher config.yml de production sans backup
- Secrets via os.environ.get(), jamais en dur
