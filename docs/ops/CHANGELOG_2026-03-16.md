# Changelog — Session du 16 mars 2026

> 18 commits sur la branche staging — de `5dbeff40` a `fa479825`

## Resume

| Categorie | Ce qui a ete fait |
|-----------|------------------|
| **Securite** | Secrets externalises, bug syntaxe Python corrige, duplications nettoyees |
| **Tests** | 151 tests (unit/integration/smoke), 10 fichiers |
| **Diagnostic** | Script `diagnose.py` — cause racine en 4 couches via SSH |
| **Dashboard QA** | Page Tests & QA avec KPIs, barre progression, email resultats |
| **Console Django** | 8 liens directs vers admin Django dans la sidebar |
| **OLX** | 17 quiz VTC complets |
| **Deploy** | `deploy.sh` corrige (sync container, pas de `--clear`, cache Mako) |
| **Documentation** | `TESTING_STRATEGY.md`, `PRE_DEPLOY_CHECKLIST.md`, `TESTING.md` |

## Commits detailles

| Commit | Type | Description |
|--------|------|-------------|
| `fa479825` | feat | Connecter tous les onglets admin aux pages Django |
| `798e1659` | feat | Dashboard Tests & QA — resultats exploitables (KPIs, barre, tableau) |
| `b1a1cc8f` | feat | Feedback instantane sur le dashboard Tests & QA |
| `87c134c7` | fix | Compatibilite Docker — auto-detection local vs container |
| `e3d7bf3b` | docs | Documenter la sync disque/container + depannage rapide |
| `1e5cb224` | feat | Detecter et corriger la desynchronisation disque/container Docker |
| `681388c9` | feat | Diagnostic cause racine — identifie le POURQUOI de chaque erreur |
| `769bac34` | feat | Script diagnostic production — identifie la cause racine des 500 |
| `59a87b89` | docs | Documenter les tests webpack et l'arbre de decision des erreurs 500 |
| `e7d0a6cd` | fix | Corriger crash 500 — webpack-stats.json supprime par collectstatic --clear |
| `5afe1767` | feat | Ajout test_deploy_health.py — detecte les regressions post-deploy |
| `3c4431ae` | fix | Corriger syntaxe Mako du dashboard tests |
| `445d4ffb` | feat | Envoi des resultats de tests par email |
| `b5193a09` | fix | Ajouter section Qualite dans la sidebar admin |
| `c1449f63` | feat | Ajout 17 quiz OLX complets — cours MF-VTC-2025 100% couvert |
| `f5138f71` | docs | Strategie de tests en 4 couches — guide complet QA et DevOps |
| `859f704d` | feat | Suite de tests complete — 134 tests couvrant toutes les customisations |
| `6fe23c26` | feat | Mise a jour noms formations homepage |
| `5dbeff40` | fix | Securisation secrets, correction config prod, nettoyage repo |

## Bugs corriges en production

| Bug | Cause racine | Fix |
|-----|-------------|-----|
| 500 sur toutes les pages | `collectstatic --clear` supprime `webpack-stats.json` | `deploy.sh` utilise `--noinput` sans `--clear` |
| 500 apres deploy | Cache Mako sert l'ancien template | `deploy.sh` vide le cache Mako automatiquement |
| Page 404 apres `git pull` | Code disque != code container Docker | `deploy.sh` fait `docker cp` automatiquement |
| SyntaxError `cms-production.py` | Instructions Python collees sur une ligne (Codex) | Saut de ligne ajoute |
| Secrets en dur dans le repo | Cles JWT, Meilisearch, OAuth2 en clair | Externalises via `os.environ.get()` |

## Fichiers crees

```
tests/
├── conftest.py
├── pytest.ini
├── diagnose.py                        # Diagnostic cause racine SSH
├── unit/
│   ├── test_tutor_config.py           # 15 tests config
│   ├── test_olx_structure.py          # 15 tests OLX
│   ├── test_theme_templates.py        # 15 tests theme
│   ├── test_plugin_logic.py           # 25 tests plugin
│   └── test_deploy_scripts.py         # 13 tests scripts
├── integration/
│   ├── test_health.py                 # 9 tests infra
│   ├── test_auth.py                   # 7 tests auth
│   ├── test_api.py                    # 8 tests API
│   └── test_deploy_health.py          # 17 tests deploy
└── smoke/
    └── test_smoke_prod.py             # 13 tests post-deploy

docs/ops/
├── PRE_DEPLOY_CHECKLIST.md            # Checklist pre-deploiement
├── TESTING.md                         # Reference technique des tests
├── TESTING_STRATEGY.md                # Strategie 4 couches QA/DevOps

olx-courses/problem/                   # 17 fichiers quiz VTC

themes/mission-theme/lms/templates/
├── admin_test_dashboard.html          # Dashboard Tests & QA
└── admin_central_dashboard.html       # Sidebar avec Console Django
```
