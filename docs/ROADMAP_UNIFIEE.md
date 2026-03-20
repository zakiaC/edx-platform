# Roadmap unifiee — Mission Formations

> Version 1.0 — 19 mars 2026
> 4 chantiers : Infrastructure + Qualiopi + Odoo + Chat
> Contexte : developpeur solo, VPS 16 Go → 32 Go, apprenants payants a venir

---

## VUE D'ENSEMBLE

```
MARS 2026                                                          JUILLET 2026
  │                                                                      │
  ▼                                                                      ▼
  Sprint 0    Sprint 1    Sprint 2    Sprint 3    Sprint 4    Sprint 5    Sprint 6
  INFRA       FONDATIONS  QUALIOPI    ODOO        CONNEXIONS  CONTENU     GO LIVE
  2 sem.      2 sem.      3 sem.      2 sem.      2 sem.      2 sem.     1 sem.
  │           │           │           │           │           │          │
  ├ VPS 32Go  ├ App Qual.  ├ 22 PDFs   ├ Odoo.sh   ├ Webhooks  ├ Formations ├ Prod
  ├ Tuning DB ├ 20 modeles ├ 7 onglets ├ Produits  ├ Dashboard ├ Tests     ├ DNS
  ├ Crisp     ├ SSO/JWT   ├ Alertes   ├ Pipeline  ├ Facturation├ Guides   ├ SSL
  ├ S3 Storage├ Celery    ├ Formulaires├ Contacts  ├ E-commerce├ Charge   ├ Backup
  └ Kill CW   └ CI/CD    └ Tests     └ Branding  └ Bilan fin.└ Audit    └ Monitoring
```

**Duree totale estimee : 14 semaines (~3.5 mois)**
**Effort estime : ~250-300 heures**

---

## SPRINT 0 — INFRASTRUCTURE ET DESENGORGEMENT (Semaines 1-2)

> Objectif : liberer de la RAM, securiser la base, preparer le terrain

### Semaine 1 — Diagnostic et tuning

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S0-01 | `docker stats --no-stream` sur le serveur → mesurer la RAM reelle par container | 15min | — |
| S0-02 | MongoDB : fixer `cacheSizeGB: 0.5` dans la config Tutor | 30min | S0-01 |
| S0-03 | MySQL : `innodb_buffer_pool_size = 1G` | 30min | S0-01 |
| S0-04 | Redis : `maxmemory 512mb` + politique `volatile-lru` | 15min | S0-01 |
| S0-05 | Meilisearch : `MEILI_MAX_INDEXING_MEMORY=200Mb` | 15min | S0-01 |
| S0-06 | Mesure post-tuning → objectif < 65% RAM | 15min | S0-02 a S0-05 |
| S0-07 | Desactiver les MFEs non utilises (Communications, ORA Grading si pas de peer review) | 30min | — |

**Critere de sortie semaine 1 : RAM < 65% sur 16 Go**

### Semaine 2 — Externalisation et upgrade

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S0-08 | Creer le compte Crisp (workspace Mission Formations) | 30min | — |
| S0-09 | Configurer le widget Crisp (couleurs MF, textes FR, bot pre-qualification) | 1h | S0-08 |
| S0-10 | Remplacer le widget Chatwoot par Crisp dans `footer.html` | 30min | S0-09 |
| S0-11 | Identification user connecte dans Crisp (email, nom) | 30min | S0-10 |
| S0-12 | Arreter les 4 containers Chatwoot (rails, sidekiq, postgres, redis) | 15min | S0-10 |
| S0-13 | Exporter les conversations Chatwoot existantes (API, archivage) | 1h | S0-12 |
| S0-14 | Supprimer le plugin Tutor `mission_wewill.py` + config Caddy | 15min | S0-12 |
| S0-15 | Supprimer les volumes Docker Chatwoot + nettoyer DNS | 15min | S0-14 |
| S0-16 | Commander et activer le VPS 32 Go OVH (upgrade ou migration) | 1h | — |
| S0-17 | Creer le bucket OVH Object Storage (S3-compatible) | 30min | — |
| S0-18 | Configurer `django-storages` dans OpenEdX pour les medias/videos → S3 | 2h | S0-17 |
| S0-19 | Creer le user MySQL read-only `qualiopi_ro` (GRANT SELECT on openedx.*) | 15min | — |
| S0-20 | Mesure finale RAM sur 32 Go → valider le headroom | 15min | S0-16 |

