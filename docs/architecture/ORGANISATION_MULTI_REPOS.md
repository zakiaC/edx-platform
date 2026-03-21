# Organisation multi-repos — Mission Formations

> Version 1.0 — 21 mars 2026
> 8 repos GitHub sous l'organisation MissionFormations
> Plan de migration depuis le monorepo actuel

---

## LES 8 REPOS

```
github.com/MissionFormations/
│
├── openedx-platform          Code — LMS formations
├── mission-qualiopi           Code — Hub API Qualiopi
├── mission-odoo               Code — Modules Odoo custom
├── mission-chatwoot           Config — WeWill Docker
├── mission-site               Code — Site internet vitrine
├── mission-docs               Docs — Documentation technique
├── mission-admin              Docs — Documents administratifs (PRIVE)
└── mission-org                Docs — Organisation interne (PRIVE)
```

---

## DETAIL PAR REPO

### 1. openedx-platform

**Role** : Fork OpenEdX avec toutes les customisations LMS/CMS
**Visibilite** : Prive
**Deploy** : VPS OVH (staging + prod)

```
openedx-platform/
├── lms/djangoapps/mission_central_admin/
│   ├── models.py             ← Academy, AcademyAdmin, AcademyCourse (restent ici)
│   ├── views.py              ← Vues LMS (allege apres migration Qualiopi)
│   ├── urls.py               ← Routes LMS uniquement
│   ├── signal_forwarder.py   ← NOUVEAU : forward signaux vers app Qualiopi
│   ├── middleware.py         ← InactiveUserLogoutMiddleware
│   ├── forms.py
│   └── migrations/
├── themes/mission-theme/
│   ├── lms/templates/        ← 80+ templates Mako
│   ├── lms/static/css/       ← CSS compile
│   ├── lms/static/sass/      ← SCSS source
│   ├── lms/static/js/        ← JS custom
│   └── cms/                  ← Templates CMS/Studio
├── tutor_plugins/             ← 8 plugins Tutor (tous ici)
│   ├── mission_central_admin.py
│   ├── mission_authn_override.py
│   ├── mission_certificates_policy.py
│   ├── mission_csp_report_only.py
│   ├── mission_braze_enrollment.py
│   ├── mission_theme_assets.py
│   ├── mission_theme_lock.py
│   └── mission_wewill.py
├── tutor-patches/             ← Config production LMS/CMS
│   ├── lms-production.py
│   ├── cms-production.py
│   ├── Dockerfile
│   └── .secrets.env          ← .gitignore
├── custom-infra/
│   ├── docs/                 ← Docs infra specifiques au LMS
│   ├── scripts/              ← Scripts deploy, smoke, config
│   └── config/               ← Templates de config
├── tests/                    ← Tests du LMS custom
│   ├── unit/
│   ├── integration/
│   ├── smoke/
│   ├── diagnose.py
│   └── pytest.ini
├── olx-courses/              ← Contenu des cours (OLX)
├── deploy.sh                 ← Script de deploiement
├── CLAUDE.md                 ← Instructions projet
├── .github/
│   └── workflows/
│       ├── ci.yml            ← Tests + lint
│       ├── deploy-staging.yml ← Deploy auto staging
│       ├── deploy-prod.yml   ← Deploy auto prod
│       └── release.yml       ← Release notes auto
└── (core OpenEdX — non modifie)
```

