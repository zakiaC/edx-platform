# Strategie de Tests & Diagnostic — Mission Formations

> Document de reference pour les equipes QA et DevOps.
> 151+ tests automatises couvrant toutes les customisations du projet.
> Derniere mise a jour : 2026-03-17

---

## Architecture en 4 couches

```
┌──────────────────┬───────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┐
│     Couche       │                          Quoi tester                              │                        Pourquoi                         │
├──────────────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
│ 1. Infra         │ Containers Docker, services (MySQL, MongoDB, Redis, Meilisearch)  │ "Est-ce que la plateforme tourne ?"                     │
├──────────────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
│ 2. Config        │ Parsing Python des tutor-patches, variables d'env, secrets        │ "Est-ce que la config est valide ?"                     │
├──────────────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
│ 3. App           │ Login, register, dashboard, acces cours, API JWT                  │ "Est-ce que les fonctions critiques marchent ?"         │
├──────────────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
│ 4. Theme/Custom  │ Templates Mako, assets CSS/JS, plugin mission_central_admin       │ "Est-ce que nos customisations cassent quelque chose ?" │
└──────────────────┴───────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────┘
```

---

## Arborescence des tests

```
tests/
├── conftest.py                        # Fixtures partagees (chemins, URLs staging)
├── pytest.ini                         # Config pytest, markers: unit/integration/smoke
│
├── unit/                              # COUCHES 2 + 4 — Sans reseau, < 2s
│   ├── test_tutor_config.py           #   Couche 2: Config Tutor
│   ├── test_olx_structure.py          #   Couche 4: Cours OLX
│   ├── test_theme_templates.py        #   Couche 4: Theme Mission
│   ├── test_plugin_logic.py           #   Couche 4: Plugin mission_central_admin
│   └── test_deploy_scripts.py         #   Couche 2: Scripts + .gitignore
│
├── integration/                       # COUCHES 1 + 3 — Containers actifs, < 60s
│   ├── test_health.py                 #   Couche 1: Services Docker
│   ├── test_auth.py                   #   Couche 3: Authentification
│   └── test_api.py                    #   Couche 3: API endpoints
│
└── smoke/                             # TOUTES COUCHES — Post-deploy, < 30s
    └── test_smoke_prod.py             #   Verification finale production
```

---

## Workflow quotidien

```
  Developpeur ecrit du code
         │
         ▼
  ┌─────────────────────┐
  │  pytest tests/unit/  │  ← Avant chaque commit (2 sec)
  │  -m unit             │
  └──────────┬──────────┘
             │ PASS?
             ▼
        git commit
             │
             ▼
  ┌──────────────────────────┐
  │  pytest tests/integration │  ← Avant chaque deploy (30 sec)
  │  -m integration           │
  └──────────┬───────────────┘
             │ PASS?
             ▼
        tutor local start
             │
             ▼
  ┌────────────────────────┐
  │  pytest tests/smoke/    │  ← Apres chaque deploy (10 sec)
  │  -m smoke               │
  └────────────────────────┘
```

**Regle TDD** : chaque nouvelle feature commence par un test qui echoue (RED), puis on code (GREEN), puis on nettoie (REFACTOR).

---

## COUCHE 1 — Infra (test_health.py)

> **Question** : "Est-ce que la plateforme tourne ?"