**Critere de sortie Sprint 0 :**
- VPS 32 Go operationnel
- RAM < 50% (objectif)
- Chatwoot supprime, Crisp fonctionnel
- Object Storage S3 configure
- User MySQL read-only cree

**Effort Sprint 0 : ~10-12 heures**

---

## SPRINT 1 — FONDATIONS APP QUALIOPI (Semaines 3-4)

> Objectif : app Django Qualiopi operationnelle, connectee a OpenEdX, deployable

### Semaine 3 — Squelette technique

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S1-01 | Creer le repo `mission-qualiopi` (Django 5.x) | 30min | — |
| S1-02 | Dockerfile + docker-compose.yml (Gunicorn 3 workers + PostgreSQL + Celery + Redis) | 2h | S1-01 |
| S1-03 | Integrer le container dans le reseau Docker Tutor | 1h | S1-02 |
| S1-04 | Configurer le DATABASE_ROUTER (PostgreSQL Qualiopi + MySQL OpenEdX read-only) | 2h | S0-19, S1-02 |
| S1-05 | Verifier les requetes read-only sur les 5 tables OpenEdX stables | 1h | S1-04 |
| S1-06 | Routing Caddy : `/qualiopi/*` → container Qualiopi | 30min | S1-03 |
| S1-07 | Auth simple (Django auth + IP whitelist) pour le jour 1 | 1h | S1-02 |
| S1-08 | Health check endpoint `/qualiopi/health` → 200 | 15min | S1-06 |

### Semaine 4 — Modeles et CI/CD

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S1-09 | Creer les 20 modeles Django (voir cahier des charges Qualiopi) | 4h | S1-04 |
| S1-10 | Modeles unmanaged (managed=False) pour les tables OpenEdX en lecture | 1h | S1-05 |
| S1-11 | Migrations initiales PostgreSQL | 30min | S1-09 |
| S1-12 | Django Admin basique pour tous les modeles (CRUD gratuit) | 2h | S1-09 |
| S1-13 | Configurer Celery + Redis (queue dediee `qualiopi`) | 1h | S1-02 |
| S1-14 | Script de deploiement `deploy-qualiopi.sh` (docker build + restart) | 1h | S1-02 |
| S1-15 | CI basique (tests + lint sur push) | 1h | S1-01 |
| S1-16 | Migrer les 2 PDFs existants (attestation + rapport de suivi) depuis mission_central_admin | 2h | S1-09, S1-13 |
| S1-17 | Charte graphique PDF Mission Formations (styles ReportLab communs) | 2h | S1-16 |

**Critere de sortie Sprint 1 :**
- `curl https://staging.mf.com/qualiopi/health` → 200
- 20 modeles migres dans PostgreSQL
- 2 PDFs existants fonctionnels dans l'app Qualiopi
- Celery operationnel
- Django Admin fonctionnel pour tous les modeles

**Effort Sprint 1 : ~20-22 heures**

---

## SPRINT 2 — MODULE QUALIOPI COMPLET (Semaines 5-7)

> Objectif : 22 PDFs brandes, 7 onglets dashboard, alertes, formulaires apprenants

### Semaine 5 — PDFs (lot 1 : documents contractuels et parcours)

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S2-01 | DOC-01 : Programme de formation (depuis structure OLX) | 3h | S1-16, S1-17 |
| S2-02 | DOC-02 : Convention de formation B2B | 2h | S1-17 |
| S2-03 | DOC-03 : Contrat de formation individuel | 1.5h | S1-17 |
| S2-04 | DOC-04 : Convocation du stagiaire | 1.5h | S1-17 |
| S2-05 | DOC-05 : Reglement interieur (template statique avec variables) | 2h | S1-17 |
| S2-06 | DOC-06 : Feuille d'emargement (paysage, logs de connexion) | 3h | S1-10 |
| S2-07 | DOC-08 : Certificat de realisation (modele Caisse des Depots) | 2h | S1-17 |
| S2-08 | DOC-15 : Livret d'accueil du stagiaire | 2h | S1-17 |

**Sous-total semaine 5 : ~17h (8 PDFs)**

