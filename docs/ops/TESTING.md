# Guide de Tests — Mission Formations

> Documentation de la suite de tests pour les equipes.
> Derniere mise a jour: 2026-03-16

---

## Vue d'ensemble

La suite de tests couvre **toutes les customisations** du projet Mission Formations.
Elle ne teste PAS le code Open edX upstream — uniquement ce que nous ajoutons.

```
tests/
├── conftest.py                    # Fixtures partagees (chemins, URLs)
├── pytest.ini                     # Configuration pytest + markers
├── unit/                          # Tests rapides, sans reseau
│   ├── test_tutor_config.py       # Config Tutor (syntaxe, secrets, doublons)
│   ├── test_olx_structure.py      # Cours OLX (XML, references, nommage)
│   ├── test_theme_templates.py    # Theme Mission (Mako, CSS, JS, securite)
│   ├── test_plugin_logic.py       # Plugin mission_central_admin
│   └── test_deploy_scripts.py     # Scripts deploy + .gitignore
├── integration/                   # Tests avec Docker actif
│   ├── test_health.py             # Sante services (containers, MySQL, Redis)
│   ├── test_auth.py               # Login, register, JWT, theme auth
│   └── test_api.py                # API courses, user, MFE config, contact
└── smoke/                         # Tests post-deploiement
    └── test_smoke_prod.py         # Pages critiques, assets, MFE, TLS
```

---

## Quand lancer les tests

| Moment | Commande | Duree |
|--------|----------|-------|
| **Avant chaque commit** | `pytest tests/unit/ -m unit` | ~2 sec |
| **Avant chaque deploy** | `pytest tests/integration/ -m integration` | ~30 sec |
| **Apres chaque deploy** | `pytest tests/smoke/ -m smoke` | ~10 sec |
| **Diagnostic complet** | `pytest tests/ -v` | ~1 min |

---

## Installation

```bash
pip install pytest
```

Pas d'autre dependance — les tests utilisent uniquement `pytest`, `ast`, `xml.etree`, `subprocess`, et la stdlib Python.

---

## Tests unitaires (unit/)

### test_tutor_config.py — Configuration Tutor

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestPythonSyntax::test_syntax_valid` | Chaque .py dans tutor-patches/ parse sans SyntaxError |
| `TestPythonSyntax::test_no_concatenated_statements` | Pas d'instructions Python collees (bug Codex) |
| `TestNoHardcodedSecrets::test_no_secrets` | Aucune cle API/JWT/RSA en dur |
| `TestNoHardcodedSecrets::test_secrets_use_environ` | Les secrets utilisent os.environ.get() |
| `TestNoDuplicateSettings::test_no_duplicate_settings` | DEFAULT_SITE_THEME et PIPELINE definis 1 seule fois |
| `TestLmsCmsCoherence::test_shared_settings_match` | Meme valeur dans LMS et CMS pour les settings partages |
| `TestLmsCmsCoherence::test_theme_dir_in_both` | COMPREHENSIVE_THEME_DIRS configure des 2 cotes |
| `TestConfigFileStructure::test_required_files_exist` | lms-production.py et cms-production.py presents |
| `TestConfigFileStructure::test_imports_present` | import os et import json dans chaque fichier |

**Quand un test echoue :**
- `test_syntax_valid` → Ouvrir le fichier a la ligne indiquee, corriger la syntaxe
- `test_no_secrets` → Remplacer la valeur en dur par `os.environ.get("CLE", "")`
- `test_no_duplicate_settings` → Supprimer le doublon (garder celui dans la section "common")

---

### test_olx_structure.py — Cours OLX

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestXmlValidity::test_course_xml_valid` | course.xml est un XML valide |
| `TestXmlValidity::test_all_xml_files_valid` | Tous les XML dans chapter/, sequential/, vertical/, html/ |
| `TestXmlValidity::test_xml_has_display_name` | Chaque element a un display_name |
| `TestReferentialIntegrity::test_course_references_chapters` | Chaque chapter reference existe |
| `TestReferentialIntegrity::test_chapters_reference_sequentials` | Chaque sequential reference existe |
| `TestReferentialIntegrity::test_sequentials_reference_verticals` | Chaque vertical reference existe |
| `TestReferentialIntegrity::test_verticals_reference_content` | Chaque html/problem reference existe |
| `TestNoOrphanFiles::test_no_orphan_chapters` | Pas de chapter sans reference dans course.xml |
| `TestNoOrphanFiles::test_no_orphan_html` | Pas de html/ sans reference dans un vertical |
| `TestNamingConventions::test_chapter_naming` | Chapitres commencent par "s" |
| `TestNamingConventions::test_html_naming` | HTML commencent par "html_s" |
| `TestNamingConventions::test_course_metadata` | course.xml a org, course, url_name, display_name |

