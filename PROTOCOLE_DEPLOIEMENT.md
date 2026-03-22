# PROTOCOLE DE DEPLOIEMENT — Mission Formations

> CE DOCUMENT EST OBLIGATOIRE. Aucune modification du staging ou de la prod
> ne doit etre faite sans suivre ce protocole. Pas d'exception.
> Applicable a tout intervenant : humain ou IA.

---

## REGLE ZERO

**Ne JAMAIS modifier le serveur staging ou prod en direct pendant une session de developpement.**

Toute modification suit le cycle :
```
Local → Test local → Commit → Deploy staging → Validation → Merge main → Deploy prod
```

Pas de raccourci. Pas de "je fais vite fait en SSH". Pas de "je teste directement sur staging".

---

## 1. AVANT TOUTE MODIFICATION

### 1.1 Checklist pre-modification

Avant de commencer a coder ou modifier quoi que ce soit, repondre a ces questions :

| Question | Reponse obligatoire |
|----------|-------------------|
| Qu'est-ce que je modifie exactement ? | Nommer les fichiers concernes |
| Quel est l'impact potentiel ? | Local (1 page) / Global (toutes les pages) / Infra (tout le serveur) |
| Est-ce reversible facilement ? | Oui (edit de fichier) / Non (install plugin, migration DB, tutor config save) |
| Ai-je un backup ? | Si non, en faire un AVANT de continuer |
| Ai-je lu le code source des fonctions impactees ? | Si non, le lire AVANT de modifier |

### 1.2 Classification des modifications

| Niveau | Type | Exemples | Procedure |
|--------|------|----------|-----------|
| **VERT** | Modification de contenu/style | CSS, texte template, image | Modifier → tester local → deployer |
| **ORANGE** | Modification de logique | Vue Python, URL, middleware, signal | Modifier → tester local → review → deployer |
| **ROUGE** | Modification d'infrastructure | Plugin Tutor, tutor config save, pip install, migration DB, Docker | **STOP — Suivre la procedure ROUGE ci-dessous** |

### 1.3 Procedure pour les modifications ROUGES

Les modifications ROUGES sont les plus dangereuses. Elles peuvent casser tout le serveur.

**AVANT :**
```bash
# 1. Lister les plugins actifs
ssh staging-openedx "tutor plugins list"

# 2. Lister les packages Python installes
ssh staging-openedx "pip list | grep tutor"

# 3. Sauvegarder les settings
ssh staging-openedx "cp ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py /tmp/production.py.backup-$(date +%Y%m%d-%H%M)"

# 4. Sauvegarder le Caddyfile
ssh staging-openedx "docker exec tutor_local-caddy-1 cat /etc/caddy/Caddyfile > /tmp/Caddyfile.backup-$(date +%Y%m%d-%H%M)"

# 5. Sauvegarder la liste des containers
ssh staging-openedx "docker ps --format '{{.Names}} {{.Image}} {{.Status}}' > /tmp/containers.backup-$(date +%Y%m%d-%H%M)"

# 6. Tag git
git tag "pre-change-$(date +%Y%m%d-%H%M%S)"
```

**APRES :**
```bash
# 1. Diff les settings
ssh staging-openedx "diff /tmp/production.py.backup-* ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py"

# 2. Verifier que tous les plugins sont toujours la
ssh staging-openedx "tutor plugins list"

# 3. Verifier que tous les containers tournent
ssh staging-openedx "docker ps --format '{{.Names}} {{.Status}}'"

# 4. Executer les tests de validation (section 3)
```

---

## 2. PIPELINE DE DEPLOIEMENT

### 2.1 Modifications de code (VERT / ORANGE)

```
ETAPE 1 — Modifier le code en local
  │  Editer les fichiers dans le repo local
  │  Ne PAS toucher au serveur
  ▼
ETAPE 2 — Tester en local (si possible)
  │  Ouvrir le fichier HTML dans le navigateur (templates statiques)
  │  Verifier la syntaxe Mako (namespaces, variables)
  │  Verifier la syntaxe SCSS (compilation)
  │  Verifier la syntaxe Python (import, indentation)
  ▼
ETAPE 3 — Commit avec message conventionnel
  │  git add <fichiers specifiques>   ← PAS git add .
  │  git commit -m "feat/fix/docs: description"
  ▼
ETAPE 4 — Deployer sur staging
  │  ./deploy.sh staging
  │  Le script fait automatiquement :
  │    - Tag pre-deploy
  │    - Backup settings
  │    - Sync code
  │    - Compile Sass
  │    - Collectstatic
  │    - Clear cache
  │    - Restart
  │    - Smoke tests
  ▼
ETAPE 5 — Validation manuelle (section 3)
  │  Ouvrir le staging dans le navigateur
  │  Verifier les 6 URLs critiques
  │  Si regression → rollback immediat
  ▼
ETAPE 6 — Confirmer
  │  Si tout est OK → passer a la modification suivante
  │  Si regression → rollback + analyser + corriger en local
```

