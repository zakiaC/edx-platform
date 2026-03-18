# TODO — Mise en production Academie Mission Formations

> Liste exhaustive de TOUT ce qui reste a faire avant la mise en prod.
> A prioriser lors de la session du 19 mars 2026.

---

## 1. CERTIFICATS (20 templates)

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 1.1 | Convertir les 20 designs de certificats en templates Mako OpenEdX | 6h | A faire |
| 1.2 | Script d'injection des templates en BDD (CertificateTemplate) | 1h | A faire |
| 1.3 | Association template → organisation/cours dans Studio | 1h | A faire |
| 1.4 | Tests unitaires (templates valides, variables presentes) | 1h | A faire |
| 1.5 | Documentation (quel template pour quelle formation) | 30min | A faire |
| 1.6 | Activer les certificats HTML dans les settings | 30min | A faire |

---

## 2. PAGES MANQUANTES DANS LE THEME

| # | Page | Template natif | Override theme | Statut |
|---|------|---------------|----------------|--------|
| 2.1 | Page progression cours | `courseware/progress.html` | Non | A faire |
| 2.2 | Page contenu cours (courseware) | `courseware/courseware.html` | Non | A evaluer |
| 2.3 | Page certificat web | `certificates/valid.html` | Non | A faire (lie aux 20 templates) |
| 2.4 | Profil/Compte | MFE account | Non | A evaluer (MFE ou Mako) |

---

## 3. CAHIER DES CHARGES — TACHES RESTANTES

### Sprint 3 (finaliser)

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 3.3 | Middleware sous-domaine (client.academie.mf.com → config academie) | 4h | A faire |
| 3.4 | Theme dynamique CSS par academie (couleurs/logo injectes) | 3h | A faire |

### Sprint 4 — Pages publiques + B2B

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 4.1 | Page publique academie `/academie/{slug}/` | 6h | A faire |
| 4.2 | Dashboard apprenant enrichi (section "Mes Academies") | 4h | A faire |
| 4.3 | Portail RH entreprise B2B (suivi collaborateurs, attestations) | 6h | A faire |
| 4.5 | Integration Odoo (webhook contrat → creation academie auto) | 4h | A faire |

### Sprint 5 — Contenu + Go Live

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 5.1 | Creer les contenus des 10 formations dans Studio | 8h | A faire |
| 5.2 | Rattacher les cours aux academies (AcademyCourse) | 1h | A faire |
| 5.3 | Tests utilisateurs avec 5 stagiaires reels | 3h | A faire |
| 5.4 | Tests de charge (50 users simultanes, < 3s par page) | 2h | A faire |
| 5.5 | Configuration DNS production | 1h | A faire |
| 5.6 | Deploiement production (migration staging → prod) | 3h | A faire |

---

## 4. INFRA / OPS

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 4.1 | Configurer Caddy wildcard SSL (certificat deja genere) | 1h | A faire |
| 4.2 | DNS wildcard *.academie.staging chez OVH | 10min | Fait (a verifier) |
| 4.3 | Migrer le plugin Tutor mission_wewill.py sur le serveur | 30min | A faire |
| 4.4 | Mettre a jour deploy.sh pour le nouveau workflow | 30min | A faire |
| 4.5 | Backup automatique quotidien (MySQL + MongoDB + PostgreSQL WeWill) | 1h | A faire |
| 4.6 | Monitoring (alertes si container down) | 2h | A faire |
| 4.7 | Renouvellement automatique certificat SSL (cron certbot) | 30min | A faire |

---

## 5. CORRECTIONS / DETTE TECHNIQUE

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 5.1 | Site Django ID 2 cree avec domaine temporaire → corriger | 10min | A faire |
| 5.2 | Academy Manager — les academies ne s'affichent pas (test en staging) | 30min | A verifier |
| 5.3 | Page /contact/ retourne 404 (route non montee) | 30min | A debugger |
| 5.4 | Verifier que TOUTES les pages fonctionnent apres le refactoring middleware | 1h | A faire |
| 5.5 | Tester la suppression d'utilisateur depuis la page custom | 15min | A verifier |
| 5.6 | Tester l'envoi d'email depuis le dashboard Tests & QA | 15min | A verifier |
| 5.7 | Migrations fake-applied sans tables (8 apps) | 2h | A evaluer |

---