### Tests disponibles

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_required_container_running[lms]` | Container LMS actif | `tutor local start -d` |
| 2 | `test_required_container_running[cms]` | Container CMS actif | `tutor local start -d` |
| 3 | `test_required_container_running[mysql]` | MySQL actif | Verifier Docker / disque |
| 4 | `test_required_container_running[mongodb]` | MongoDB actif | Verifier Docker / RAM |
| 5 | `test_required_container_running[redis]` | Redis actif | Verifier Docker |
| 6 | `test_optional_container_running[meilisearch]` | Meilisearch actif (optionnel) | Pas critique |
| 7 | `test_mysql_responds` | MySQL repond au ping | Verifier credentials |
| 8 | `test_redis_responds` | Redis retourne PONG | Verifier connexion |
| 9 | `test_mongodb_responds` | MongoDB repond au ping | Verifier auth / disque |

### Commande

```bash
pytest tests/integration/test_health.py -m integration -v
```

---

## COUCHE 1b — Sync disque / container Docker (test_deploy_health.py)

> **Question** : "Est-ce que le code dans le container correspond au code sur le disque ?"

### Contexte du probleme

Sur notre stack Tutor, il y a **deux copies du code** :
- `/root/edx-platform/` — le disque du serveur (mis a jour par `git pull`)
- `/openedx/edx-platform/` — dans le container Docker (copie independante)

**Un `git pull` met a jour le disque mais PAS le container.**
Sans `docker cp`, le container continue de servir l'ancien code.

Symptomes :
- Page qui retourne 404 alors que la route existe dans le code
- Vue qui retourne 500 car le fichier `views.py` dans le container est l'ancienne version
- Template manquant alors qu'il est bien dans le repo

### Tests disponibles

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_plugin_code_synced` | Compare le hash md5 de `urls.py`, `views.py`, `models.py`, `tasks.py`, `apps.py` entre disque et container | `docker cp` du plugin + restart |
| 2 | `test_templates_synced` | Compare le hash md5 des templates critiques entre disque et container | `docker cp` des themes + restart |
| 3 | `test_new_routes_accessible` | Verifie que TOUTES les routes Django custom sont enregistrees dans le container | `docker cp` du plugin + restart |

### Commande

```bash
pytest tests/integration/test_deploy_health.py::TestDiskContainerSync -m integration -v
```

### Fix quand ca echoue

```bash
# Copier le plugin mis a jour dans le container
docker cp /root/edx-platform/lms/djangoapps/mission_central_admin/ \
  tutor_local-lms-1:/openedx/edx-platform/lms/djangoapps/mission_central_admin/

# Copier le theme mis a jour dans le container
docker cp /root/edx-platform/themes/mission-theme/ \
  tutor_local-lms-1:/openedx/themes/mission-theme/

# Restart pour prendre en compte
docker restart tutor_local-lms-1
```

### Prevention

**Toujours utiliser `./deploy.sh staging`** au lieu de `git pull + restart`.
Le script `deploy.sh` inclut automatiquement le `docker cp` (etape 1/6).

### Diagnostic automatique

Le script `tests/diagnose.py` inclut cette verification dans la couche 1b.
Quand une desync est detectee, le diagnostic affiche :

```
CAUSE RACINE PRINCIPALE:
============================================================
  Code desynchronise entre disque et container Docker
  Cascade: git pull → disque mis a jour → container garde l'ancien code → route manquante → 404/500
  Origine: le container Docker a sa propre copie du code, independante du disque

  Fix complet:
  ./deploy.sh staging
```

### Quand l'utiliser

- Apres un reboot du serveur
- Apres `tutor local stop && tutor local start`
- Quand le site est inaccessible
- Apres une mise a jour Docker

---

## COUCHE 2 — Config (test_tutor_config.py + test_deploy_scripts.py)

> **Question** : "Est-ce que la config est valide ?"

### Tests — Configuration Tutor (test_tutor_config.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_syntax_valid[lms-production.py]` | Syntaxe Python LMS | Corriger le fichier a la ligne indiquee |
| 2 | `test_syntax_valid[cms-production.py]` | Syntaxe Python CMS | Corriger le fichier a la ligne indiquee |
| 3 | `test_syntax_valid[lms-assets.py]` | Syntaxe Python LMS assets | Corriger la syntaxe |
| 4 | `test_syntax_valid[cms-assets.py]` | Syntaxe Python CMS assets | Corriger la syntaxe |
| 5 | `test_no_concatenated_statements` | Pas d'instructions collees (bug Codex) | Ajouter saut de ligne |
| 6 | `test_no_secrets[lms-production.py]` | Pas de cles API en dur dans LMS | Utiliser os.environ.get() |
| 7 | `test_no_secrets[cms-production.py]` | Pas de cles API en dur dans CMS | Utiliser os.environ.get() |
| 8 | `test_secrets_use_environ` | Secrets charges via env vars | Remplacer valeur en dur |
| 9 | `test_no_duplicate_settings` | Pas de settings definis 2 fois | Supprimer le doublon |
| 10 | `test_shared_settings_match` | LMS et CMS coherents | Aligner les valeurs |
| 11 | `test_theme_dir_in_both` | Theme dir configure partout | Ajouter COMPREHENSIVE_THEME_DIRS |
| 12 | `test_required_files_exist` | Fichiers config presents | Creer le fichier manquant |
| 13 | `test_imports_present` | import os/json presents | Ajouter l'import |
| 14 | `test_lms_inherits_production` | LMS herite de production | Verifier l'import |
| 15 | `test_cms_inherits_production` | CMS herite de production | Verifier l'import |

