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

## RESUME QUANTITATIF

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