### 2.2 Modifications d'infrastructure (ROUGE)

```
ETAPE 1 — Documenter l'intention
  │  Ecrire : "Je vais installer le plugin X parce que Y"
  │  Lister les impacts potentiels
  ▼
ETAPE 2 — Rechercher
  │  Lire la documentation du plugin/package
  │  Chercher les issues connues sur GitHub
  │  Verifier la compatibilite avec la version de Tutor (21.0.x)
  ▼
ETAPE 3 — Backup complet (procedure 1.3)
  │  Settings, plugins, containers, Caddyfile, tag git
  ▼
ETAPE 4 — Executer la modification
  │  pip install / tutor plugins enable / tutor config save
  ▼
ETAPE 5 — Verifier les effets de bord
  │  Diff settings (OBLIGATOIRE)
  │  Verifier plugins toujours presents (OBLIGATOIRE)
  │  Verifier containers toujours la (OBLIGATOIRE)
  ▼
ETAPE 6 — Restart et validation
  │  tutor local restart lms
  │  Smoke tests (section 3)
  ▼
ETAPE 7 — Si regression
  │  ROLLBACK IMMEDIAT :
  │  ssh staging-openedx "cp /tmp/production.py.backup-* ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py"
  │  ssh staging-openedx "tutor local restart lms"
  │  Analyser la cause AVANT de retenter
```

---

## 3. TESTS DE VALIDATION OBLIGATOIRES

### 3.1 Smoke tests (apres chaque deploy)

Ces 6 tests doivent TOUS passer. Si un seul echoue, c'est un rollback.

| # | Test | URL | Attendu |
|---|------|-----|---------|
| 1 | Homepage | https://academie.staging.missionformations.com/ | 200, page MF affichee |
| 2 | Login | https://academie.staging.missionformations.com/login | 200, formulaire de connexion |
| 3 | Catalogue | https://academie.staging.missionformations.com/catalogue/ | 200, liste des formations |
| 4 | Cours about | https://academie.staging.missionformations.com/courses/course-v1:MissionFormations+MF-VTC-2025+2025/about | 200, page du cours |
| 5 | Dashboard (connecte) | https://academie.staging.missionformations.com/dashboard | 200 ou redirect login |
| 6 | Cours (connecte) | https://academie.staging.missionformations.com/courses/course-v1:MissionFormations+MF-VTC-2025+2025/course/ | 200 ou redirect vers MFE Learning |

### 3.2 Verification des services

```bash
# Tous les containers doivent etre "Up"
ssh staging-openedx "docker ps --format '{{.Names}} {{.Status}}' | grep -v 'Up' | grep -v 'Exited (0)'"
# Si cette commande retourne quelque chose → probleme

# Services obligatoires :
# tutor_local-lms-1        Up
# tutor_local-cms-1        Up
# tutor_local-mysql-1      Up
# tutor_local-mongodb-1    Up
# tutor_local-redis-1      Up
# tutor_local-caddy-1      Up
# tutor_local-mfe-1        Up    ← CRITIQUE — sans lui les cours ne marchent pas
# tutor_local-lms-worker-1 Up
# tutor_local-cms-worker-1 Up
```

### 3.3 Verification des settings critiques

```bash
ssh staging-openedx "docker exec tutor_local-lms-1 python -c \"
from django.conf import settings
checks = {
    'LEARNING_MICROFRONTEND_URL': settings.LEARNING_MICROFRONTEND_URL,
    'ENABLE_MFE_CONFIG_API': settings.ENABLE_MFE_CONFIG_API,
    'DEFAULT_SITE_THEME': settings.DEFAULT_SITE_THEME,
    'CERTIFICATES_HTML_VIEW': settings.FEATURES.get('CERTIFICATES_HTML_VIEW'),
    'ENABLE_DISCUSSION_SERVICE': settings.FEATURES.get('ENABLE_DISCUSSION_SERVICE'),
}
for k, v in checks.items():
    status = 'OK' if v else 'MISSING'
    print(f'{status}: {k} = {v}')
\" 2>/dev/null"
```

Valeurs attendues :
| Setting | Valeur attendue |
|---------|----------------|
| LEARNING_MICROFRONTEND_URL | https://apps.academie.staging.missionformations.com/learning |
| ENABLE_MFE_CONFIG_API | True |
| DEFAULT_SITE_THEME | mission-theme |
| CERTIFICATES_HTML_VIEW | True |
| ENABLE_DISCUSSION_SERVICE | True |

