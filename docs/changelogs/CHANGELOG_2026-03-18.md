# Changelog — Session du 18 mars 2026

> 38 commits sur la branche staging
> De `aa480f05` a `7562d407`

## Resume

| Categorie | Ce qui a ete fait |
|-----------|------------------|
| **Sprint 2** | Academy Manager complet (modeles, vues, templates, 12 academies) |
| **Sprint 3** | Dashboard connecte (Apprenants, Formations donnees reelles) |
| **Catalogue** | Page /catalogue/ avec 10 formations reelles + filtres + recherche |
| **Enrollment** | Page d'inscription cours avec design wireframe (course_about.html) |
| **Aide** | Centre d'aide 8 guides + FAQ 9 questions (/aide/) |
| **Chat** | WeWill self-hosted (4 containers Docker) + widget sur toutes les pages |
| **PDF** | Module Qualiopi — attestation + rapport de suivi (ReportLab) |
| **Refactoring** | 0 fichier natif OpenEdX modifie (middleware + signals dans le plugin) |
| **Admin** | Suppression user securisee, Console Django dropdown, delete user page |
| **Tests** | 178 tests (+44 nouveaux: PDF, Aide, Academy, deploy) |
| **Footer** | Liens vers missionformations.com (about, CGV, mentions legales) |
| **Infra** | Plugin Tutor WeWill, certificat SSL wildcard, Caddy reverse proxy |
| **Docs** | Epic Qualiopi (14 tickets), Epic fork WeWill (9 tickets), diagnostic repo |

## Commits detailles

### Features

| Commit | Description |
|--------|-------------|
| `7ab94c5c` | Sprint 2 — Academy Manager complet (modeles, vues, templates) |
| `742a4768` | Sprint 3 — Apprenants et Formations donnees reelles |
| `d596dc33` | Centre d'aide complet — 8 guides + FAQ 9 questions |
| `5d5b4d58` | Page catalogue des formations — donnees reelles OpenEdX |
| `863dc9f8` | Page d'inscription cours — design wireframe enrollment |
| `efcb0172` | Rapports PDF Qualiopi (attestation + suivi formation) |
| `be1f7504` | Suppression securisee des utilisateurs (foreign keys CMS) |
| `ef4e2673` | Console Django en dropdown depliable |
| `18130cae` | Liens Mission Formations sur LMS, MFE et Studio |
| `489d404a` | Widget chat WeWill sur toutes les pages du LMS |
| `600be31a` | Liens vers missionformations.com (about, CGV, mentions legales) |
| `c2655f4f` | Rediriger /courses vers /catalogue/ |

### Refactoring (0 fichier natif modifie)

| Commit | Description |
|--------|-------------|
| `8a2112e4` | Restaurer 2 templates natifs (email + admin) — le theme override suffit |
| `c0fa2a12` | Restaurer management.py et register.py — logique dans le plugin |
| `7522f003` | <%page args> pour les variables Mako — solution stable prod |
| `cb1e131c` | Remplacer Chatwoot par WeWill — toutes les references |

### Infra

| Commit | Description |
|--------|-------------|
| `435f3a59` | Plugin Tutor mission_wewill — reverse proxy Caddy |
| `8e26a951` | Proxy via nom DNS Docker au lieu de bridge IP |
| `5e15ad04` | Domaine WEWILL_HOST configurable |

### Bugs corriges

| Commit | Bug | Cause racine |
|--------|-----|-------------|
| `7562d407` | 500 sur /heartbeat → Studio inaccessible | Middleware accedait a request.user avant AuthenticationMiddleware |
| `8873436c` | Fleches pixelisees dans la section Aide | HTML entities double-echappees par Mako |
| `8ce9d1b9` | Terms of Service / Privacy Policy natifs dans le footer | Boucle legal_links non remplacee |
| `5406ae85` | Widget chat non fonctionnel | Token en BDD different de celui copie |
| `c8ddfc54` | Branding "Chatwoot" visible dans le widget | CSS ::after pour masquer (iframe limitee) |

### Documentation

| Commit | Description |
|--------|-------------|
| `dccb1a61` | Diagnostic repo — natif vs custom (334+ fichiers audites) |
| `8f0eb64d` | Epic module Qualiopi — 14 tickets, 10 types de documents |
| `2452d1d6` | Epic fork WeWill — 9 tickets Jira |
| `36c89dbc` | Guides utilisateur WeWill (equipe + clients) |
| `e049a88a` | Documentation technique WeWill + procedure mise en prod |
| `63917bb6` | Changelog 17 mars + CLAUDE.md bilan sprints 1-3 |

## Etat du repo

| Metrique | Valeur |
|----------|--------|
| Fichiers custom | 334+ |
| Fichiers natifs modifies | **0** |
| Tests | 178 |
| Templates dans le theme | 75+ |
| Modeles Django custom | 5 (Academy, AcademyAdmin, AcademyCourse, AcademyEnrollment, InternalMessageAudit) |
| Vues custom | 25+ |
| Routes custom | 20+ |
| Plugins Tutor | 8 |
| Cours dans Studio | 10 |
| Academies en BDD | 12 (11 MF + 1 B2B test) |
| Organisations OpenEdX | 12 |

## Cahier des charges — Avancement

| Sprint | Statut |
|--------|--------|
| Sprint 1 — Fondations | **Termine** |
| Sprint 2 — Academy Manager | **Termine** |
| Sprint 3 — Dashboard avance | **Termine** |
| Sprint 4 — Pages publiques + B2B | **En cours** (catalogue fait, enrollment fait) |
| Sprint 5 — Contenu + Go Live | A faire |

## Epics separees

| Epic | Tickets | Statut |
|------|---------|--------|
| Fork WeWill (chat) | 9 tickets (CHAT-1 a 9) | Planifie |
| Module Qualiopi | 14 tickets (QUA-1 a 14) | Planifie |