### Tests — Scripts et securite (test_deploy_scripts.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 16 | `test_deploy_sh_exists` | deploy.sh present | Creer le script |
| 17 | `test_deploy_sh_executable` | deploy.sh chmod +x | `chmod +x deploy.sh` |
| 18 | `test_deploy_sh_valid_bash` | Syntaxe bash valide | Corriger la syntaxe |
| 19 | `test_deploy_sh_has_shebang` | Shebang present | Ajouter `#!/bin/bash` |
| 20 | `test_script_exists` | Scripts custom-infra presents | Verifier le dossier |
| 21 | `test_script_valid_bash` | Scripts bash valides | Corriger la syntaxe |
| 22 | `test_gitignore_exists` | .gitignore present | Creer le fichier |
| 23 | `test_pattern_in_gitignore[*.secrets.env]` | Secrets ignores | Ajouter le pattern |
| 24 | `test_pattern_in_gitignore[.codex-renders/]` | Artefacts Codex ignores | Ajouter le pattern |
| 25 | `test_pattern_in_gitignore[.DS_Store]` | macOS ignore | Ajouter le pattern |
| 26 | `test_pattern_in_gitignore[docker.sock]` | Docker socket ignore | Ajouter le pattern |
| 27 | `test_pattern_in_gitignore[*.xlsx]` | Fichiers Excel ignores | Ajouter le pattern |
| 28 | `test_no_secrets_env_tracked` | Aucun .secrets.env dans git | `git rm --cached` |

### Commande

```bash
pytest tests/unit/test_tutor_config.py tests/unit/test_deploy_scripts.py -m unit -v
```

### Quand l'utiliser

- Apres modification de `tutor-patches/*.py`
- Apres ajout d'un secret ou variable d'env
- Apres modification de deploy.sh ou .gitignore
- Pour verifier qu'un outil IA n'a pas casse la config

---

## COUCHE 3 — App (test_auth.py + test_api.py)

> **Question** : "Est-ce que les fonctions critiques marchent ?"

### Tests — Authentification (test_auth.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_login_page_200` | Page /login accessible | Verifier LMS + theme |
| 2 | `test_register_page_200` | Page /register accessible | Verifier LMS + theme |
| 3 | `test_csrf_api` | Token CSRF fonctionne | Verifier middleware |
| 4 | `test_login_has_mission_branding` | Theme Mission sur login | Verifier DEFAULT_SITE_THEME |
| 5 | `test_login_not_mfe_redirect` | Pas de redirect vers MFE | Verifier ENABLE_AUTHN_MICROFRONTEND=False |
| 6 | `test_dashboard_requires_auth` | Dashboard protege | Verifier login_required |
| 7 | `test_admin_dashboard_requires_auth` | Admin protege | Verifier _admin_allowed |

### Tests — API (test_api.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 8 | `test_lms_heartbeat` | /heartbeat LMS OK | Container LMS down |
| 9 | `test_cms_heartbeat` | /heartbeat CMS OK | Container CMS down |
| 10 | `test_courses_list` | API courses retourne JSON | Verifier base de donnees |
| 11 | `test_user_api_requires_auth` | /api/user/v1/me protege | Verifier auth middleware |
| 12 | `test_mfe_config_accessible` | MFE config API OK | Verifier ENABLE_MFE_CONFIG_API |
| 13 | `test_mfe_config_has_mission_branding` | SITE_NAME = Mission | Verifier MFE_CONFIG |
| 14 | `test_contact_page` | /contact/ accessible | Verifier plugin URLs |
| 15 | `test_mission_errors_preview` | Pages erreur custom OK | Verifier error_views |