---

## 4. PROCEDURE DE ROLLBACK

### 4.1 Rollback code (modification VERT/ORANGE)

```bash
# Trouver le dernier tag pre-deploy
git tag | grep pre-deploy | tail -1

# Revenir au code stable
git checkout <tag>

# Redeployer
./deploy.sh staging
```

### 4.2 Rollback settings (modification ROUGE)

```bash
# Restaurer les settings sauvegardes
ssh staging-openedx "cp /tmp/production.py.backup-YYYYMMDD-HHMM ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py"

# Restart LMS
ssh staging-openedx "tutor local restart lms"

# Verifier
# → Executer les smoke tests (section 3)
```

### 4.3 Rollback complet (tout est casse)

```bash
# 1. Arreter tout
ssh staging-openedx "tutor local stop"

# 2. Restaurer le Caddyfile
ssh staging-openedx "docker cp /tmp/Caddyfile.backup-YYYYMMDD-HHMM tutor_local-caddy-1:/etc/caddy/Caddyfile"

# 3. Restaurer les settings
ssh staging-openedx "cp /tmp/production.py.backup-YYYYMMDD-HHMM ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py"

# 4. Redemarrer
ssh staging-openedx "tutor local start -d"

# 5. Verifier
# → Executer les smoke tests (section 3)
```

---

## 5. REGLES POUR LES TEMPLATES MAKO

### 5.1 Templates globaux (DANGER)

Ces fichiers sont charges sur TOUTES les pages du LMS.
Une erreur dedans = 500 sur TOUT le site.

| Fichier | Impact |
|---------|--------|
| body-extra.html | Toutes les pages |
| header/header.html | Toutes les pages |
| footer.html | Toutes les pages |
| main.html | Toutes les pages |

**Regles :**
- Toujours tester en local avant de deployer
- Toujours verifier les imports de namespace : `<%namespace name='static' file='static_content.html'/>`
- Tester une page dans les 30 secondes apres deploy
- Si 500 → rollback IMMEDIAT, analyser ENSUITE

### 5.2 CSS et SCSS

**TOUJOURS utiliser le pipeline SCSS du theme :**

```
1. Creer le fichier : themes/mission-theme/lms/static/sass/partials/lms/theme/_moncomposant.scss
2. Importer dans :    themes/mission-theme/lms/static/sass/lms-main-v1.scss
3. Compiler :         npm run compile-sass -- --skip-default
4. Le CSS est integre dans le CSS principal → servi automatiquement
```

**JAMAIS :**
- De CSS inline dans un template Mako
- De fichier CSS separe charge via `static.url()`
- De `<link>` dans body-extra.html

### 5.3 Variables disponibles dans les templates

Avant d'utiliser une variable dans un template, verifier qu'elle existe dans le contexte.
Les namespaces ne sont PAS herites automatiquement — chaque template doit importer ce dont il a besoin.

---

## 6. REGLES POUR TUTOR ET LES PLUGINS

### 6.1 Commandes dangereuses

| Commande | Danger | Alternative |
|----------|--------|-------------|
| `tutor config save` | Regenere TOUS les settings depuis les plugins | Backup settings AVANT, diff APRES |
| `tutor local launch` | Fait config save + pull images + restart tout | Ne pas utiliser pour un seul plugin — utiliser `tutor local start -d` |
| `pip install tutor-xxx` | Peut ecraser des packages existants | Verifier `pip list | grep tutor` avant et apres |
| `tutor plugins disable xxx` | Supprime la config du plugin des settings | Backup AVANT |

### 6.2 Plugins obligatoires

Ces plugins doivent TOUJOURS etre installes et actives :

| Plugin | Paquet pip | Role | Sans lui |
|--------|-----------|------|----------|
| **mfe** | tutor-mfe | MFEs (Learning, Account, etc.) | Cours inaccessibles, SSL error sur apps.* |
| **forum** | tutor-forum | Forum de discussion | Discussions desactivees |
| mission_central_admin | (custom) | Dashboard admin | Dashboard admin inaccessible |
| mission_theme_lock | (custom) | Theme + auth | Theme par defaut OpenEdX |
| mission_certificates_policy | (custom) | Certificats HTML | Certificats non rendus |
| mission_csp_report_only | (custom) | Securite CSP | Pas de monitoring CSP |
| mission_wewill | (custom) | Chat WeWill | Chat non route |

### 6.3 Avant d'installer un nouveau plugin

