# Changelog — Session du 17 mars 2026

> Suite de la session du 16 mars. Branche staging.

## Resume

| Categorie | Ce qui a ete fait |
|-----------|------------------|
| **Sprint 1** | 11 organisations MF creees, plugins discovery+credentials actives, sites Django nettoyes |
| **Sprint 2** | Plugin Academy Manager complet (modeles, vues, templates, migration) |
| **Sprint 3** | Dashboard admin connecte aux donnees reelles (Apprenants, Formations) |
| **Mako** | Fix stable <%page args> pour tous les templates custom — pret prod |
| **SSL** | Certificat wildcard Let's Encrypt genere pour *.academie.staging.missionformations.com |
| **Admin** | Suppression utilisateur securisee, Console Django en dropdown, page delete user |
| **UI** | Dashboard Tests & QA avec KPIs et resultats exploitables, feedback email instantane |
| **Diagnostic** | Script diagnose.py avec cause racine, sync disque/container, webpack detection |
| **Deploy** | deploy.sh corrige (docker cp auto, pas de --clear, cache Mako, pytest) |
| **DB** | Tables manquantes corrigees (oel_collections, mission_central_admin, sites) |

## Commits

| Commit | Description |
|--------|-------------|
| `7522f003` | fix(mako): <%page args> stable prod pour tous les templates |
| `742a4768` | feat(dashboard): Sprint 3 — Apprenants et Formations donnees reelles |
| `7ab94c5c` | feat(academy): Sprint 2 — plugin Academy Manager complet |
| `c3b255d9` | fix(ui): Utilisateurs dans le dropdown Console Django |
| `ef4e2673` | feat(ui): regrouper Console Django en dropdown depliable |
| `be1f7504` | feat(admin): suppression securisee des utilisateurs |
| `aa480f05` | docs: changelog session 16 mars 2026 |
| `798e1659` | feat(ui): dashboard Tests & QA resultats exploitables |
| `b1a1cc8f` | feat(ui): feedback instantane sur le dashboard Tests & QA |
| `87c134c7` | fix(tests): compatibilite Docker — auto-detection local vs container |
| `e3d7bf3b` | docs(qa): documenter la sync disque/container + depannage rapide |
| `1e5cb224` | feat(ops): detecter et corriger la desync disque/container Docker |
| `681388c9` | feat(ops): diagnostic cause racine — identifie le POURQUOI |
| `769bac34` | feat(ops): script diagnostic production |
| `59a87b89` | docs(qa): documenter les tests webpack et arbre de decision 500 |
| `e7d0a6cd` | fix(ops): corriger crash 500 webpack-stats.json |
| `5afe1767` | feat(tests): ajout test_deploy_health.py |
| `3c4431ae` | fix(template): corriger syntaxe Mako du dashboard tests |
| `445d4ffb` | feat(tests): envoi des resultats de tests par email |
| `b5193a09` | fix(dashboard): ajouter section Qualite dans la sidebar admin |
| `c1449f63` | feat(vtc): ajout 17 quiz OLX complets |
| `f5138f71` | docs(qa): strategie de tests en 4 couches |
| `859f704d` | feat(tests): suite de tests complete — 134 tests |
| `6fe23c26` | feat(theme): mise a jour noms formations homepage |
| `5dbeff40` | fix(ops): securisation secrets, correction config prod, nettoyage repo |

## Cahier des charges — Avancement

| Sprint | Statut | Detail |
|--------|--------|--------|
| **Sprint 1** — Fondations | Termine | 11 orgs, discovery+credentials, sites nettoyes, certificat SSL wildcard |
| **Sprint 2** — Academy Manager | Termine | Modeles Academy/AcademyAdmin/AcademyCourse/AcademyEnrollment, vues CRUD, templates |
| **Sprint 3** — Dashboard avance | Termine | Apprenants et Formations connectes aux donnees reelles, page Academies supprimee |
| **Sprint 4** — Pages publiques + B2B | A faire | Page /academie/{slug}/, portail RH, middleware sous-domaine |
| **Sprint 5** — Contenu + Go Live | A faire | Import cours, tests utilisateurs, deploiement prod |