**Ce qui est RETIRE de ce repo (migre vers mission-docs) :**
- docs/qualiopi/*
- docs/odoo/*
- docs/chatwoot/*
- docs/chat-v2/*
- docs/architecture/*
- docs/business/*
- docs/changelogs/*
- docs/todo/*
- docs/FAQ_technique/*
- docs/ROADMAP_UNIFIEE.md
- docs/demo/*
- prompts/*

**Ce qui RESTE dans docs/ :**
- docs/ops/ (runbooks, checklists, DNS, testing — specifique au LMS)

---

### 2. mission-qualiopi

**Role** : App Django standalone — hub API central, conformite Qualiopi
**Visibilite** : Prive
**Deploy** : Container Docker sur VPS OVH (meme reseau que OpenEdX)

```
mission-qualiopi/
├── qualiopi/                  ← App Django principale
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config.py          ← QualiopiConfig
│   │   ├── parcours.py        ← RecueilBesoin, Convention, EvaluationPrePost, Emargement
│   │   ├── suivi.py           ← EnqueteSatisfaction, AbandonLog, PointSuivi, EnqueteInsertion
│   │   ├── equipe.py          ← FicheFormateur, ActionFormationFormateur, ReunionPedagogique, SousTraitant
│   │   ├── qualite.py         ← Reclamation, VeilleEntry, Partenariat, PlanAmelioration, RevueDirection
│   │   ├── documents.py       ← DocumentQualiopi, BilanFinanceur
│   │   └── automation.py      ← AutomationRule, AutomationLog, ScheduledTask, EmailTemplate, RSSSource, QualiopiScorecard, Notification
│   ├── api/
│   │   ├── webhooks/
│   │   │   ├── openedx.py     ← Groupe 1 (6 endpoints)
│   │   │   ├── odoo.py        ← Groupe 2 (5 endpoints)
│   │   │   └── chat.py        ← Groupe 3 (2 endpoints)
│   │   ├── data.py            ← Groupe 4 (6 endpoints — dashboard)
│   │   ├── documents.py       ← Groupe 5 (5 endpoints — PDFs)
│   │   ├── forms.py           ← Groupe 6 (8 endpoints — formulaires apprenant)
│   │   ├── admin_crud.py      ← Groupe 7 (~30 endpoints — CRUD registres)
│   │   ├── notifications.py   ← Groupe 8 (3 endpoints)
│   │   ├── scorecard.py       ← Groupe 9 (3 endpoints)
│   │   ├── veille.py          ← Groupe 10 (5 endpoints)
│   │   ├── emails.py          ← Groupe 11 (5 endpoints)
│   │   ├── automation.py      ← Groupe 12 (4 endpoints)
│   │   ├── exports.py         ← Groupe 13 (5 endpoints)
│   │   └── config.py          ← Groupe 14 (4 endpoints)
│   ├── services/
│   │   ├── openedx_reader.py  ← Requetes MySQL read-only OpenEdX
│   │   ├── odoo_client.py     ← Client API Odoo
│   │   ├── chatwoot_client.py ← Client API WeWill
│   │   ├── pdf_generator.py   ← Moteur PDF ReportLab (22 templates)
│   │   ├── email_sender.py    ← Envoi emails avec templates
│   │   ├── rss_scraper.py     ← Scraping flux RSS veille
│   │   └── scorecard_engine.py ← Calcul des 32 indicateurs
│   ├── tasks/
│   │   ├── pdf_tasks.py       ← Celery tasks generation PDF
│   │   ├── email_tasks.py     ← Celery tasks envoi email
│   │   ├── automation_tasks.py ← Celery tasks workflows
│   │   ├── watch_tasks.py     ← Celery tasks veille RSS
│   │   ├── quality_tasks.py   ← Celery tasks alertes qualite
│   │   └── attendance_tasks.py ← Celery tasks assiduite
│   ├── templates/
│   │   ├── emails/            ← 17 templates email HTML
│   │   ├── pdf/               ← Styles et layouts PDF
│   │   └── dashboard/         ← Templates dashboard Qualiopi (7 onglets)
│   ├── static/
│   │   ├── css/               ← Styles dashboard Qualiopi
│   │   ├── js/                ← JS dashboard
│   │   └── images/            ← Logo MF pour les PDFs
│   ├── management/
│   │   └── commands/
│   │       ├── seed_rss_sources.py    ← Initialiser les sources de veille
│   │       ├── seed_email_templates.py ← Initialiser les 17 templates email
│   │       ├── migrate_from_lms.py    ← Migration depuis mission_central_admin
│   │       └── generate_scorecard.py  ← Generer le scorecard manuellement
│   ├── routers.py             ← DATABASE_ROUTER (PostgreSQL + MySQL read-only)
│   ├── celery_config.py       ← Celery beat schedule
│   └── settings.py            ← Settings Django
├── lms_data/                  ← Modeles unmanaged OpenEdX (lecture seule)
│   ├── models.py              ← LmsUser, CourseEnrollment, CourseGrade, etc.
│   └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── tests/
│   ├── test_models.py
│   ├── test_api.py
│   ├── test_pdf.py
│   ├── test_workflows.py
│   ├── test_scorecard.py
│   └── conftest.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       ├── deploy-prod.yml
│       └── release.yml
├── README.md
└── .env.example
```

---

### 3. mission-odoo

**Role** : Modules Odoo custom pour Mission Formations
**Visibilite** : Prive
**Deploy** : Odoo.sh (deploy auto via Git)

```
mission-odoo/
├── mission_formations/        ← Module Odoo principal
│   ├── __manifest__.py        ← Manifest du module
│   ├── models/
│   │   ├── product_template.py ← Champs custom sur les produits (course_id, duree, modalite)
│   │   ├── sale_order.py      ← Logique webhook a la confirmation commande
│   │   ├── account_move.py    ← Logique webhook a la creation facture
│   │   └── res_partner.py     ← Champs custom contacts (type apprenant/OPCO/formateur)
│   ├── views/
│   │   ├── product_views.xml  ← UI custom produits
│   │   ├── sale_views.xml     ← UI custom devis/commandes
│   │   └── partner_views.xml  ← UI custom contacts
│   ├── data/
│   │   ├── pipeline_stages.xml ← Etapes pipeline CRM
│   │   └── email_templates.xml ← Templates email Odoo brandes MF
│   ├── reports/
│   │   ├── report_invoice.xml ← Facture brandee Mission Formations
│   │   ├── report_saleorder.xml ← Devis brande Mission Formations
│   │   └── header_footer.xml ← Header/footer communs (logo, mentions legales)
│   ├── controllers/
│   │   └── webhooks.py        ← Endpoints webhook sortants (→ Qualiopi)
│   ├── security/
│   │   └── ir.model.access.csv
│   └── static/
│       └── description/
│           └── icon.png       ← Icone du module
├── tests/
│   ├── test_webhooks.py
│   └── test_reports.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── README.md
└── requirements.txt
```

---

### 4. mission-chatwoot

**Role** : Configuration WeWill (Chatwoot self-hosted)
**Visibilite** : Prive
**Deploy** : VPS separe ou meme VPS (Docker)

```
mission-chatwoot/
├── docker-compose.yml         ← 4 services (rails, sidekiq, postgres, redis)
├── .env.example               ← Template (jamais les vrais secrets)
├── branding/
│   ├── logo-mission.png       ← Logo Mission Formations
│   ├── apply-branding.sh      ← Script : copier logo + set INSTALLATION_NAME
│   └── README.md              ← Instructions branding
├── backup/
│   ├── backup.sh              ← Script backup PostgreSQL WeWill
│   └── restore.sh             ← Script restauration
├── docs/
│   ├── INSTALLATION.md        ← Guide d'installation
│   ├── EXPLOITATION.md        ← Guide d'exploitation (demarrer, arreter, logs)
│   └── MIGRATION_PROD.md      ← Checklist migration staging → prod
├── .github/
│   └── workflows/
│       └── deploy.yml
└── README.md
```

---

### 5. mission-site

**Role** : Site internet vitrine missionformations.com
**Visibilite** : Prive
**Deploy** : Vercel / Netlify / VPS

```
mission-site/
├── src/                       ← Code source du site
│   ├── pages/
│   ├── components/
│   ├── styles/
│   └── assets/
├── public/
│   ├── images/
│   └── favicon.ico
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── package.json               ← (si framework JS)
├── README.md
└── .env.example
```

**Note** : la stack du site reste a definir (Next.js, Hugo, HTML statique, WordPress headless, etc.)

---

### 6. mission-docs

**Role** : Documentation technique transverse
**Visibilite** : Prive (ou public si tu veux partager)
**Deploy** : Aucun (ou GitHub Pages optionnel)

```
mission-docs/
├── architecture/
│   ├── PROCESS_COMPLET_MISSION_FORMATIONS.md
│   ├── STRATEGIE_CICD_MULTI_REPOS.md
│   └── ORGANISATION_MULTI_REPOS.md    ← Ce fichier
├── qualiopi/
│   ├── EPIC_MODULE_QUALIOPI.md
│   ├── CAHIER_DES_CHARGES_QUALIOPI.md
│   ├── AUTOMATISATIONS_QUALIOPI.md
│   └── SPECIFICATION_API.md
├── odoo/
│   └── CAHIER_DES_CHARGES_ODOO.md
├── chatwoot/
│   ├── CAHIER_DES_CHARGES_CHATWOOT.md
│   ├── EPIC_FORK_WEWILL.md
│   └── ETAT_ACTUEL.md
├── changelogs/
│   ├── CHANGELOG_2026-03-16.md
│   ├── CHANGELOG_2026-03-17.md
│   └── CHANGELOG_2026-03-18.md
├── todo/
│   ├── TODO_MISE_EN_PROD.md
│   └── TODO_DASHBOARD_APPRENANT.md
├── FAQ_technique/
│   └── FAQ_RESOLUTION_PROBLEMES_TECHNIQUES.md
├── prompts/                   ← Prompts IA (optionnel, peut rester .gitignore)
│   ├── prompt_architecture_qualiopi.txt
│   └── prompt_review_api_qualiopi.txt
├── demo/
│   └── COMPTES_DEMO.md
├── ROADMAP_UNIFIEE.md
└── README.md                  ← Index de toute la documentation
```

---

### 7. mission-admin

**Role** : Documents administratifs de l'organisme de formation
**Visibilite** : PRIVE (jamais public)
**Deploy** : Aucun

```
mission-admin/
├── contrats/
│   ├── clients/               ← Conventions signees par client
│   ├── formateurs/            ← Contrats formateurs (salaries + independants)
│   ├── sous-traitants/        ← Conventions de sous-traitance
│   └── templates/             ← Modeles vierges (Word/PDF)
├── opco/
│   ├── dossiers/              ← Dossiers de prise en charge par OPCO
│   ├── bilans/                ← Bilans pedagogiques envoyes
│   └── contacts.md            ← Liste des OPCO et contacts
├── comptabilite/
│   ├── factures/              ← Factures emises (export Odoo)
│   ├── fec/                   ← Fichiers des Ecritures Comptables
│   └── tva/                   ← Declarations TVA / exoneration
├── rh/
│   ├── formateurs/            ← CV, diplomes, certifications
│   ├── plan-formation/        ← Plan de formation des formateurs
│   └── entretiens/            ← Entretiens professionnels
├── legal/
│   ├── cgv.md                 ← Conditions Generales de Vente
│   ├── rgpd/                  ← Politique RGPD, registre traitements, DPO
│   ├── reglement-interieur.md ← Reglement interieur OF
│   ├── declaration-activite/  ← N° DA, prefet, renouvellements
│   └── assurance/             ← RC Pro, assurance locaux
├── qualiopi/
│   ├── certificat/            ← Certificat Qualiopi (scan)
│   ├── rapports-audit/        ← Rapports d'audit initial + surveillance
│   ├── plan-amelioration/     ← Plans d'amelioration annuels
│   └── revue-direction/       ← PV des revues de direction
├── business/
│   └── template accompagnement UP - business plan enrichi.xlsx
├── .gitignore                 ← Ignorer les fichiers sensibles
└── README.md
```

**IMPORTANT** : ce repo est **strictement prive**. Il contient des donnees personnelles (RGPD), des contrats et des informations financieres. Jamais public.

---

### 8. mission-org

**Role** : Organisation interne, strategie, pilotage
**Visibilite** : PRIVE
**Deploy** : Aucun

```
mission-org/
├── strategie/
│   ├── business-plan.md       ← Vision, marche, positionnement
│   ├── objectifs-2026.md      ← OKRs / objectifs annuels
│   └── roadmap-produit.md     ← Roadmap fonctionnelle (pas technique)
├── commercial/
│   ├── prospection/           ← Pipeline prospects, leads, suivi
│   ├── tarifs.md              ← Grille tarifaire par formation
│   ├── argumentaire.md        ← Arguments de vente
│   └── partenaires.md         ← Partenaires actifs et prospects
├── reunions/
│   ├── 2026-03-19.md          ← CR de reunion
│   ├── 2026-03-20.md
│   └── templates/             ← Template de CR
├── kpis/
│   ├── dashboard.md           ← KPIs business suivis
│   ├── 2026-Q1.md             ← Bilan trimestriel
│   └── 2026-Q2.md
├── processus/
│   ├── onboarding-client.md   ← Processus d'accueil client
│   ├── onboarding-formateur.md ← Processus d'accueil formateur
│   ├── gestion-reclamation.md ← Processus de gestion des reclamations
│   └── facturation.md         ← Processus de facturation
├── veille/
│   ├── concurrents.md         ← Benchmark concurrentiel
│   └── marche.md              ← Tendances du marche de la formation
└── README.md
```

---

## PLAN DE MIGRATION DEPUIS LE MONOREPO

### Etape 1 — Creer l'organisation GitHub (5 min)

```bash
# Via l'interface GitHub : github.com/organizations/new
# Nom : MissionFormations
# Plan : Free (suffisant)
```

### Etape 2 — Creer les 8 repos vides (10 min)

```bash
gh repo create MissionFormations/openedx-platform --private
gh repo create MissionFormations/mission-qualiopi --private
gh repo create MissionFormations/mission-odoo --private
gh repo create MissionFormations/mission-chatwoot --private
gh repo create MissionFormations/mission-site --private
gh repo create MissionFormations/mission-docs --private
gh repo create MissionFormations/mission-admin --private
gh repo create MissionFormations/mission-org --private
```

### Etape 3 — Migrer openedx-platform (30 min)

```bash
# Ajouter le nouveau remote
cd ~/edx-platform
git remote add org git@github.com:MissionFormations/openedx-platform.git

# Pousser toutes les branches
git push org --all
git push org --tags

# Optionnel : changer origin
git remote set-url origin git@github.com:MissionFormations/openedx-platform.git
```

### Etape 4 — Peupler mission-docs (30 min)

```bash
# Creer le repo local
mkdir ~/mission-docs && cd ~/mission-docs
git init

# Copier les docs depuis edx-platform
cp -r ~/edx-platform/docs/qualiopi/ qualiopi/
cp -r ~/edx-platform/docs/odoo/ odoo/
cp -r ~/edx-platform/docs/chatwoot/ chatwoot/
cp -r ~/edx-platform/docs/chat-v2/ chatwoot/  # fusionner avec chatwoot/
cp -r ~/edx-platform/docs/architecture/ architecture/
cp -r ~/edx-platform/docs/changelogs/ changelogs/
cp -r ~/edx-platform/docs/todo/ todo/
cp -r ~/edx-platform/docs/FAQ_technique/ FAQ_technique/
cp -r ~/edx-platform/docs/business/ business/  # sera deplace vers mission-admin apres
cp ~/edx-platform/docs/ROADMAP_UNIFIEE.md .
cp -r ~/edx-platform/prompts/ prompts/
cp -r ~/edx-platform/demo/ demo/

# Creer le README index
# (a rediger)

git add -A
git commit -m "feat: initialisation mission-docs — documentation technique transverse"
git remote add origin git@github.com:MissionFormations/mission-docs.git
git push -u origin main
```

### Etape 5 — Peupler mission-admin (15 min)

```bash
mkdir ~/mission-admin && cd ~/mission-admin
git init

# Creer la structure
mkdir -p contrats/{clients,formateurs,sous-traitants,templates}
mkdir -p opco/{dossiers,bilans}
mkdir -p comptabilite/{factures,fec,tva}
mkdir -p rh/{formateurs,plan-formation,entretiens}
mkdir -p legal/{rgpd,declaration-activite,assurance}
mkdir -p qualiopi/{certificat,rapports-audit,plan-amelioration,revue-direction}
mkdir -p business

# Deplacer le business plan
cp ~/edx-platform/docs/business/*.xlsx business/

# Creer le README
# (a rediger)

# Creer le .gitignore (exclure les fichiers sensibles trop gros)
echo "*.zip" >> .gitignore
echo "*.bak" >> .gitignore

git add -A
git commit -m "feat: initialisation mission-admin — documents administratifs OF"
git remote add origin git@github.com:MissionFormations/mission-admin.git
git push -u origin main
```

### Etape 6 — Peupler mission-org (15 min)

```bash
mkdir ~/mission-org && cd ~/mission-org
git init

mkdir -p strategie commercial/{prospection} reunions/templates kpis processus veille

# Creer les fichiers initiaux
# (a rediger plus tard)

git add -A
git commit -m "feat: initialisation mission-org — organisation interne"
git remote add origin git@github.com:MissionFormations/mission-org.git
git push -u origin main
```

### Etape 7 — Peupler mission-chatwoot (15 min)

```bash
mkdir ~/mission-chatwoot && cd ~/mission-chatwoot
git init

mkdir -p branding backup docs

# Creer le docker-compose et la doc depuis les infos existantes
# (docker-compose = copie de /root/chatwoot/ sur le serveur)

git add -A
git commit -m "feat: initialisation mission-chatwoot — config WeWill Docker"
git remote add origin git@github.com:MissionFormations/mission-chatwoot.git
git push -u origin main
```

### Etape 8 — Initialiser mission-qualiopi (quand Sprint 1 demarre)

```bash
mkdir ~/mission-qualiopi && cd ~/mission-qualiopi
django-admin startproject qualiopi_project .
# Structure detaillee dans ce document (voir section 2)
```

### Etape 9 — Initialiser mission-odoo (quand Sprint 3 demarre)

```bash
# Creer le module Odoo via scaffold ou manuellement
```

### Etape 10 — Nettoyer openedx-platform (apres migration docs)

```bash
# Supprimer les docs migrees du repo openedx-platform
cd ~/edx-platform
rm -rf docs/qualiopi docs/odoo docs/chatwoot docs/chat-v2
rm -rf docs/architecture docs/changelogs docs/todo
rm -rf docs/FAQ_technique docs/business docs/ROADMAP_UNIFIEE.md
rm -rf prompts/ demo/
git add -A
git commit -m "chore: nettoyage post-migration — docs deplacees vers mission-docs"
```

---

## MATRICE DE RESPONSABILITE

| Repo | CI | CD Staging | CD Prod | Release notes | Secrets |
|------|-----|-----------|---------|---------------|---------|
| openedx-platform | Tests + lint | SSH deploy auto | SSH deploy auto | Auto | SSH, serveur |
| mission-qualiopi | Tests + lint + build Docker | Docker pull auto | Docker pull auto | Auto | SSH, DB, HMAC, S3, SMTP |
| mission-odoo | Lint | Odoo.sh auto | Odoo.sh auto | Auto | Odoo.sh gere |
| mission-chatwoot | — | SSH deploy | SSH deploy | Auto | SSH, DB |
| mission-site | Lint + build | Deploy auto | Deploy auto | Auto | Deploy token |
| mission-docs | Markdown lint | — | — | Changelog | — |
| mission-admin | — | — | — | — | — |
| mission-org | — | — | — | — | — |

---

## LIENS ENTRE LES REPOS

```
openedx-platform ◄──webhook──► mission-qualiopi ◄──API──► mission-odoo
       │                              │                         │
       │ widget JS                    │ webhook                 │ webhook
       ▼                              ▼                         │
mission-chatwoot ──────webhook──► mission-qualiopi ◄────────────┘
                                      │
                                      │ donnees
                                      ▼
                               mission-docs (reference)
                               mission-admin (preuves Qualiopi)
                               mission-org (pilotage)
```

---

## CALENDRIER DE CREATION DES REPOS

| Quand | Repos a creer | Raison |
|-------|---------------|--------|
| **Sprint 0** (maintenant) | Organisation GitHub + mission-docs + mission-admin + mission-org | Ranger la doc, commencer propre |
| **Sprint 0** | Migrer openedx-platform vers l'org | Centraliser |
| **Sprint 0** | mission-chatwoot | Externaliser la config WeWill |
| **Sprint 1** | mission-qualiopi | Debut du developpement app Qualiopi |
| **Sprint 3** | mission-odoo | Debut de la config Odoo |
| **Sprint 5+** | mission-site | Quand le site est pret a etre developpe |