```bash
# 1. Sauvegarder l'etat actuel
ssh staging-openedx "tutor plugins list > /tmp/plugins-before.txt"
ssh staging-openedx "pip list | grep tutor > /tmp/pip-tutor-before.txt"
ssh staging-openedx "cp ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py /tmp/production.py.backup"

# 2. Installer le plugin
ssh staging-openedx "pip install --break-system-packages tutor-xxx"

# 3. Verifier que rien n'a ete ecrase
ssh staging-openedx "pip list | grep tutor > /tmp/pip-tutor-after.txt"
ssh staging-openedx "diff /tmp/pip-tutor-before.txt /tmp/pip-tutor-after.txt"
# Si un paquet a disparu → le reinstaller IMMEDIATEMENT

# 4. Activer et configurer
ssh staging-openedx "tutor plugins enable xxx"
ssh staging-openedx "tutor config save"

# 5. Diff settings
ssh staging-openedx "diff /tmp/production.py.backup ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py"
# Lire le diff ATTENTIVEMENT avant de continuer

# 6. Restart et tester
ssh staging-openedx "tutor local start -d"
# → Executer les smoke tests (section 3)
```

---

## 7. REGLES POUR LES SESSIONS IA

Ce protocole s'applique que l'intervenant soit un humain ou une IA (Claude, ChatGPT, Gemini, etc.).

### 7.1 Ce qu'une IA n'a PAS le droit de faire sans validation humaine

| Action | Regle |
|--------|-------|
| `tutor config save` | DEMANDER AVANT — expliquer ce qui va etre ecrase |
| `tutor local launch` | DEMANDER AVANT — expliquer les consequences |
| `pip install` sur le serveur | DEMANDER AVANT — lister les paquets impactes |
| Modifier body-extra.html, header.html, footer.html | PREVENIR que c'est un template global |
| Modifier un plugin Tutor | PREVENIR que ca necessite un tutor config save |
| Toute commande SSH sur le serveur de prod | INTERDIT sauf instruction explicite |

### 7.2 Ce qu'une IA DOIT faire systematiquement

| Action | Quand |
|--------|-------|
| Lire le code source avant de modifier une variable | Toujours |
| Verifier les namespaces Mako avant de modifier un template | Toujours |
| Proposer un rollback plan avant une modification ROUGE | Toujours |
| Tester les smoke tests apres un deploy | Toujours |
| Commiter avec un message conventionnel | Toujours |
| Ne pas enchainer les modifications sans valider la precedente | Toujours |

### 7.3 Principe de la modification unique

**Une modification a la fois. Valider. Puis la suivante.**

PAS : "je modifie 5 fichiers, j'installe un plugin, je change le CSS, et je deploie tout d'un coup"
OUI : "je modifie 1 fichier, je deploie, je valide, puis je passe au suivant"

---

## 8. HISTORIQUE DES INCIDENTS (pour ne pas repeter)

| Date | Incident | Cause | Impact | Temps perdu |
|------|----------|-------|--------|-------------|
| 2026-03-22 | 500 sur tout le staging | body-extra.html sans namespace static | Toutes les pages inaccessibles | 30 min |
| 2026-03-22 | Cours introuvable (404) | LEARNING_MICROFRONTEND_URL = None apres tutor config save | Tous les cours inaccessibles | 1h |
| 2026-03-22 | SSL error sur apps.* | tutor-mfe desinstalle par pip install tutor-forum | MFEs inaccessibles, cours inaccessibles | 1h |
| 2026-03-22 | CSS forum 404 | Fichier CSS separe non collecte par collectstatic | CSS non applique | 30 min |
| 2026-03-22 | CSS inline comme fix | Tentative de contournement au lieu de corriger la cause | Dette technique | 15 min |

**Total temps perdu sur des regressions evitables : ~3h**

---

## 9. CHECKLIST RAPIDE (A IMPRIMER)

Avant chaque deploy :
- [ ] Ai-je un backup des settings ?
- [ ] Ai-je un tag git pre-deploy ?
- [ ] Est-ce que je modifie un template global ? Si oui, suis-je pret a tester dans les 30 secondes ?
- [ ] Est-ce une modification ROUGE ? Si oui, ai-je suivi la procedure ROUGE ?

Apres chaque deploy :
- [ ] Homepage : 200 ?
- [ ] Login : 200 ?
- [ ] Catalogue : 200 ?
- [ ] Cours about : 200 ?
- [ ] Cours content (connecte) : accessible ?
- [ ] Containers : tous Up ?
- [ ] Settings critiques : tous presents ?

Si un test echoue :
- [ ] ROLLBACK IMMEDIAT
- [ ] Analyser la cause
- [ ] Corriger EN LOCAL
- [ ] Redeployer avec la correction
