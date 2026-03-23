# Procedure de mise a jour OpenEdX — Mission Formations

> Version 1.0 — 23 mars 2026
> IMPORTANT : ne jamais merger directement upstream dans ton fork

---

## 1. DIAGNOSTIC ACTUEL

| Element | Valeur |
|---------|--------|
| Fork base sur | Commit du 18 fevrier 2025 (master upstream) |
| Upstream en avance | ~1 548 commits |
| Tes commits custom | 15 (master) + 151 (staging) |
| Tutor version | v21.0.1 (Ulmo) |
| Derniere release upstream | Sumac.3 |
| Fichiers core modifies | AUCUN — tout le custom est dans des dossiers separes |

---

## 2. POURQUOI TON FORK N'A PAS BESOIN D'ETRE A JOUR

Tes customisations sont **isolees du core OpenEdX** :

| Ton code custom | Emplacement | Depend du core ? |
|----------------|-------------|-----------------|
| Theme Mission | `themes/mission-theme/` | Non — monte par-dessus |
| Plugin admin | `lms/djangoapps/mission_central_admin/` | Faiblement — utilise les APIs stables |
| Plugins Tutor | `tutor_plugins/` | Non — injectes via le systeme de plugins |
| Patches config | `tutor-patches/` | Depend de la version Tutor |
| Tests | `tests/` | Non |
| Docs | `docs/` | Non |
| Deploy | `deploy.sh` | Non |

**Le core OpenEdX dans ton container Docker vient de l'image Tutor** (`overhangio/openedx:21.0.2`), pas de ton fork. Ton fork est utilise uniquement pour stocker et deployer tes fichiers custom via `deploy.sh` (docker cp).

---

## 3. LA BONNE STRATEGIE : NE PAS MERGER, DEPLOYER PAR-DESSUS

### Comment ca fonctionne aujourd'hui

```
Image Docker Tutor (overhangio/openedx:21.0.2)
  = OpenEdX officiel, a jour pour la release Ulmo
     │
     │  docker cp (deploy.sh)
     ▼
Tes fichiers custom montes par-dessus :
  - themes/mission-theme/ → /openedx/themes/
  - mission_central_admin/ → /openedx/edx-platform/lms/djangoapps/
  - tutor-patches/ → settings injectes via plugins Tutor
```

**Le core OpenEdX est mis a jour quand tu changes l'image Tutor** — pas quand tu merges upstream dans ton fork.

### Comment mettre a jour OpenEdX

La mise a jour se fait via **Tutor**, pas via Git :

```bash
# 1. Mettre a jour Tutor
pip install --upgrade tutor

# 2. Tutor pull les nouvelles images Docker (nouvelle version OpenEdX)
tutor local upgrade --from=ulmo

# 3. Verifier que tes plugins sont compatibles
tutor plugins list

# 4. Tester
```

---

## 4. PROCEDURE DE MISE A JOUR (STEP BY STEP)

### Pre-requis

- [ ] Backup complet (tache 7 — deja en place)
- [ ] Tag git pre-upgrade : `git tag pre-upgrade-$(date +%Y%m%d)`
- [ ] Lister les plugins actifs : `tutor plugins list`
- [ ] Lister les packages pip : `pip list | grep tutor`
- [ ] Sauvegarder les settings : `cp production.py /tmp/production.py.pre-upgrade`

### Etape 1 — Verifier la nouvelle version

```bash
# Quelle version de Tutor est disponible ?
pip index versions tutor 2>/dev/null || pip install tutor==

# Lire les release notes :
# https://discuss.openedx.org/c/announcements/
# https://github.com/overhangio/tutor/releases
```

**LIRE les release notes AVANT de mettre a jour.** Chercher :
- Breaking changes
- Migrations de base de donnees
- APIs supprimees
- Changements de settings

### Etape 2 — Backup complet

```bash
# Sur le serveur
/root/backups/backup.sh

# Tag git
git tag pre-upgrade-$(date +%Y%m%d)
git push origin --tags
```

### Etape 3 — Mettre a jour Tutor sur le serveur

```bash
# Installer la nouvelle version
pip install --upgrade tutor tutor-mfe tutor-forum

# Verifier
tutor --version
```

### Etape 4 — Lancer l'upgrade

```bash
# Tutor gere la migration automatiquement
tutor local upgrade --from=ulmo

# Cela fait :
# 1. Pull les nouvelles images Docker
# 2. Arrete les containers
# 3. Execute les migrations de BDD
# 4. Redemarre avec la nouvelle version
```

### Etape 5 — Reappliquer les customisations

```bash
# OBLIGATOIRE apres chaque upgrade (meme principe que tutor local launch)
# Suivre le PROCESS_POST_TUTOR_LAUNCH.md

# 1. Verifier les plugins
tutor plugins list

# 2. Redeployer le theme et le plugin custom
./deploy.sh staging

# 3. Reappliquer le branding WeWill
# (automatique grace au container sidecar chatwoot-branding)

# 4. Verifier les settings
# (voir docs/ops/PROCESS_POST_TUTOR_LAUNCH.md)
```