### Semaine 6 — PDFs (lot 2 : evaluations + qualite) + formulaires

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S2-09 | DOC-09 : Evaluation pre-formation (PDF + formulaire apprenant) | 3h | S1-09 |
| S2-10 | DOC-10 : Evaluation post-formation (PDF + comparaison pre/post) | 3h | S2-09 |
| S2-11 | DOC-11 : Enquete satisfaction a chaud (formulaire + PDF synthese) | 4h | S1-09 |
| S2-12 | DOC-12 : Enquete satisfaction a froid (formulaire + PDF synthese) | 2h | S2-11 |
| S2-13 | DOC-16 : Attestation d'assiduite | 1h | S1-10 |
| S2-14 | DOC-17 : PV de reunion pedagogique | 1.5h | S1-17 |
| S2-15 | DOC-18 : Fiche formateur | 1.5h | S1-17 |
| S2-16 | DOC-19 : Convention de sous-traitance | 1.5h | S1-17 |
| S2-17 | DOC-20 : Recepisse de reclamation (generation auto) | 1h | S1-09 |
| S2-18 | DOC-21 : Plan d'amelioration annuel | 1.5h | S1-17 |
| S2-19 | DOC-22 : Revue de direction | 1.5h | S1-17 |

**Sous-total semaine 6 : ~21.5h (11 PDFs + 3 formulaires)**

### Semaine 7 — Dashboard Qualiopi (7 onglets) + alertes

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S2-20 | Vue d'ensemble : scorecard 32 indicateurs (vert/orange/rouge) | 4h | S1-09, S1-10 |
| S2-21 | Onglet C1 — Information du public (Ind. 1-4) : checklists + config | 2h | S1-09 |
| S2-22 | Onglet C2 — Analyse des besoins (Ind. 5-8) : statut par apprenant | 3h | S2-09 |
| S2-23 | Onglet C3 — Suivi et evaluation (Ind. 9-14) : donnees auto + registres | 4h | S2-06, S2-11 |
| S2-24 | Onglet C4 — Moyens pedagogiques (Ind. 15-19) : checklists + CRUD | 2h | S1-09 |
| S2-25 | Onglet C5 — Qualification formateurs (Ind. 20-23) : CRUD + uploads | 2h | S2-15 |
| S2-26 | Onglet C6 — Veille et environnement pro (Ind. 24-30) : CRUD + journal | 3h | S1-09 |
| S2-27 | Onglet C7 — Appreciations et reclamations (Ind. 31-32) : CRUD + SLA | 2h | S2-17 |
| S2-28 | Systeme d'alertes : notifications quand KPI non atteint ou echeance proche | 3h | S2-20 |
| S2-29 | DOC-14 : Bilan de formation ZIP (agregation de tous les PDFs) | 3h | S2-01 a S2-19 |
| S2-30 | Bouton "Dossier auditeur" (ZIP complet pour un audit Qualiopi) | 2h | S2-29 |
| S2-31 | Theming dashboard Qualiopi (meme design que mission-theme) | 3h | S2-20 |
| S2-32 | Tests unitaires : modeles, PDFs, routes, alertes | 4h | Tout |

**Sous-total semaine 7 : ~37h**

**Critere de sortie Sprint 2 :**
- 22 PDFs generables avec design Mission Formations
- 7 onglets + vue d'ensemble scorecard
- Formulaires apprenants (eval pre/post, satisfaction)
- Systeme d'alertes fonctionnel
- ZIP auditeur generee en async via Celery
- Tests unitaires > 80% couverture sur les modeles et PDFs

**Effort Sprint 2 : ~75 heures (3 semaines intensives)**

---

## SPRINT 3 — ODOO (Semaines 8-9)

> Objectif : Odoo operationnel, pipeline CRM, produits, contacts, branding

### Semaine 8 — Setup Odoo et configuration

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S3-01 | Creer le compte Odoo.sh (plan Standard) | 30min | — |
| S3-02 | Configurer la societe Mission Formations (SIRET, N° DA, logo, adresse) | 1h | S3-01 |
| S3-03 | Installer les modules : CRM, Ventes, Facturation, Contacts, Signature | 30min | S3-01 |
| S3-04 | Creer les produits (10 formations initiales, avec course_id custom) | 2h | S3-03 |
| S3-05 | Configurer le pipeline CRM (6 etapes : lead → gagne/perdu) | 1h | S3-03 |
| S3-06 | Creer les categories de contacts (apprenant, entreprise, OPCO, formateur) | 1h | S3-03 |
| S3-07 | Importer les contacts existants (formateurs, academies B2B) | 1h | S3-06 |
| S3-08 | Configurer la facturation (comptes, TVA, exoneration formation pro) | 2h | S3-03 |
| S3-09 | Configurer la mention Qualiopi sur les factures et devis | 30min | S3-08 |