## Session 18 mars 2026

| Commit | Description |
|--------|-------------|
| `17c1ed59` | feat(chat): Chatwoot self-hosted configure — token + baseUrl |
| `489d404a` | feat(chat): integrer Chatwoot sur toutes les pages du LMS |
| `8873436c` | fix(aide): remplacer fleches HTML par SVG anti-pixelisation |
| `439b1d02` | feat(tests): +30 tests — Aide, Academy Manager, delete user |
| `d596dc33` | feat(aide): Centre d'aide complet — 8 guides + FAQ 9 questions |
| `63917bb6` | docs: changelog 17 mars, CLAUDE.md bilan sprints 1-3 |
| `7522f003` | fix(mako): <%page args> stable prod pour tous les templates |

## Infrastructure

| Element | Statut |
|---------|--------|
| Certificat SSL wildcard | Genere (expire 15/06/2026) |
| Certificat sur le serveur | Copie dans /root/certs/ |
| DNS wildcard *.academie.staging | Configure chez OVH |
| Caddy wildcard config | A faire |
| 11 organisations OpenEdX | Creees |
| 12 academies en BDD (11 MF + 1 B2B test) | Creees |
| Plugin discovery | Active |
| Plugin credentials | Active |
| Chatwoot self-hosted | 4 containers Docker (rails, sidekiq, postgres, redis) |
| Chatwoot token | o1xopqgYNv1n8VHEbEHcNGdR |
| Chatwoot admin | chat.staging.missionformations.com |
| Chatwoot DNS | A ajouter: chat.staging A 89.167.50.194 |
| Centre d'aide | /aide/ — 8 guides + FAQ 9 questions |
| Tests | 164 tests (+ 30 nouveaux) |

## Bugs corriges en production (session 16-17 mars)

| Bug | Cause racine | Fix |
|-----|-------------|-----|
| 500 sur toutes les pages | webpack-stats.json supprime par collectstatic --clear | deploy.sh sans --clear |
| 500 apres deploy | Cache Mako perime | deploy.sh vide le cache auto |
| Page 404 apres git pull | Code disque != code container Docker | deploy.sh fait docker cp auto |
| Templates affichent 0/vide | locals().get() ne marche pas en Mako | <%page args> (mecanisme officiel) |
| Suppression user → 500 | Foreign key course_creators (table CMS) | Vue custom avec nettoyage SQL |
| Migration tables manquantes | Migrations fake-applied sans tables | Fake-reset + apply |
| SyntaxError cms-production.py | Instructions collees (Codex) | Saut de ligne |
| Secrets en dur dans le repo | Cles JWT/Meilisearch/OAuth2 en clair | os.environ.get() |

## Arborescence des fichiers crees/modifies

```
lms/djangoapps/mission_central_admin/
├── models.py                          # +Academy, AcademyAdmin, AcademyCourse, AcademyEnrollment
├── views.py                           # +academy_list, academy_create, academy_detail, delete_user, test_dashboard
├── urls.py                            # +5 routes academy-manager, +1 route delete-user
└── migrations/
    └── 0002_academy_*.py              # Migration 4 tables

themes/mission-theme/lms/templates/
├── academy_manager/
│   ├── dashboard.html                 # Liste academies MF + B2B
│   ├── create.html                    # Formulaire creation avec color picker
│   └── detail.html                    # Detail avec 5 onglets
├── admin_central_dashboard.html       # Apprenants/Formations connectes, Academies supprime
├── admin_test_dashboard.html          # KPIs, barre progression, email resultats
├── admin_delete_user.html             # Suppression securisee utilisateurs
└── _mf_dashboard_sidebar.html         # Section Qualite + Console Django

tests/
├── diagnose.py                        # Diagnostic cause racine SSH (couche 0-4)
└── integration/
    └── test_deploy_health.py          # Tests sync disque/container + webpack

docs/ops/
├── TESTING_STRATEGY.md                # Strategie 4 couches (mis a jour)
├── PRE_DEPLOY_CHECKLIST.md            # Procedure deploy (mis a jour)
└── CHANGELOG_2026-03-17.md            # Ce fichier
```