### Commande

```bash
pytest tests/integration/test_auth.py tests/integration/test_api.py -m integration -v
```

### Quand l'utiliser

- Apres modification du plugin mission_central_admin
- Apres changement de config MFE
- Apres mise a jour OpenEdX
- Quand le login ne fonctionne pas

---

## COUCHE 4 — Theme & Custom (test_theme_templates.py + test_plugin_logic.py + test_olx_structure.py)

> **Question** : "Est-ce que nos customisations cassent quelque chose ?"

### Tests — Theme Mission (test_theme_templates.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_lms_template_exists[index.html]` | Homepage template present | Restaurer le fichier |
| 2 | `test_lms_template_exists[dashboard.html]` | Dashboard template present | Restaurer le fichier |
| 3 | `test_lms_template_exists[header/header.html]` | Header present | Restaurer le fichier |
| 4 | `test_lms_template_exists[footer.html]` | Footer present | Restaurer le fichier |
| 5 | `test_lms_template_exists[403.html]` | Page 403 presente | Restaurer le fichier |
| 6 | `test_lms_template_exists[body-extra.html]` | Body extra present | Restaurer le fichier |
| 7 | `test_lms_template_exists[login_and_register.html]` | Login template present | Restaurer le fichier |
| 8 | `test_lms_template_exists[_mf_dashboard_hero.html]` | Dashboard hero present | Restaurer le fichier |
| 9 | `test_lms_template_exists[_mf_dashboard_sidebar.html]` | Sidebar presente | Restaurer le fichier |
| 10 | `test_lms_template_exists[_mf_dashboard_admin.html]` | Admin dashboard present | Restaurer le fichier |
| 11 | `test_lms_template_exists[_mf_dashboard_formateur.html]` | Formateur dashboard present | Restaurer le fichier |
| 12 | `test_lms_template_exists[_mf_brand_panel.html]` | Brand panel present | Restaurer le fichier |
| 13 | `test_static_template_exists` | Pages erreur statiques (403, 404, server-error) | Restaurer |
| 14 | `test_static_file_exists[css/lms-main-v1.css]` | CSS compile present et non vide | Recompiler SCSS |
| 15 | `test_static_file_exists[js/mf-dashboard.js]` | JS dashboard present | Restaurer |
| 16 | `test_static_file_exists[images/logo.png]` | Logo present | Restaurer |
| 17 | `test_static_file_exists[images/favicon.ico]` | Favicon present | Restaurer |
| 18 | `test_scss_entry_point_exists` | SCSS entry point present | Creer lms-main-v1.scss |
| 19 | `test_cms_footer_exists` | Footer CMS present | Restaurer |
| 20 | `test_has_inherit_directive` | Templates heritent de main.html | Ajouter <%inherit> |
| 21 | `test_has_pagetitle_block` | Bloc pagetitle present | Ajouter le bloc |
| 22 | `test_no_unclosed_mako_blocks` | Blocs <%block> fermes | Fermer avec </%block> |
| 23 | `test_no_unclosed_mako_defs` | Defs <%def> fermees | Fermer avec </%def> |
| 24 | `test_dashboard_includes_partials` | Dashboard inclut sidebar+hero | Ajouter <%include> |
| 25 | `test_css_contains_brand_colors` | Couleurs Mission dans CSS | Recompiler SCSS |
| 26 | `test_css_not_empty` | CSS > 10Ko (pas casse) | Recompiler SCSS |
| 27 | `test_dashboard_js_has_mf_dashboard` | Objet MF_DASHBOARD dans JS | Verifier le JS |
| 28 | `test_login_js_has_brand_panel` | Brand panel dans login JS | Verifier le JS |
| 29 | `test_no_hardcoded_passwords` | Pas de mots de passe en dur | Supprimer le secret |
| 30 | `test_csrf_in_forms` | CSRF dans formulaires POST | Ajouter csrf_token |