**Quand un test echoue :**
- `test_verticals_reference_content` → Creer le fichier problem/ ou html/ manquant
- `test_no_orphan_html` → Ajouter une reference dans le vertical correspondant

---

### test_theme_templates.py — Theme Mission

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestRequiredFiles::test_lms_template_exists` | 12 templates critiques presents |
| `TestRequiredFiles::test_static_file_exists` | CSS compile, JS, logo, favicon presents et non vides |
| `TestMakoSyntax::test_has_inherit_directive` | Templates principales heritent de main.html |
| `TestMakoSyntax::test_no_unclosed_mako_blocks` | Autant de <%block que de </%block> |
| `TestMakoSyntax::test_no_unclosed_mako_defs` | Autant de <%def que de </%def> |
| `TestMakoSyntax::test_dashboard_includes_partials` | Dashboard inclut sidebar + hero |
| `TestDesignSystem::test_css_contains_brand_colors` | Couleurs #0965D0, #01E8AE, #0a1628 dans le CSS |
| `TestDesignSystem::test_css_not_empty` | CSS compile > 10Ko (pas casse) |
| `TestDesignSystem::test_dashboard_js_has_mf_dashboard` | Objet MF_DASHBOARD dans le JS |
| `TestTemplateSecurity::test_no_hardcoded_passwords` | Pas de mots de passe en dur |
| `TestTemplateSecurity::test_csrf_in_forms` | Token CSRF dans tous les formulaires POST |

**Quand un test echoue :**
- `test_css_not_empty` → Recompiler le SCSS : `tutor local do openedx-assets build`
- `test_no_unclosed_mako_blocks` → Ouvrir le template, chercher le <%block non ferme

---

### test_plugin_logic.py — Plugin mission_central_admin

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestPluginStructure::test_module_exists` | 8 modules Python presents |
| `TestPluginStructure::test_initial_migration_exists` | Migration 0001 presente |
| `TestPluginPythonSyntax::test_syntax_valid` | Tous les .py parsent sans erreur |
| `TestPluginUrls::test_urls_file_has_expected_patterns` | 7 routes attendues declarees |
| `TestPluginUrls::test_views_match_urls` | Chaque vue referencee existe |
| `TestModelDefinition::test_model_has_required_fields` | 13 champs du modele InternalMessageAudit |
| `TestModelDefinition::test_model_has_status_choices` | Statuts queued/sent/failed |
| `TestPluginTemplates::test_template_exists` | 5 templates du plugin presents |
| `TestAppConfig::test_ready_registers_handlers` | Error handlers 403/404/500 enregistres |
| `TestCeleryTasks::test_task_exists` | Tache Celery send_internal_message_task |
| `TestCeleryTasks::test_task_is_idempotent` | Verification anti-double-envoi |
| `TestTutorPlugins::test_tutor_plugin_syntax` | 6 plugins Tutor syntaxiquement valides |

---

### test_deploy_scripts.py — Scripts et infra

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestDeployScript::test_deploy_sh_exists` | deploy.sh present |
| `TestDeployScript::test_deploy_sh_executable` | chmod +x |
| `TestDeployScript::test_deploy_sh_valid_bash` | bash -n (syntaxe valide) |
| `TestCustomInfraScripts::test_script_valid_bash` | Scripts custom-infra valides |
| `TestGitignore::test_pattern_in_gitignore` | Patterns critiques dans .gitignore |
| `TestGitignore::test_no_secrets_env_tracked` | Aucun .secrets.env tracke par git |

---

## Tests d'integration (integration/)

**Prerequis :** Containers Docker Tutor en cours d'execution.

### test_health.py — Sante services

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestContainers::test_required_container_running` | LMS, CMS, MySQL, MongoDB, Redis actifs |
| `TestServiceHealth::test_mysql_responds` | MySQL repond au ping |
| `TestServiceHealth::test_redis_responds` | Redis retourne PONG |
| `TestServiceHealth::test_mongodb_responds` | MongoDB repond au ping |
| `TestDjangoHealth::test_lms_django_check` | manage.py check --deploy sans erreur |
| `TestDjangoHealth::test_lms_theme_loaded` | DEFAULT_SITE_THEME = mission-theme |