## 6. ONGLETS / PAGES DU DASHBOARD ADMIN

| # | Onglet | Donnees | Statut |
|---|--------|---------|--------|
| 6.1 | Overview | KPIs reels + revenus hardcodes | Partiel |
| 6.2 | Analytics | Placeholder complet | A connecter |
| 6.3 | Formateurs | Donnees reelles | Fait |
| 6.4 | Apprenants | Donnees reelles | Fait |
| 6.5 | Formations | Donnees reelles | Fait |
| 6.6 | Academies | Supprime → Academy Manager | Fait |
| 6.7 | Planning | Placeholder (calendrier statique) | A connecter |
| 6.8 | Revenus | Placeholder | A connecter (Odoo/ecommerce) |
| 6.9 | Frais formateurs | Placeholder | A connecter |
| 6.10 | Factures | Placeholder | A connecter |
| 6.11 | Notifications | Donnees reelles | Fait |
| 6.12 | Parametres | Placeholder | A connecter |
| 6.13 | Tests & QA | Fonctionnel | Fait |
| 6.14 | Console Django (dropdown) | Liens actifs | Fait |

---

## 7. ONGLETS / PAGES DU DASHBOARD APPRENANT

| # | Section | Statut |
|---|---------|--------|
| 7.1 | Hero (progress rings) | Fonctionnel |
| 7.2 | Recommandations | Hardcode (3 cartes statiques) |
| 7.3 | Statistiques (5 KPIs) | Partiel |
| 7.4 | Mes formations (liste) | Fonctionnel |
| 7.5 | Evenements a venir | Hardcode (3 events statiques) |
| 7.6 | Activite hebdomadaire | Placeholder |
| 7.7 | Certificats | Fonctionnel |
| 7.8 | Badges | Hardcode (6 badges statiques) |
| 7.9 | Notifications | Fonctionnel |
| 7.10 | Section "Mes Academies" | A creer (Sprint 4.2) |

---

## 8. PAGES PUBLIQUES

| # | Page | URL | Statut |
|---|------|-----|--------|
| 8.1 | Homepage | `/` | Fait (design MF) |
| 8.2 | Catalogue | `/catalogue/` | Fait (10 formations) |
| 8.3 | Enrollment (inscription cours) | `/courses/{id}/about` | Fait (design wireframe) |
| 8.4 | Login / Register | `/login`, `/register` | Fait (design MF) |
| 8.5 | Centre d'aide | `/aide/` | Fait (8 guides + FAQ) |
| 8.6 | Contact | `/contact/` | Fait (formulaire email) |
| 8.7 | About | `/about` | Fait (redirect missionformations.com) |
| 8.8 | CGV | `/tos` | Fait (redirect missionformations.com) |
| 8.9 | Mentions legales | `/privacy` | Fait (redirect missionformations.com) |
| 8.10 | Page academie publique | `/academie/{slug}/` | A faire (Sprint 4.1) |
| 8.11 | Portail B2B | `/entreprise/` | A faire (Sprint 4.3) |

---

## 9. EPICS SEPAREES (projets a part)

| Epic | Tickets | Effort | Statut |
|------|---------|--------|--------|
| Fork WeWill (chat) | 9 tickets (CHAT-1 a 9) | ~20h | Planifie |
| Module Qualiopi | 14 tickets (QUA-1 a 14) | ~43h | Planifie |

---

## 10. SECURITE / RGPD