### Tests — Plugin mission_central_admin (test_plugin_logic.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 31 | `test_plugin_dir_exists` | Dossier plugin present | Restaurer |
| 32 | `test_module_exists[*.py]` | 8 modules Python presents | Creer le module manquant |
| 33 | `test_migrations_dir_exists` | Dossier migrations present | `makemigrations` |
| 34 | `test_initial_migration_exists` | Migration 0001 presente | `makemigrations` |
| 35 | `test_syntax_valid[*.py]` | Syntaxe Python de chaque module | Corriger la syntaxe |
| 36 | `test_migration_syntax` | Syntaxe migration | Corriger ou regenerer |
| 37 | `test_urls_file_has_expected_patterns` | 8 routes declarees | Ajouter la route |
| 38 | `test_views_match_urls` | Chaque vue referencee existe | Creer la vue |
| 39 | `test_model_has_required_fields` | 13 champs InternalMessageAudit | Ajouter le champ + migration |
| 40 | `test_model_has_status_choices` | Statuts queued/sent/failed | Ajouter le choix |
| 41 | `test_model_has_recipients_method` | Methode recipients() | Implementer la methode |
| 42 | `test_template_exists` | 6 templates plugin presents | Creer le template |
| 43 | `test_contact_template_has_form` | Formulaire dans contact.html | Ajouter <form> |
| 44 | `test_messaging_template_has_form` | Formulaire dans messaging | Ajouter <form> |
| 45 | `test_app_label` | App label correct | Verifier apps.py |
| 46 | `test_ready_registers_handlers` | Error handlers enregistres | Verifier ready() |
| 47 | `test_task_exists` | Tache Celery presente | Creer la tache |
| 48 | `test_task_is_idempotent` | Anti-double-envoi | Ajouter check statut |
| 49 | `test_tutor_plugin_syntax[*.py]` | 6 plugins Tutor valides | Corriger la syntaxe |

### Tests — Cours OLX (test_olx_structure.py)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 50 | `test_course_xml_valid` | course.xml parsable | Corriger le XML |
| 51 | `test_all_xml_files_valid[chapter]` | Tous les chapters valides | Corriger le XML |
| 52 | `test_all_xml_files_valid[sequential]` | Tous les sequentials valides | Corriger le XML |
| 53 | `test_all_xml_files_valid[vertical]` | Tous les verticals valides | Corriger le XML |
| 54 | `test_all_xml_files_valid[html]` | Tous les html valides | Corriger le XML |
| 55 | `test_xml_has_display_name` | display_name sur chaque element | Ajouter l'attribut |
| 56 | `test_course_references_chapters` | Chaque ref chapter existe | Creer le fichier |
| 57 | `test_chapters_reference_sequentials` | Chaque ref sequential existe | Creer le fichier |
| 58 | `test_sequentials_reference_verticals` | Chaque ref vertical existe | Creer le fichier |
| 59 | `test_verticals_reference_content` | Chaque ref html/problem existe | Creer le fichier |
| 60 | `test_no_orphan_chapters` | Pas de chapter orphelin | Supprimer ou referencer |
| 61 | `test_no_orphan_html` | Pas de html orphelin | Supprimer ou referencer |
| 62 | `test_chapter_naming` | Convention s{N}_... | Renommer le fichier |
| 63 | `test_html_naming` | Convention html_s{N}_... | Renommer le fichier |
| 64 | `test_course_metadata` | Attributs org, course, url_name | Ajouter l'attribut |

### Commande

```bash
pytest tests/unit/test_theme_templates.py tests/unit/test_plugin_logic.py tests/unit/test_olx_structure.py -m unit -v
```

### Quand l'utiliser

- Apres modification de templates Mako
- Apres ajout/modification de CSS ou JS
- Apres modification du plugin Django
- Apres ajout de contenu OLX
- Apres intervention d'un outil IA (Codex, Copilot)

---

## Tests Smoke — Post-deploiement (test_smoke_prod.py)

