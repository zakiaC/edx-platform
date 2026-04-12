# Guide Plugins Tutor — Mission Formations

## Comment ca marche

Les plugins Tutor sont des fichiers Python dans /root/.local/share/tutor-plugins/ sur le VPS.
Ils injectent des settings dans les fichiers generes par Tutor via des "patches".
Chaque plugin a une responsabilite unique.

## Plugins actifs

| Plugin | Role | Fichier source |
|--------|------|---------------|
| mission_theme_lock | Auth flow + theme par defaut + suppression logo OpenEdX | tutor_plugins/mission_theme_lock.py |
| mission_mfe_branding | Branding MFE : slogan, footer, suppression texte edX | tutor_plugins/mission_mfe_branding.py |
| mission_central_admin | Dashboard admin central | tutor_plugins/mission_central_admin.py |
| mission_multi_tenant | eox-tenant routing multi-academies | tutor_plugins/mission_multi_tenant.py |
| mission_certificates_policy | Certificats menu policy | tutor_plugins/mission_certificates_policy.py |
| mission_braze_enrollment | Braze email config | tutor_plugins/mission_braze_enrollment.py |
| mission_csp_report_only | CSP report-only headers | tutor_plugins/mission_csp_report_only.py |
| mission_theme_assets | Assets theme statiques | tutor_plugins/mission_theme_assets.py |
| mission_wewill | WeWill chat widget | tutor_plugins/mission_wewill.py |
| indigo | Footer MFE custom (supporte INDIGO_FOOTER_SLOGAN etc.) | pip install tutor-indigo |

## Comment deployer un nouveau plugin

1. Creer le fichier dans tutor_plugins/ (repo local)
2. git commit + git push origin staging
3. Sur le VPS :
   - cd /root/edx-platform && git pull origin staging --rebase
   - cp tutor_plugins/MON_PLUGIN.py /root/.local/share/tutor-plugins/
   - tutor plugins enable MON_PLUGIN
   - tutor config save
   - tutor local restart lms (ou cms selon le plugin)

## Comment modifier un plugin existant

1. Modifier le fichier dans tutor_plugins/ (repo local)
2. git commit + git push origin staging
3. Sur le VPS :
   - cd /root/edx-platform && git pull origin staging --rebase
   - cp tutor_plugins/MON_PLUGIN.py /root/.local/share/tutor-plugins/
   - tutor config save
   - tutor local restart lms

## ATTENTION — Regles critiques

- Le chemin VPS des plugins est /root/.local/share/tutor-plugins/ (PAS tutor_plugins/ du repo)
- Apres chaque tutor config save, verifier que les settings n'ont pas ete ecrases
- Ne JAMAIS faire tutor images build openedx sans verifier OPENEDX_EXTRA_PIP_REQUIREMENTS
- tutor images build --no-cache mfe est necessaire si on modifie le footer/header MFE structurellement

## Architecture MFE vs Mako

- LMS (homepage, catalogue, dashboard) = templates Mako → theme dans /openedx/themes/mission-theme/lms/
- Studio + pages cours = MFE React → config via MFE_CONFIG (API /api/mfe_config/v1)
- Le footer/header MFE = composant React @edx/frontend-component-footer
- Le plugin indigo remplace ce footer par un footer custom qui lit INDIGO_FOOTER_SLOGAN etc.
- Sans indigo, les variables INDIGO_* sont ignorees par le footer par defaut

## Verification rapide

Pour verifier que les settings MFE sont actifs :
```
docker exec tutor_local-lms-1 python -c "import django,os;os.environ['DJANGO_SETTINGS_MODULE']='lms.envs.tutor.production';django.setup();from django.conf import settings;print(settings.MFE_CONFIG.get('INDIGO_FOOTER_SLOGAN','PAS DEFINI'))"
```

Pour verifier ce que l'API retourne aux MFEs :
```
curl -s https://academie.staging.missionformations.com/api/mfe_config/v1 | python3 -m json.tool | grep -i "slogan\|powered\|logo"
```