| # | Tache | Effort | Statut |
|---|-------|--------|--------|
| 10.1 | Rotation des secrets JWT + Meilisearch (exposes dans l'historique git) | 1h | A faire |
| 10.2 | Verifier que .secrets.env n'est pas tracke | 5min | Fait |
| 10.3 | Politique de sauvegarde des donnees | 1h | A documenter |
| 10.4 | Procedure de suppression des donnees (RGPD) | 2h | A documenter |
| 10.5 | Verifier les permissions des fichiers sur le serveur | 30min | A faire |

---

## 11. TESTS A AJOUTER

| # | Test | Type | Statut |
|---|------|------|--------|
| 11.1 | Tests des 20 templates de certificats | Unit | A faire |
| 11.2 | Tests de la page catalogue (donnees reelles) | Integration | A faire |
| 11.3 | Tests de la page enrollment (course_about) | Integration | A faire |
| 11.4 | Tests du middleware InactiveUserLogoutMiddleware | Unit | A faire |
| 11.5 | Tests du signal patch_activation_email | Unit | A faire |
| 11.6 | Tests de la redirection /courses → /catalogue/ | Integration | A faire |
| 11.7 | Test smoke: toutes les pages publiques retournent 200 | Smoke | A verifier |

---

## 12. DOCUMENTATION A CREER

| # | Document | Pour qui | Statut |
|---|----------|----------|--------|
| 12.1 | Guide formateur (utilisation Studio + dashboard) | Formateurs | A faire |
| 12.2 | Guide apprenant (inscription, cours, certificat) | Apprenants | A faire |
| 12.3 | Guide admin (dashboard, Academy Manager, utilisateurs) | Admins | A faire |
| 12.4 | Procedure de mise en prod complete | DevOps | Partiel (PRE_DEPLOY_CHECKLIST) |
| 12.5 | Runbook incidents production | DevOps | Partiel (TESTING_STRATEGY) |
| 12.6 | Documentation API (routes custom, endpoints) | Dev | A faire |

---

## 13. DASHBOARDS A REPRENDRE

### Dashboard admin (`/admin/mission-dashboard/`)

| # | Element | Etat actuel | A faire |
|---|---------|-------------|---------|
| 13.1 | Overview — KPIs hero | Apprenants + formateurs reels, CA hardcode | Connecter le CA a Odoo ou ecommerce |
| 13.2 | Overview — Graphique revenus mensuels | Hardcode (6 barres statiques) | Connecter ou supprimer |
| 13.3 | Overview — Donut repartition academies | Donnees reelles | OK |
| 13.4 | Overview — Inscriptions recentes | Donnees reelles | OK |
| 13.5 | Overview — Activite recente | Donnees reelles | OK |
| 13.6 | Analytics — 4 KPIs | Hardcode (156, 78%, 4.2h, 4.5/5) | Connecter aux vrais donnees |
| 13.7 | Analytics — Graphique inscriptions | Hardcode | Connecter |
| 13.8 | Analytics — Taux completion par formation | Hardcode | Connecter |
| 13.9 | Planning — Calendrier | Hardcode (fevrier 2026 statique) | Connecter aux dates des cours |
| 13.10 | Revenus — KPIs + transactions | Tout hardcode | Connecter a Odoo/ecommerce |
| 13.11 | Frais formateurs — Tableau | Tout hardcode | Creer le modele + interface |
| 13.12 | Factures — Tableau | Tout hardcode | Creer le modele + interface |
| 13.13 | Parametres — Formulaire | Tout hardcode | Implementer les vrais settings |
| 13.14 | Design global admin | Fonctionnel mais a affiner | Revoir selon wireframe final |

### Dashboard apprenant (`/dashboard`)

| # | Element | Etat actuel | A faire |
|---|---------|-------------|---------|
| 13.15 | Hero progress rings | Fonctionnel (VTC + IT) | Dynamiser pour toutes les academies |
| 13.16 | Recommandations | 3 cartes hardcodees | Algorithme de recommandation (basé sur academie/progression) |
| 13.17 | Stats (5 KPIs) | Partiellement connecte | Connecter Modules OK, Taux reussite |
| 13.18 | Evenements a venir | 3 events hardcodes | Connecter aux dates des cours |
| 13.19 | Activite hebdomadaire | Barres placeholder | Connecter aux logs de connexion |
| 13.20 | Badges | 6 badges hardcodes | Connecter au systeme de badges OpenEdX |
| 13.21 | Section "Mes Academies" | N'existe pas | Creer (Sprint 4.2) |
| 13.22 | Design dashboard apprenant wireframe | Design MF actuel (different du wireframe v3) | Aligner sur le wireframe si requis |

### Dashboard formateur (`/dashboard` quand is_staff)

| # | Element | Etat actuel | A faire |
|---|---------|-------------|---------|
| 13.23 | Sidebar formateur | Fonctionnel | Revoir les liens et onglets |
| 13.24 | Stats formateur (4 KPIs) | Donnees partielles | Connecter apprenants actifs, taux completion |
| 13.25 | Actions rapides | 4 boutons | Verifier que les liens fonctionnent |
| 13.26 | Formations vendues | Tableau reel | OK |
| 13.27 | Apprenants recents | Tableau reel | OK |
| 13.28 | Calendrier formateur | Hardcode | Connecter aux dates des cours |
| 13.29 | Activite recente formateur | Donnees reelles | OK |
| 13.30 | Acces aux rapports PDF Qualiopi | N'existe pas | Ajouter boutons attestation + suivi |

---

## 14. CUSTOMISATION STUDIO

| # | Element | Etat actuel | A faire |
|---|---------|-------------|---------|
| 14.1 | Footer Studio | Customise (liens MF) | OK |
| 14.2 | Header Studio | Natif OpenEdX | Customiser avec branding MF |
| 14.3 | Page d'accueil Studio | Natif | Customiser (logo, couleurs, textes FR) |
| 14.4 | Sidebar Studio | Natif | Evaluer si customisation necessaire |
| 14.5 | Page creation de cours | Natif | Ajouter les organisations MF dans le dropdown |
| 14.6 | Templates d'email Studio | Natif | Brander avec design Mission |
| 14.7 | Page parametres cours (Schedule & Details) | Natif | Verifier traduction FR |
| 14.8 | Widgets user_dropdown Studio | Customise (liens) | Verifier |

---

## 15. ESPACE FORMATEUR (vue dedicee)

| # | Element | A faire |
|---|---------|---------|
| 15.1 | Dashboard formateur dedie (pas le meme que admin) | Affiner le template _mf_dashboard_formateur.html |
| 15.2 | Vue "Mes formations" pour le formateur | Liste des cours ou il est instructor |
| 15.3 | Vue "Mes apprenants" pour le formateur | Liste des inscrits dans ses cours |
| 15.4 | Acces Qualiopi formateur | Boutons attestation, emargement, eval pre/post |
| 15.5 | Acces Studio depuis le dashboard formateur | Lien direct vers ses cours dans Studio |
| 15.6 | Messagerie interne formateur | Deja fait (/messagerie/interne/) — verifier acces |
| 15.7 | Notifications formateur | Deja fait (/notifications/interne/) — verifier acces |
| 15.8 | Export resultats formateur | Bouton CSV des notes de ses apprenants |

---

## 16. CONTENU DES 10 FORMATIONS

| # | Formation | Org | Contenu dans Studio | Statut |
|---|-----------|-----|---------------------|--------|
| 16.1 | Certificat de Formation Professionnelle VTC | MF-VTC | Cours OLX complet (8 chapters, 27 HTML, 17 quiz) | Fait |
| 16.2 | Maitriser l'IA en entreprise | MF-IA | Cours vide (cree dans Studio) | A creer |
| 16.3 | Leadership et Management d'equipe | MF-MGMT | Cours vide | A creer |
| 16.4 | Gestion des RH et Droit du travail | MF-RH | Cours vide | A creer |
| 16.5 | Excel et Outils bureautiques | MF-DIGITAL | Cours vide | A creer |
| 16.6 | Techniques de vente et Negociation | MF-VENTE | Cours vide | A creer |
| 16.7 | Anglais professionnel VTC | MF-VTC | Cours vide | A creer |
| 16.8 | Comptabilite et Gestion financiere | MF-FINANCE | Cours vide | A creer |
| 16.9 | Automatisation et Workflows IA | MF-IA | Cours vide | A creer |
| 16.10 | Cours existant MF-VTC-2025 | MissionFormations | Cours OLX complet | Fait |

Pour chaque formation a creer :
- [ ] Structure OLX (chapters, sequentials, verticals)
- [ ] Contenu HTML par module (textes, objectifs, exemples)
- [ ] Quiz par chapitre (QCM, 3-5 questions)
- [ ] Description du cours (short_description + overview dans Studio)
- [ ] Image du cours
- [ ] Dates de debut/fin
- [ ] Rattachement a l'academie (AcademyCourse)

---

## 17. GUIDES UTILISATEURS A CREER

| # | Guide | Pour qui | Contenu | Effort | Statut |
|---|-------|----------|---------|--------|--------|
| 17.1 | Guide apprenant complet | Apprenants | Inscription, connexion, naviguer un cours, exercices, progression, certificat, FAQ | 4h | A faire |
| 17.2 | Guide formateur complet | Formateurs | Acces Studio, creer un cours, gerer les apprenants, notes, export, rapports, messagerie | 4h | A faire |
| 17.3 | Guide admin complet | Super admins | Dashboard admin, Academy Manager, gestion utilisateurs, Tests QA, Console Django | 3h | A faire |
| 17.4 | Guide B2B (responsable RH) | Clients B2B | Portail entreprise, suivi collaborateurs, attestations, siege, facturation | 2h | A faire (depend Sprint 4.3) |

Formats :
- Version en ligne (page /aide/ — enrichir les guides existants)
- Version PDF telechargeable
- Version video (optionnel, phase 2)

---

## 18. MODULE QUALIOPI — INTEGRATION AU DASHBOARD

| # | Tache | Dependance | Effort | Statut |
|---|-------|------------|--------|--------|
| 18.1 | Modeles Django (FormationProgram, Convention, SatisfactionSurvey, EmargementLog) | Aucune | 3h | A faire |
| 18.2 | Migration 0003_qualiopi_models | 18.1 | 30min | A faire |
| 18.3 | Onglet "Qualiopi" dans le dashboard admin | 18.1 | 4h | A faire |
| 18.4 | Attestation de formation PDF (enrichir l'existant) | 18.1 | 2h | A faire |
| 18.5 | Programme de formation PDF (depuis structure OLX) | 18.1 | 4h | A faire |
| 18.6 | Feuille d'emargement e-learning (logs connexion) | 18.1 | 4h | A faire |
| 18.7 | Rapport de suivi enrichi (progression par module) | 18.1 | 2h | A faire |
| 18.8 | Enquete de satisfaction (formulaire + synthese PDF) | 18.1 | 5h | A faire |
| 18.9 | Bilan de formation (ZIP complet pour auditeur) | 18.4-18.8 | 4h | A faire |
| 18.10 | Convention de formation B2B | 18.1 | 3h | A faire |
| 18.11 | Convocation stagiaire | 18.1 | 2h | A faire |
| 18.12 | Evaluation pre/post formation | 18.1 | 3h | A faire |
| 18.13 | Boutons PDF dans le dashboard formateur | 18.4, 18.6 | 2h | A faire |
| 18.14 | Tests unitaires Qualiopi (modeles, PDF, routes) | 18.1-18.12 | 3h | A faire |
| 18.15 | Documentation auditeur Qualiopi | 18.9 | 3h | A faire |
| 18.16 | Documentation admin Qualiopi | 18.3 | 2h | A faire |
| 18.17 | Documentation formateur Qualiopi | 18.13 | 2h | A faire |

---

## RESUME QUANTITATIF (mis a jour)

| Categorie | A faire | Fait | Total |
|-----------|---------|------|-------|
| Certificats | 6 | 0 | 6 |
| Pages theme | 3 | 16 | 19 |
| Cahier des charges | 10 | 8 | 18 |
| Infra/Ops | 7 | 3 | 10 |
| Corrections | 7 | 0 | 7 |
| Dashboard admin | 10 | 4 | 14 |
| Dashboard apprenant | 7 | 3 | 10 |
| Dashboard formateur | 8 | 2 | 10 |
| Customisation Studio | 6 | 2 | 8 |
| Pages publiques | 2 | 9 | 11 |
| Securite | 4 | 1 | 5 |
| Contenu formations | 8 | 2 | 10 |
| Guides utilisateurs | 4 | 0 | 4 |
| Module Qualiopi | 17 | 0 | 17 |
| Tests | 7 | 178 | 185 |
| Documentation | 5 | 10+ | 15+ |
| **TOTAL** | **~111 taches** | **~238 faits** | **~349** |

**Estimation effort restant : ~180-220h de travail**

| Categorie | A faire | Fait | Total |
|-----------|---------|------|-------|
| Certificats | 6 | 0 | 6 |
| Pages theme | 3 | 16 | 19 |
| Cahier des charges | 10 | 8 | 18 |
| Infra/Ops | 7 | 3 | 10 |
| Corrections | 7 | 0 | 7 |
| Dashboard admin (onglets) | 6 | 8 | 14 |
| Dashboard apprenant | 5 | 5 | 10 |
| Pages publiques | 2 | 9 | 11 |
| Securite | 4 | 1 | 5 |
| Tests | 7 | 178 | 185 |
| Documentation | 5 | 10+ | 15+ |
| **TOTAL** | **~62 taches** | **~238 faits** | **~300** |

**Estimation effort restant : ~80-100h de travail**
