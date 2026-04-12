# PROCESS DE DEPLOIEMENT — Mission Formations

## 3 types de modifications, 3 process differents

---

## TYPE 1 : Modification LMS (templates Mako, CSS, plugin Django)

Fichiers concernes :
- themes/mission-theme/lms/ (templates, SCSS, CSS, JS, images)
- lms/djangoapps/mission_central_admin/ (plugin Django)

### Process :

```
MACHINE LOCALE
1. Modifier les fichiers
2. git add <fichiers modifies>
3. git commit -m "description claire"
4. git push origin staging

5. ./deploy.sh staging
```

Le deploy.sh fait tout automatiquement :
- Tag git de securite
- Backup settings serveur
- docker cp theme + plugin → container LMS
- Compilation Sass
- Collectstatic (JAMAIS --clear)
- Force-copy CSS
- docker cp theme → container CMS
- Collectstatic CMS
- Vider cache Mako
- Restart LMS + CMS
- Smoke tests automatiques

### Verification :
- Homepage : https://academie.staging.missionformations.com/
- Login : /login
- Dashboard : /dashboard
- Cours : /courses/course-v1:MissionFormations+MF-VTC-2025+2025/course/

---

## TYPE 2 : Modification MFE (logo, footer, couleurs, slogan)

Fichiers concernes :
- tutor_plugins/mission_mfe_branding.py (slogan, footer links, texte edX)
- tutor_plugins/mission_theme_lock.py (logo powered by, auth flow)

### Process :

```
MACHINE LOCALE
1. Modifier le plugin dans tutor_plugins/
2. git add tutor_plugins/MON_PLUGIN.py
3. git commit -m "description claire"
4. git push origin staging

VPS (ssh root@academie.staging.missionformations.com)
5. cd /root/edx-platform
6. git stash && git pull origin staging --rebase
7. cp tutor_plugins/MON_PLUGIN.py /root/.local/share/tutor-plugins/
8. tutor config save
9. tutor local restart lms

VERIFICATION
10. curl -s https://academie.staging.missionformations.com/api/mfe_config/v1 | python3 -m json.tool | grep "MA_VARIABLE"
11. Ctrl+Shift+R sur le navigateur
```

### ATTENTION :
- Apres tutor config save, TOUJOURS verifier que les settings n'ont pas ete ecrases
- Les variables INDIGO_* necessitent le plugin tutor-indigo installe

---

## TYPE 3 : Modification structurelle MFE (header/footer React, nouveau composant)

Fichiers concernes :
- Brand package ou fork des composants React MFE

### Process :

```
VPS (ssh root@academie.staging.missionformations.com)
1. pip install tutor-PLUGIN (si nouveau plugin)
2. tutor plugins enable PLUGIN
3. tutor config save

BACKUP OBLIGATOIRE AVANT BUILD
4. tutor plugins list > /tmp/plugins-backup.txt
5. pip list | grep tutor > /tmp/tutor-packages-backup.txt

BUILD
6. tutor images build --no-cache mfe

DEPLOIEMENT
7. tutor local stop
8. tutor local start -d

VERIFICATION
9. Verifier LMS : https://academie.staging.missionformations.com/
10. Verifier Studio : https://studio.staging.missionformations.com/
11. Verifier un cours
12. tutor plugins list | grep mission (tous les plugins toujours la ?)
```

### ATTENTION :
- Le build MFE prend 20-30 minutes
- Ne JAMAIS faire tutor images build openedx sans verifier OPENEDX_EXTRA_PIP_REQUIREMENTS=["eox-tenant"]
- Apres le build, TOUJOURS verifier que les plugins mission sont toujours actifs

---

## ROLLBACK

Si une modification casse le site :

```
MACHINE LOCALE
1. git checkout $(git tag | grep pre-deploy | tail -1)
2. ./deploy.sh staging
```

Si c'est un probleme de plugin Tutor :
```
VPS
1. tutor plugins disable PLUGIN_PROBLEMATIQUE
2. tutor config save
3. tutor local restart lms
```

---

## REGLES IMPERATIVES

1. JAMAIS collectstatic --clear (supprime webpack-stats.json → 500)
2. JAMAIS tutor config save sans backup settings AVANT
3. JAMAIS tutor images build openedx sans OPENEDX_EXTRA_PIP_REQUIREMENTS
4. TOUJOURS docker cp vers /openedx/themes/ (PAS /openedx/edx-platform/themes/)
5. TOUJOURS vider le cache Mako apres modif templates
6. TOUJOURS tester dans les 30 secondes apres deploy
7. TOUJOURS commiter avec un message clair decrivant la modification
8. TOUJOURS verifier les plugins actifs apres un build d'image

---

## DIAGNOSTIC RAPIDE

### Les settings MFE sont-ils actifs ?
```
docker exec tutor_local-lms-1 python -c "import django,os;os.environ['DJANGO_SETTINGS_MODULE']='lms.envs.tutor.production';django.setup();from django.conf import settings;print(settings.MFE_CONFIG)"
```

### L'API MFE retourne-t-elle les bonnes valeurs ?
```
curl -s https://academie.staging.missionformations.com/api/mfe_config/v1 | python3 -m json.tool
```

### Le theme est-il assigne ?
```
tutor local do settheme mission-theme
```

### Les plugins sont-ils actifs ?
```
tutor plugins list | grep mission
```

### Les containers tournent-ils ?
```
docker ps --format "{{.Names}} {{.Status}}" | grep tutor
```

### Logs d'erreur ?
```
docker logs tutor_local-lms-1 --tail 30
docker logs tutor_local-cms-1 --tail 30
docker logs tutor_local-mfe-1 --tail 30
```

---

## CONTACTS

- Zakia : PM
- Allyah : Specialiste OpenEdX
- Ishaq : Specialiste DevOps
- Claude : DevOps Mission