> Validation finale apres deploy. Couvre les 4 couches en mode "boite noire".

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_homepage_200` | Homepage accessible | Verifier LMS |
| 2 | `test_homepage_has_mission_content` | Contenu Mission present | Verifier theme |
| 3 | `test_login_200` | Login accessible | Verifier auth |
| 4 | `test_register_200` | Register accessible | Verifier auth |
| 5 | `test_studio_200` | Studio accessible | Verifier CMS |
| 6 | `test_contact_200` | Contact accessible | Verifier plugin |
| 7 | `test_favicon_loads` | Favicon charge | collectstatic |
| 8 | `test_logo_loads` | Logo charge | collectstatic |
| 9 | `test_css_theme_loaded` | CSS Mission present | Recompiler assets |
| 10 | `test_mfe_accessible` | MFE account/learning/authoring | Verifier Caddy + MFE |
| 11 | `test_no_500` | Aucune page en erreur 500 | Verifier logs LMS |
| 12 | `test_tls_valid` | Certificat TLS valide | Renouveler certificat |
| 13 | `test_tls_certificate_expiry` | Certificat > 7 jours | Renouveler certificat |

### Commande

```bash
pytest tests/smoke/ -m smoke -v
```

### Variables d'environnement pour cibler un autre env

```bash
MF_LMS_URL=https://academie.missionformations.com \
MF_CMS_URL=https://studio.missionformations.com \
MF_MFE_URL=https://apps.academie.missionformations.com \
pytest tests/smoke/ -m smoke -v
```

---

## Tests post-deploy (test_deploy_health.py)

> Detecte les regressions causees par le deploiement lui-meme.
> **A lancer systematiquement apres chaque deploy sur staging ou production.**

### Tests — Pages admin (pas de 500)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 1 | `test_no_500_on_admin_pages[/admin/mission-dashboard/]` | Dashboard admin ne crash pas | Verifier logs LMS |
| 2 | `test_no_500_on_admin_pages[/admin/mission-dashboard/tests/]` | Page Tests & QA ne crash pas | Verifier logs LMS |
| 3 | `test_no_500_on_admin_pages[/contact/]` | Page contact ne crash pas | Verifier logs LMS |
| 4 | `test_no_500_on_admin_pages[/messagerie/interne/]` | Messagerie ne crash pas | Verifier logs LMS |

### Tests — Cache Mako

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 5 | `test_dashboard_renders_without_error` | Dashboard admin pas de "Server Error" | Vider cache Mako + restart |
| 6 | `test_test_dashboard_renders_without_error` | Page Tests & QA pas de "Server Error" | Vider cache Mako + restart |
| 7 | `test_homepage_renders_mission_theme` | Homepage contient les classes CSS `mf-` | collectstatic + restart |

> **Qu'est-ce que le cache Mako ?**
> Mako compile les templates `.html` en fichiers Python `.mako.py` dans `/tmp/`.
> Apres un deploy, l'ancien cache peut rester et servir une version perimee du template.
> Symptome : erreur 500 ou page cassee alors que le code est correct.

**Fix cache Mako :**
```bash
docker exec tutor_local-lms-1 bash -c 'find /tmp -name "*.mako.py" -delete'
docker restart tutor_local-lms-1
```

### Tests — Webpack (CRITIQUE)

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 8 | `test_webpack_stats_exists` | `webpack-stats.json` present dans le container | `npm run webpack` + collectstatic + restart |
| 9 | `test_webpack_stats_not_empty` | `webpack-stats.json` est un JSON valide | `npm run webpack` + collectstatic + restart |
| 10 | `test_collectstatic_preserves_webpack` | webpack status = "done" apres collectstatic | Relancer webpack avant collectstatic |

> **Pourquoi ces tests sont critiques ?**
> `main.html` (le template parent de TOUTES les pages) appelle `static.webpack('commons')`.
> Cette fonction lit `webpack-stats.json`. Si le fichier est absent → `OSError` → **500 sur TOUTES les pages**.
>
> **Cause la plus frequente :** `collectstatic --clear` supprime tout dans `/openedx/staticfiles/`,
> y compris `webpack-stats.json`. C'est pourquoi `deploy.sh` utilise `--noinput` SANS `--clear`.

**Fix webpack-stats.json manquant :**
```bash
docker exec tutor_local-lms-1 bash -c 'cd /openedx/edx-platform && npm run webpack'
docker exec tutor_local-lms-1 ./manage.py lms collectstatic --noinput
docker restart tutor_local-lms-1
```

### Tests — Synchronisation git / serveur

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 11 | `test_git_no_uncommitted_theme_changes` | Pas de modifs non commitees dans `themes/` | `git commit` ou `git checkout` |
| 12 | `test_container_has_latest_code` | Container a le dernier commit staging | `git pull` + restart |

### Tests — Fichiers statiques

| # | Test | Description | Action si FAIL |
|---|------|-------------|----------------|
| 13 | `test_theme_css_served` | CSS theme accessible via HTTP | collectstatic + restart |
| 14 | `test_theme_js_served` | JS dashboard accessible via HTTP | collectstatic + restart |

### Commande

```bash
pytest tests/integration/test_deploy_health.py -m integration -v
```

### Quand l'utiliser

- **Apres chaque deploy** (staging ou production)
- Quand une page affiche "erreur temporaire" ou "Server Error"
- Apres un `collectstatic`
- Apres un `docker restart` du LMS

### Arbre de decision des erreurs 500

```
Page retourne 500
       │
       ├── TOUTES les pages en 500 ?
       │       OUI → webpack-stats.json manquant
       │              Fix: npm run webpack + collectstatic + restart
       │
       ├── UNE SEULE page en 500 ?
       │       OUI → Template Mako corrompu ou bug dans le code
       │              Fix: vider cache Mako + restart
       │              Si persiste: docker logs tutor_local-lms-1 --tail 50
       │
       └── Pages OK puis 500 apres deploy ?
               OUI → collectstatic --clear a supprime webpack-stats.json
                      Fix: npm run webpack + collectstatic --noinput + restart