### Semaine 9 — Branding et workflow

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S3-10 | Personnaliser les templates PDF Odoo (devis, factures) : header/footer MF | 3h | S3-02 |
| S3-11 | Template convention de formation dans Odoo (ou lien vers Qualiopi) | 2h | S3-10 |
| S3-12 | Configurer les emails transactionnels Odoo (confirmation, relance) avec branding MF | 1h | S3-02 |
| S3-13 | Creer les regles d'automatisation : commande confirmee → action server (webhook) | 2h | S3-05 |
| S3-14 | Creer les regles d'automatisation : paiement recu → action server (webhook) | 2h | S3-08 |
| S3-15 | Configurer Stripe dans Odoo (paiement CB en ligne) | 2h | S3-08 |
| S3-16 | Tester le workflow complet : lead → devis → signature → commande → facture → paiement | 2h | S3-13, S3-14 |
| S3-17 | Documentation : guide admin Odoo pour l'equipe MF | 2h | S3-16 |

**Critere de sortie Sprint 3 :**
- Odoo.sh operationnel avec 10 produits/formations
- Pipeline CRM fonctionnel
- Devis et factures brandes Mission Formations
- Regles d'automatisation webhook prets (pas encore connectes)
- Stripe configure

**Effort Sprint 3 : ~24 heures**

---

## SPRINT 4 — CONNEXIONS INTER-SERVICES (Semaines 10-11)

> Objectif : les 4 services communiquent entre eux via webhooks

### Semaine 10 — Webhooks entrants (vers OpenEdX et Qualiopi)

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S4-01 | Endpoint OpenEdX : `POST /api/webhook/odoo/enrollment` (commande confirmee → enrollment) | 3h | S3-13 |
| S4-02 | Securite webhook : signature HMAC + IP whitelist | 1h | S4-01 |
| S4-03 | Logique : creer le user OpenEdX si inexistant + enrollment + academy B2B | 3h | S4-01 |
| S4-04 | Endpoint Qualiopi : `POST /api/webhook/odoo/payment` (paiement → convocation) | 2h | S3-14 |
| S4-05 | Logique : generer la convocation (DOC-04) + envoi email au stagiaire | 2h | S4-04, S2-04 |
| S4-06 | Endpoint Qualiopi : `POST /api/webhook/odoo/convention` (convention signee → registre) | 1h | S4-04 |
| S4-07 | Endpoint Qualiopi : `POST /api/webhook/crisp/conversation` (tag reclamation → registre) | 2h | S0-08 |
| S4-08 | Configurer le webhook Crisp → Odoo (nouvelle conversation → lead CRM) | 1h | S0-08, S3-05 |
| S4-09 | Tests d'integration : Odoo commande → enrollment OpenEdX | 2h | S4-03 |

### Semaine 11 — Dashboard admin connecte + webhooks sortants

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S4-10 | API Qualiopi → Odoo : recuperer CA, factures, frais formateurs | 3h | S3-08 |
| S4-11 | Cache Redis des donnees Odoo (refresh toutes les 15 min) | 1h | S4-10 |
| S4-12 | Dashboard admin LMS : connecter l'onglet "Revenus" aux donnees Odoo | 2h | S4-10 |
| S4-13 | Dashboard admin LMS : connecter l'onglet "Factures" aux donnees Odoo | 2h | S4-10 |
| S4-14 | Dashboard admin LMS : connecter l'onglet "Frais formateurs" aux donnees Odoo | 2h | S4-10 |
| S4-15 | Dashboard admin LMS : CA hero (overview) connecte a Odoo | 1h | S4-10 |
| S4-16 | Webhook OpenEdX → Odoo : certificat obtenu → MAJ fiche contact | 2h | — |
| S4-17 | Webhook Qualiopi → Odoo : abandon detecte → MAJ fiche contact (risque perte) | 1h | S2-28 |
| S4-18 | Integration iframe ou lien SSO : dashboard LMS → app Qualiopi | 2h | S1-07 |
| S4-19 | Tests end-to-end : parcours complet lead → paiement → enrollment → formation → certificat | 3h | Tout |