### Etape 6 — Tester

```bash
# Executer la checklist de test (docs/ops/TEST_STAGING_CHECKLIST.md)
# Les 33 tests doivent passer
```

### Etape 7 — Si ca casse

```bash
# ROLLBACK

# Option 1 : reinstaller l'ancienne version de Tutor
pip install tutor==21.0.2 tutor-mfe==21.0.0 tutor-forum==21.0.0

# Option 2 : restaurer les settings
cp /tmp/production.py.pre-upgrade ~/.local/share/tutor/env/apps/openedx/settings/lms/production.py
tutor local restart lms

# Option 3 : restaurer la BDD (dernier recours)
# Restaurer le backup MySQL + MongoDB
```

---

## 5. COMPATIBILITE DES PLUGINS CUSTOM

Avant chaque upgrade, verifier que tes plugins sont compatibles :

### Ce qui peut casser

| Plugin | Risque | Quoi verifier |
|--------|--------|--------------|
| `mission_central_admin` | Moyen | Les imports OpenEdX (models, signals) existent toujours dans la nouvelle version |
| `mission_theme_lock` | Faible | Les settings FEATURES existent toujours |
| `mission_certificates_policy` | Faible | Le setting CERTIFICATES_HTML_VIEW existe toujours |
| Theme Mako | Moyen | Les templates de base (main.html, header.html) n'ont pas change de structure |
| CSS compile | Moyen | Les variables SCSS OpenEdX n'ont pas change |

### Comment verifier

```bash
# Apres l'upgrade, avant de deployer :

# 1. Tester que le plugin Python s'importe sans erreur
docker exec tutor_local-lms-1 python -c "
import lms.djangoapps.mission_central_admin
print('Plugin OK')
"

# 2. Tester que les templates compilent
docker exec tutor_local-lms-1 python -c "
from mako.template import Template
t = Template(filename='/openedx/themes/mission-theme/lms/templates/footer.html')
print('Templates OK')
"

# 3. Tester que le Sass compile
docker exec tutor_local-lms-1 npm run compile-sass -- --skip-default
```

---

## 6. CALENDRIER DE MISE A JOUR RECOMMANDE

| Quand | Action |
|-------|--------|
| **Maintenant** | Ne rien faire — rester sur Ulmo (stable, teste) |
| **Apres la mise en prod** | Evaluer le passage a Redwood ou Sumac |
| **Tous les 6 mois** | Verifier les release notes, evaluer l'upgrade |
| **Jamais** | Ne jamais passer 2+ releases d'un coup (Ulmo → Sumac directement) |

### Ordre des upgrades

```
Ulmo (actuel) → Redwood → Sumac → [future release]
```

**Toujours upgrader UNE release a la fois.** Jamais sauter une release.

---

## 7. CE QU'IL FAUT FAIRE AVEC LE FORK GIT

### Court terme (maintenant)

Ne rien changer. Le fork sert de **depot de code custom**, pas de miroir du core.

### Moyen terme (quand tu auras le CI/CD)

Reorganiser le repo pour que les fichiers custom soient clairement separes :

```
edx-platform/                    ← Fork (on ne touche pas le core)
├── mission-custom/               ← NOUVEAU dossier unique pour tout le custom
│   ├── theme/                    ← themes/mission-theme/ (deplace)
│   ├── plugin/                   ← mission_central_admin/ (deplace)
│   ├── tutor-plugins/            ← tutor_plugins/ (deplace)
│   ├── tutor-patches/            ← tutor-patches/ (deplace)
│   ├── tests/                    ← tests/ (deplace)
│   └── deploy.sh                 ← deploy.sh (deplace)
└── (tout le reste = core OpenEdX, jamais modifie)
```

### Long terme

Migrer les fichiers custom hors du fork completement :
- Theme → repo `mission-site` ou npm package
- Plugin → repo `mission-qualiopi` (deja prevu)
- Plugins Tutor → pip package ou repo dedie

Le fork devient alors inutile — tu utilises l'image Tutor officielle + tes packages.

---

## 8. REGLES ABSOLUES

| Regle | Pourquoi |
|-------|----------|
| Ne JAMAIS modifier un fichier du core OpenEdX | Rend les upgrades impossibles |
| Ne JAMAIS merger upstream dans ton fork | Trop de conflits, trop de risques |
| Toujours deployer le custom par-dessus (docker cp) | Le core vient de l'image Docker Tutor |
| Toujours tester apres un upgrade | Les APIs peuvent changer |
| Toujours upgrader une release a la fois | Moins de risques, plus facile a debugger |
| Toujours backup avant un upgrade | Pouvoir revenir en arriere |
