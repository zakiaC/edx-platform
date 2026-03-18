# Diagnostic du repo — Natif OpenEdX vs Custom Mission Formations

> Audit du 18 mars 2026
> Total : 334+ fichiers custom, 4 fichiers natifs modifies

---

## Architecture du code custom

```
edx-platform/
│
├── themes/mission-theme/          72 fichiers  ✅ ISOLE
│   ├── lms/templates/             47 templates Mako (dashboard, admin, aide, catalogue, auth, emails)
│   ├── lms/static/                16 fichiers (CSS, JS, SCSS, images)
│   └── cms/templates/              6 templates (footer Studio, widgets)
│
├── lms/djangoapps/mission_central_admin/  13 fichiers  ✅ ISOLE
│   ├── models.py                  Academy, AcademyAdmin, AcademyCourse, AcademyEnrollment, InternalMessageAudit
│   ├── views.py                   25+ vues (dashboard, academy manager, aide, catalogue, PDF, delete user, tests)
│   ├── urls.py                    18 routes
│   ├── pdf_reports.py             Generation PDF Qualiopi (attestation + rapport suivi)
│   ├── tasks.py                   Celery (envoi emails internes)
│   ├── error_views.py             Pages erreur custom (403, 404, 500, maintenance)
│   ├── forms.py                   Formulaire admin user avec email obligatoire
│   ├── apps.py                    Config app + registration error handlers
│   └── migrations/                2 migrations (InternalMessageAudit + Academy models)
│
├── tutor_plugins/                  8 fichiers  ✅ ISOLE
│   ├── mission_theme_lock.py      Force le theme + desactive MFE auth
│   ├── mission_theme_assets.py    Copie CSS/JS dans staticfiles
│   ├── mission_central_admin.py   Enregistre l'app Django
│   ├── mission_certificates_policy.py  Politique certificats sidebar
│   ├── mission_braze_enrollment.py     Config email enrollment
│   ├── mission_csp_report_only.py      Headers CSP
│   └── mission_wewill.py          Reverse proxy Caddy pour le chat
│
├── tutor-patches/                  5 fichiers  ✅ ISOLE
│   ├── lms-production.py          Config LMS (JWT, MFE, features, theme)
│   ├── cms-production.py          Config CMS (theme, auth OAuth2)
│   ├── lms-assets.py              Config compilation assets LMS
│   ├── cms-assets.py              Config compilation assets CMS
│   └── Dockerfile                 (non utilise actuellement)
│
├── tests/                         21 fichiers  ✅ ISOLE
│   ├── unit/                      7 fichiers (config, OLX, theme, plugin, deploy, PDF)
│   ├── integration/               4 fichiers (health, auth, API, deploy)
│   ├── smoke/                     1 fichier (post-deploy)
│   ├── conftest.py                Fixtures partagees
│   └── diagnose.py                Script diagnostic cause racine SSH
│
├── docs/                          ✅ ISOLE
│   ├── ops/                       Changelogs, checklist, testing, WeWill guides
│   ├── qualiopi/                  Epic module Qualiopi (14 tickets)
│   └── chat-v2/                   Epic fork WeWill (9 tickets)
│
├── olx-courses/                   117 fichiers  ✅ ISOLE
│   └── MF-VTC-2025               Cours VTC complet (8 chapters, 19 sequentials, 44 verticals, 27 HTML, 17 quiz)
│
├── custom-infra/                  20 fichiers  ✅ ISOLE
│   ├── scripts/                   Deploy, smoke test, tenant config
│   └── config/                    Template tenant JSON
│
└── deploy.sh                      Script de deploiement principal
```

---

## Fichiers natifs OpenEdX modifies (DETTE TECHNIQUE)

### 1. common/djangoapps/student/views/management.py
- **Modification** : Ajoute `site_id` au contexte de l'email d'activation
- **Raison** : Pour que l'email utilise le bon theme (Mission au lieu de OpenEdX)
- **Impact** : Faible — ajoute un parametre, ne casse rien
- **Risque upstream** : Conflit lors des mises a jour OpenEdX
- **Solution ideale** : Creer un signal handler dans mission_central_admin qui injecte le site_id
- **Priorite** : Basse

### 2. openedx/core/djangoapps/user_authn/views/register.py
- **Modification** : Garde les users inactifs deconnectes avant activation email
- **Raison** : Securite — empecher l'acces avant validation email
- **Impact** : Moyen — change le comportement d'authentification
- **Risque upstream** : Conflit lors des mises a jour OpenEdX
- **Solution ideale** : Middleware custom dans mission_central_admin qui intercepte la session
- **Priorite** : Moyenne

### 3. common/templates/student/edx_ace/accountactivation/email/body.html
- **Modification** : Email d'activation brande Mission Formations
- **Statut** : DOUBLON — le meme template existe dans themes/mission-theme/
- **Action** : Restaurer le fichier natif, le theme prend la priorite automatiquement
- **Priorite** : Haute (facile a corriger)

### 4. lms/templates/admin/base_site.html
- **Modification** : CSS admin Django (couleurs Mission)
- **Statut** : DOUBLON — le meme template existe dans themes/mission-theme/
- **Action** : Verifier que le theme override est complet, puis restaurer le natif
- **Priorite** : Haute (facile a corriger)

---

## Actions correctives

### Immediat (doublons a supprimer)

| Fichier natif | Action | Risque |
|---------------|--------|--------|
| `common/templates/.../accountactivation/email/body.html` | Restaurer version OpenEdX originale | Zero — le theme override fonctionne |
| `lms/templates/admin/base_site.html` | Restaurer version OpenEdX originale | Zero — le theme override fonctionne |

### A planifier (refactoring)

| Fichier natif | Solution | Effort |
|---------------|----------|--------|
| `management.py` | Signal handler dans mission_central_admin | 2h |
| `register.py` | Middleware custom dans mission_central_admin | 3h |

---

## Resume

| Categorie | Fichiers | Isolation |
|-----------|----------|-----------|
| Theme mission-theme | 72 | ✅ Parfait |
| Plugin Django | 13 | ✅ Parfait |
| Plugins Tutor | 8 | ✅ Parfait |
| Config Tutor | 5 | ✅ Parfait |
| Infra custom | 20 | ✅ Parfait |
| Tests | 21 | ✅ Parfait |
| Documentation | 74 | ✅ Parfait |
| Cours OLX | 117 | ✅ Parfait |
| **Fichiers natifs modifies** | **4** | **⚠️ 2 doublons + 2 a refactorer** |

**Conclusion** : Le repo est bien organise. 330+ fichiers custom sont isoles dans des dossiers dedies. Seuls 4 fichiers natifs ont ete touches — 2 sont des doublons faciles a corriger, 2 necessitent un refactoring pour etre deplacees dans le plugin.