**Critere de sortie Sprint 4 :**
- Webhook Odoo → OpenEdX : enrollment automatique a la commande
- Webhook Odoo → Qualiopi : convocation auto au paiement
- Webhook Crisp → Odoo : lead auto a chaque conversation
- Dashboard admin : onglets Revenus/Factures/Frais connectes aux donnees reelles Odoo
- Lien/iframe vers le dashboard Qualiopi depuis le LMS
- Test E2E valide

**Effort Sprint 4 : ~30 heures**

---

## SPRINT 5 — CONTENU, TESTS, DOCUMENTATION (Semaines 12-13)

> Objectif : formations pretes, tests de charge, guides utilisateurs

### Semaine 12 — Contenu et formations

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S5-01 | Creer 8 formations dans Studio (structure OLX : chapters, sequentials, verticals) | 8h | — |
| S5-02 | Contenu HTML par module (textes, objectifs, exemples) | 8h | S5-01 |
| S5-03 | Quiz par chapitre (QCM, 3-5 questions par chapitre) | 4h | S5-01 |
| S5-04 | Images de cours (banniere, thumbnail) | 2h | S5-01 |
| S5-05 | Descriptions des cours (short_description + overview dans Studio) | 2h | S5-01 |
| S5-06 | Rattacher les cours aux academies (AcademyCourse) | 1h | S5-01 |
| S5-07 | Synchroniser les 10 formations dans les produits Odoo | 1h | S5-01, S3-04 |
| S5-08 | Uploader les videos sur OVH Object Storage + configurer les URLs dans Studio | 4h | S0-18 |

### Semaine 13 — Tests et documentation

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S5-09 | Tests de charge avec Locust : 50 apprenants simultanes | 3h | S5-01 |
| S5-10 | Objectif : < 3s par page, 0 erreur 500 sous charge | — | S5-09 |
| S5-11 | Tests des 22 PDFs Qualiopi (generation + contenu correct) | 2h | S2 |
| S5-12 | Test smoke : toutes les pages publiques retournent 200 | 1h | — |
| S5-13 | Test parcours apprenant complet (inscription → cours → quiz → certificat) | 2h | S5-01 |
| S5-14 | Test parcours admin complet (dashboard → Qualiopi → PDF → ZIP) | 2h | S2 |
| S5-15 | Test parcours formateur (dashboard → cours → apprenants → rapport) | 1h | — |
| S5-16 | Guide apprenant (page /aide/ enrichie + PDF telecharge) | 4h | — |
| S5-17 | Guide formateur (Studio + dashboard + rapports) | 4h | — |
| S5-18 | Guide admin (dashboard + Qualiopi + Odoo + utilisateurs) | 3h | — |
| S5-19 | Procedure de mise en prod complete (etape par etape) | 2h | — |
| S5-20 | Monitoring : Netdata ou Grafana sur le VPS (RAM, CPU, containers) | 2h | — |

**Critere de sortie Sprint 5 :**
- 10 formations avec contenu reel (dont 2 existantes + 8 nouvelles)
- Videos sur S3/Object Storage
- Tests de charge passes (50 users, < 3s)
- Guides utilisateurs publies
- Monitoring en place

**Effort Sprint 5 : ~48 heures**

---

## SPRINT 6 — GO LIVE (Semaine 14)

> Objectif : mise en production