```

---

## Procedure de diagnostic en cas de bug production

```
1. Bug signale en production
         │
         ▼
2. Lancer: pytest tests/smoke/ -m smoke -v
         │
         ├── Si des tests smoke echouent → identifier la couche cassee
         │
         ▼
3. Lancer les tests de la couche concernee:
   - Infra cassee     → pytest tests/integration/test_health.py
   - Auth cassee      → pytest tests/integration/test_auth.py
   - API cassee       → pytest tests/integration/test_api.py
   - Theme casse      → pytest tests/unit/test_theme_templates.py
   - Config cassee    → pytest tests/unit/test_tutor_config.py
   - Regression deploy → pytest tests/integration/test_deploy_health.py
         │
         ▼
4. Le test qui echoue indique:
   - Le composant exact en erreur
   - L'action corrective a effectuer
         │
         ▼
5. Corriger → Relancer les tests → Deployer → Smoke tests
```

---

## Dashboard Tests & QA

Les administrateurs (superusers) ont acces a une interface web pour lancer les tests directement depuis le dashboard :

**URL** : `/admin/mission-dashboard/tests/`

**Acces** : Sidebar > section "Qualite" > "Tests & QA"

**Fonctionnalites** :
- Lancer les tests unitaires, integration, smoke ou tout
- Voir les resultats colores (PASSED/FAILED)
- Documentation inline

---

## Compteur de tests par couche

| Couche | Fichier(s) | Nb tests | Type |
|--------|-----------|----------|------|
| 1. Infra | test_health.py | 9 | integration |
| 1b. Sync | test_deploy_health.py (TestDiskContainerSync) | 3 | integration |
| 2. Config | test_tutor_config.py + test_deploy_scripts.py | 28 | unit |
| 3. App | test_auth.py + test_api.py | 15 | integration |
| 4. Theme/Custom | test_theme_templates.py + test_plugin_logic.py + test_olx_structure.py | 82 | unit |
| Deploy | test_deploy_health.py (Mako, webpack, pages, static) | 14 | integration |
| Smoke | test_smoke_prod.py | 13 | smoke |
| **TOTAL** | **10 fichiers** | **~151** | |

---

## Ajouter un nouveau test

1. **Identifier la couche** (1-4) et le type (unit/integration/smoke)
2. **Ecrire le test d'abord** (TDD: il doit echouer = RED)
3. **Coder la feature** (GREEN)
4. **Nettoyer** (REFACTOR)
5. **Mettre a jour ce document** avec la description du test
6. **Commiter test + code ensemble**

### Convention de nommage

```python
# Fichier: tests/{type}/test_{composant}.py
# Classe: Test{Domaine}
# Methode: test_{ce_que_ca_verifie}

class TestAuthPages:
    def test_login_page_200(self):
        ...
```