### test_auth.py — Authentification

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestAuthPages::test_login_page_200` | /login retourne 200 |
| `TestAuthPages::test_csrf_api` | /csrf/api/v1/token fonctionne |
| `TestAuthTheme::test_login_has_mission_branding` | Theme Mission sur la page login |
| `TestAuthTheme::test_login_not_mfe_redirect` | Pas de redirect vers MFE authn |
| `TestProtectedPages::test_dashboard_requires_auth` | Dashboard protege |
| `TestProtectedPages::test_admin_dashboard_requires_auth` | Admin protege |

### test_api.py — API

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestApiHeartbeat::test_lms_heartbeat` | /heartbeat retourne 200 |
| `TestCoursesApi::test_courses_list` | API courses retourne du JSON |
| `TestUserApi::test_user_api_requires_auth` | /api/user/v1/me protege (401/403) |
| `TestMfeConfigApi::test_mfe_config_has_mission_branding` | SITE_NAME contient "Mission" |
| `TestMissionEndpoints::test_contact_page` | /contact/ accessible publiquement |

---

## Tests smoke (smoke/)

**Lancer apres chaque deploy.** Peut etre automatise dans le pipeline.

### test_smoke_prod.py

| Test | Ce qu'il verifie |
|------|-----------------|
| `TestCriticalPages::test_homepage_200` | Homepage accessible |
| `TestCriticalPages::test_homepage_has_mission_content` | Contenu Mission present |
| `TestCriticalPages::test_studio_200` | Studio accessible |
| `TestStaticAssets::test_favicon_loads` | favicon.ico charge |
| `TestStaticAssets::test_logo_loads` | logo.png charge |
| `TestMfeApps::test_mfe_accessible` | MFE account, learning, authoring OK |
| `TestNo500Errors::test_no_500` | Aucune page critique en 500 |
| `TestTls::test_tls_valid` | Certificat TLS valide |
| `TestTls::test_tls_certificate_expiry` | Certificat expire dans > 7 jours |

---

## Variables d'environnement

Pour tester un autre environnement que staging :

```bash
MF_LMS_URL=https://academie.missionformations.com \
MF_CMS_URL=https://studio.missionformations.com \
MF_MFE_URL=https://apps.academie.missionformations.com \
pytest tests/smoke/ -m smoke
```

---

## Ajouter un nouveau test

1. Identifier la couche (unit / integration / smoke)
2. Creer le test dans le fichier existant ou un nouveau `test_*.py`
3. Ajouter le marker `@pytest.mark.unit` / `@pytest.mark.integration` / `@pytest.mark.smoke`
4. Mettre a jour ce document avec la description du test
5. **Commiter le test AVANT le code** (TDD: Red → Green → Refactor)

---

## Compteur de tests

| Fichier | Nb tests | Couverture |
|---------|----------|------------|
| test_tutor_config.py | 15 | Config Tutor, secrets, doublons, coherence LMS/CMS |
| test_olx_structure.py | 12 | XML, references, orphelins, nommage |
| test_theme_templates.py | 15 | Templates, Mako, CSS, JS, securite |
| test_plugin_logic.py | 18 | Plugin structure, URLs, modele, tasks, Tutor plugins |
| test_deploy_scripts.py | 10 | Scripts bash, .gitignore, secrets trackes |
| test_health.py | 9 | Containers, services, Django check |
| test_auth.py | 6 | Login, register, CSRF, protection pages |
| test_api.py | 7 | Heartbeat, courses, user, MFE config, contact |
| test_smoke_prod.py | 12 | Homepage, assets, MFE, 500, TLS |
| **TOTAL** | **~104** | **Toutes les customisations Mission Formations** |