| # | Tache | Effort | Dependance |
|---|-------|--------|------------|
| S6-01 | Configuration DNS production (academie.missionformations.com) | 1h | — |
| S6-02 | Certificat SSL production (Caddy auto ou Let's Encrypt) | 30min | S6-01 |
| S6-03 | DNS wildcard *.academie.missionformations.com | 15min | S6-01 |
| S6-04 | Migration base de donnees staging → production | 2h | — |
| S6-05 | Configuration Odoo production (domaine, stripe prod, emails prod) | 1h | — |
| S6-06 | Configuration Crisp production (domaine) | 15min | — |
| S6-07 | Rotation des secrets (JWT, Meilisearch, API keys) | 1h | — |
| S6-08 | Backup automatique quotidien (MySQL + MongoDB + PostgreSQL Qualiopi) | 2h | — |
| S6-09 | Cron de renouvellement SSL | 15min | S6-02 |
| S6-10 | Smoke test production (toutes les pages, PDFs, webhooks) | 2h | S6-04 |
| S6-11 | Test avec 5 stagiaires reels (parcours complet) | 3h | S6-10 |
| S6-12 | Runbook incidents production (procedures en cas de panne) | 2h | — |
| S6-13 | Communication : ouverture du site aux apprenants | 1h | S6-11 |

**Critere de sortie Sprint 6 :**
- Site production accessible
- Backup quotidien automatise
- Secrets rotates
- Test avec vrais utilisateurs valide
- Runbook en place

**Effort Sprint 6 : ~16 heures**

---

## RECAPITULATIF PAR SPRINT

| Sprint | Semaines | Focus | Effort | Livrables cles |
|--------|----------|-------|--------|-----------------|
| **S0** | 1-2 | Infra, tuning RAM, Crisp, S3 | ~12h | VPS 32 Go, Chatwoot supprime, RAM < 50% |
| **S1** | 3-4 | App Qualiopi (squelette + modeles) | ~22h | App deployee, 20 modeles, 2 PDFs migres |
| **S2** | 5-7 | Qualiopi complet (22 PDFs + 7 onglets) | ~75h | 22 PDFs, dashboard 32 indicateurs, alertes |
| **S3** | 8-9 | Odoo setup + branding | ~24h | CRM, ventes, facturation, Stripe |
| **S4** | 10-11 | Webhooks + connexions | ~30h | 4 services connectes, dashboard reel |
| **S5** | 12-13 | Contenu + tests + docs | ~48h | 10 formations, tests charge, guides |
| **S6** | 14 | Go live | ~16h | Production operationnelle |
| **TOTAL** | **14 sem.** | | **~227h** | |

---

## BUDGET MENSUEL CIBLE

| Poste | Cout/mois |
|-------|-----------|
| VPS OVH 32 Go (8 vCPU) | ~45-50€ |
| Odoo.sh Standard (3 users) | ~75€ |
| Crisp Pro (2-4 agents) | 0-25€ |
| OVH Object Storage (videos + PDFs) | ~10-15€ |
| Domaine(s) + DNS | ~5€ |
| **Total** | **~135-170€/mois** |

---

## DEPENDANCES CRITIQUES (CHEMIN CRITIQUE)

```
S0 (infra)
  └──► S1 (app Qualiopi)
         └──► S2 (PDFs + dashboard)
                └──► S4 (connexions) ──► S6 (go live)
                       ▲
S3 (Odoo) ─────────────┘
                       ▲
S5 (contenu) ──────────┘
```

**Le chemin critique est : S0 → S1 → S2 → S4 → S6**
- S3 (Odoo) peut demarrer en parallele de S2
- S5 (contenu) peut demarrer en parallele de S4

---

## RISQUES ET MITIGATIONS

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| OOM killer sur 32 Go | Faible | Critique | Monitoring Netdata + alertes RAM > 80% |
| Upgrade VPS = downtime | Moyenne | Moyen | Planifier hors heures, ou migration a chaud OVH |
| API Odoo instable | Faible | Moyen | Cache Redis + retry Celery |
| Webhook perdu (Odoo → OpenEdX) | Moyenne | Eleve | File d'attente + log + retry + alerte si echec |
| Conflit migration OpenEdX upgrade | Moyenne | Eleve | Tables Qualiopi dans PostgreSQL separee (pas dans MySQL OpenEdX) |
| Charge videos saturant le disque | Elevee | Critique | S3 Object Storage obligatoire (jamais sur le VPS) |
| Dev solo = bus factor 1 | Elevee | Critique | Documentation, runbook, backup, CI/CD automatise |

---

## DECISIONS PRISES (19 mars 2026)

| Decision | Choix | Raison |
|----------|-------|--------|
| Architecture Qualiopi | Option C — Hybride (app separee + MySQL read-only) | Consensus 4/5 IA, isolation LMS, dev solo |
| Chat | Crisp (SaaS) remplace Chatwoot self-hosted | RAM liberee, zero maintenance, RGPD France |
| ERP | Odoo.sh (SaaS) | Zero maintenance, modules complets, dev solo |
| Stockage video | OVH Object Storage (S3) | Jamais sur le disque du VPS |
| Generation PDF | Celery async dans le container Qualiopi | Jamais synchrone dans uWSGI LMS |
| VPS | Upgrade 32 Go | Obligatoire avant prod avec apprenants payants |
| Fork WeWill | Abandonne | ROI negatif pour un dev solo |
