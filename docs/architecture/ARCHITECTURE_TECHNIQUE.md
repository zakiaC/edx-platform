# Document d'Architecture Technique — Mission Formations

> Version 1.0 — 21 mars 2026
> Plateforme de formation professionnelle certifiee Qualiopi
> Inspire de la strategie DevOps Provence AI, adapte au contexte SaaS/OpenEdX

---

## 1. PRESENTATION GENERALE

### 1.1 Le produit

**Mission Formations** est une plateforme de formation professionnelle en ligne (e-learning)
destinee aux organismes de formation, entreprises et particuliers.

| Caracteristique | Detail |
|-----------------|--------|
| **Type** | SaaS (Software as a Service) — heberge par Mission Formations |
| **Acces** | Navigateur web (aucune installation cote client) |
| **Certification** | Qualiopi (en cours) — conformite 32 indicateurs |
| **Cible** | Apprenants individuels, entreprises B2B, financeurs (OPCO, CPF, Mission Locale, CSE) |
| **Editeur** | Mission Formations |

### 1.2 Les briques fonctionnelles

```
┌────────────────────────────────────────────────────────────────────────┐
│                     MISSION FORMATIONS — ECOSYSTEME                    │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    COUCHE UTILISATEUR                            │   │
│  │                                                                 │   │
│  │  Apprenant          Formateur          Admin          Auditeur  │   │
│  │  • Cours            • Studio           • Dashboard    • Preuves │   │
│  │  • Quiz             • Apprenants       • KPIs         • 32 ind. │   │
│  │  • Certificats      • Notes            • Qualiopi     • ZIP     │   │
│  │  • Progression      • Rapports         • Utilisateurs           │   │
│  │  • Satisfaction     • Messagerie       • Academies              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    COUCHE APPLICATIVE                            │   │
│  │                                                                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │  │ OpenEdX  │  │ Qualiopi │  │  Odoo    │  │ WeWill   │       │   │
│  │  │  (LMS)   │  │  (Hub)   │  │  (ERP)   │  │ (Chat)   │       │   │
│  │  │          │  │          │  │          │  │          │       │   │
│  │  │ Django   │  │ Django   │  │ Python   │  │ Rails    │       │   │
│  │  │ Mako     │  │ DRF      │  │ Odoo.sh  │  │ Docker   │       │   │
│  │  │ uWSGI    │  │ Gunicorn │  │ (SaaS)   │  │          │       │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    COUCHE DONNEES                                │   │
│  │                                                                 │   │
│  │  MySQL       MongoDB     PostgreSQL   Redis      Meilisearch   │   │
│  │  (OpenEdX)   (Cours)     (Qualiopi)   (Cache)    (Recherche)   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    COUCHE INFRASTRUCTURE                        │   │
│  │                                                                 │   │
│  │  VPS OVH 32 Go    Docker/Compose    Caddy    OVH Object S3    │   │
│  │  Ubuntu 22.04      Tutor v21.0.1     SSL      Videos/PDFs      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    COUCHE RESEAU                                 │   │
│  │                                                                 │   │
│  │  Cloudflare (CDN + DDoS + SSL)    DNS OVH    HTTPS uniquement  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPOSANTS TECHNIQUES

### 2.1 Catalogue des services

| Service | Technologie | Version | Role | Port interne |
|---------|------------|---------|------|-------------|
| **LMS** | OpenEdX (Django) | Tutor v21.0.1 (Ulmo) | Plateforme de formation (cours, quiz, certificats) | 8000 |
| **CMS (Studio)** | OpenEdX (Django) | Tutor v21.0.1 | Creation et edition des cours | 8001 |
| **MySQL** | MySQL | 8.0 | Base relationnelle OpenEdX (users, enrollments, grades, certificates) | 3306 |
| **MongoDB** | MongoDB | 7.0 | Contenu des cours (modulestore), ORA2, xblock states | 27017 |
| **Redis** | Redis | 7-alpine | Cache (7 caches), broker Celery, sessions | 6379 |
| **Meilisearch** | Meilisearch | Latest | Recherche full-text des cours (catalogue, courseware) | 7700 |
| **Caddy** | Caddy | Latest | Reverse proxy, terminaison SSL, routing | 80, 443 |
| **App Qualiopi** | Django + DRF | 5.x | Hub API central, conformite Qualiopi, PDFs, automatisations | 8080 |
| **Qualiopi Celery** | Celery | 5.x | Workers async (PDFs, emails, veille, alertes) | — |
| **PostgreSQL Qualiopi** | PostgreSQL | 16 | Base Qualiopi (registres, formulaires, documents) | 5432 |
| **Odoo** | Odoo.sh (SaaS) | 17.0 | CRM, ventes, facturation, signature electronique | — (externe) |
| **WeWill** | Chatwoot | Latest | Chat support temps reel | 3000 |
| **WeWill Sidekiq** | Sidekiq | — | Jobs async WeWill (emails, webhooks) | — |
| **WeWill PostgreSQL** | PostgreSQL | 14 | Base WeWill (conversations, contacts) | 5433 |
| **WeWill Redis** | Redis | 7-alpine | Cache + queues WeWill | 6380 |
| **OVH Object Storage** | S3 compatible | — | Stockage videos, PDFs generes, backups | — (externe) |

### 2.2 Schema reseau

```
                              INTERNET
                                 │
                          ┌──────┴──────┐
                          │ Cloudflare  │
                          │ CDN + WAF   │
                          └──────┬──────┘
                                 │
                          ┌──────┴──────┐
                          │   Caddy     │
                          │  :80 :443   │
                          └──────┬──────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    academie.mf.com    studio.mf.com     chat.mf.com
              │                  │                  │
         ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
         │  LMS    │       │  CMS    │       │ WeWill  │
         │  :8000  │       │  :8001  │       │  :3000  │
         └────┬────┘       └─────────┘       └─────────┘
              │
    /qualiopi/*
              │
         ┌────┴────┐
         │Qualiopi │
         │  :8080  │
         └─────────┘

Reseau Docker interne (non expose) :
  MySQL :3306    MongoDB :27017    Redis :6379
  Meilisearch :7700    PostgreSQL Qualiopi :5432
```

### 2.3 Ports exposes (firewall VPS)

| Port | Protocole | Usage | Expose a |
|------|-----------|-------|----------|
| 22 | TCP | SSH (administration) | IP admin uniquement |
| 80 | TCP | HTTP (redirect → 443) | Public |
| 443 | TCP | HTTPS (tout le trafic) | Public |

**Tous les autres ports sont fermes.** Les services internes communiquent via le reseau Docker bridge (non accessible depuis l'exterieur).

---

## 3. ENVIRONNEMENTS

### 3.1 Types d'environnements

| Environnement | Role | URL | Donnees | Deploiement |
|---------------|------|-----|---------|-------------|
| **Production** | Apprenants reels, formations payantes | `academie.missionformations.com` | Donnees reelles | Push sur `main` → deploy auto |
| **Staging** | Tests pre-production, validation | `academie.staging.missionformations.com` | Donnees de test / anonymisees | Push sur `staging` → deploy auto |
| **Demo** | Demonstrations clients, demos commerciales | `demo.missionformations.com` | Donnees de demonstration | Manuel (snapshot staging) |
| **Dev local** | Developpement | `localhost` | Donnees de test | Local (docker compose up) |

### 3.2 Matrice des services par environnement

| Service | Production | Staging | Demo | Dev local |
|---------|-----------|---------|------|-----------|
| LMS | ✅ | ✅ | ✅ | ✅ |
| CMS (Studio) | ✅ | ✅ | ✅ | ✅ |
| MySQL | ✅ | ✅ | ✅ | ✅ |
| MongoDB | ✅ | ✅ | ✅ | ✅ |
| Redis | ✅ | ✅ | ✅ | ✅ |
| Meilisearch | ✅ | ✅ | ❌ | ❌ |
| App Qualiopi | ✅ | ✅ | ✅ | ✅ |
| Celery workers | ✅ | ✅ | ❌ | ✅ |
| Celery beat | ✅ | ❌ | ❌ | ❌ |
| Odoo.sh | ✅ | ✅ (sandbox) | ❌ | ❌ |
| WeWill | ✅ | ✅ | ❌ | ❌ |
| Cloudflare | ✅ | ❌ | ❌ | ❌ |
| OVH Object Storage | ✅ | ✅ | ❌ | ❌ |
| Monitoring (Netdata) | ✅ | ✅ | ❌ | ❌ |

### 3.3 Convention DNS

| Pattern | Exemple | Usage |
|---------|---------|-------|
| `academie.missionformations.com` | — | LMS production |
| `studio.missionformations.com` | — | CMS/Studio production |
| `academie.staging.missionformations.com` | — | LMS staging |
| `demo.missionformations.com` | — | Instance demo client |
| `chat.missionformations.com` | — | WeWill production |
| `apps.missionformations.com` | — | MFEs (Account, Learning, etc.) |
| `meilisearch.missionformations.com` | — | Recherche (interne) |
| `{client}.academie.missionformations.com` | `abc.academie.missionformations.com` | Sous-domaine academie B2B |

---

## 4. RESSOURCES ET DIMENSIONNEMENT

### 4.1 Configuration actuelle

| Composant | Specification |
|-----------|--------------|
| **Hebergeur** | OVH VPS |
| **OS** | Ubuntu 22.04 LTS |
| **CPU** | 8 vCPU |
| **RAM** | 16 Go (→ upgrade 32 Go prevu) |
| **Disque** | 160 Go SSD |
| **Reseau** | 1 Gbps |
| **IP** | 1 IPv4 publique |

### 4.2 Dimensionnement par palier

| Palier | Apprenants | Formations | RAM | CPU | Disque | Cout VPS |
|--------|-----------|------------|-----|-----|--------|----------|
| **Demarrage** | 0-50 | 5-10 | 32 Go | 8 vCPU | 200 Go + S3 | ~45€/mois |
| **Croissance** | 50-200 | 10-30 | 32 Go | 8 vCPU | 200 Go + S3 | ~45€/mois |
| **Scaling** | 200-500 | 30-70 | 64 Go | 8-16 vCPU | 300 Go + S3 | ~90€/mois |
| **Enterprise** | 500+ | 100+ | 2 × 32 Go | 2 × 8 vCPU | S3 massif | ~150€/mois |

### 4.3 Repartition memoire cible (32 Go)

| Service | RAM allouee | % |
|---------|-----------|---|
| LMS (4 workers uWSGI) | 5-6 Go | 17% |
| CMS (2 workers uWSGI) | 2-3 Go | 8% |
| MySQL (innodb_buffer_pool) | 4-6 Go | 16% |
| MongoDB (WiredTiger cache) | 2-3 Go | 8% |
| Redis | 1 Go | 3% |
| Meilisearch | 500 Mo | 2% |
| App Qualiopi (3 workers Gunicorn) | 1-2 Go | 5% |
| Celery workers (2) | 500 Mo - 1 Go | 3% |
| PostgreSQL Qualiopi | 500 Mo | 2% |
| Caddy | 50 Mo | <1% |
| OS + overhead Docker | 3-4 Go | 11% |
| **Headroom (libre)** | **6-8 Go** | **~25%** |
| **Total** | **32 Go** | **100%** |

**Regle : toujours garder 20-25% de RAM libre** pour absorber les pics (generation PDF, sessions simultanees, backups).

### 4.4 Stockage

| Type | Emplacement | Usage | Taille estimee |
|------|-------------|-------|---------------|
| **Systeme + Docker** | SSD VPS | OS, images Docker, logs | 50 Go |
| **Bases de donnees** | SSD VPS | MySQL, MongoDB, PostgreSQL | 20-50 Go |
| **Videos** | OVH Object Storage (S3) | Contenus pedagogiques | 100-500 Go |
| **PDFs generes** | OVH Object Storage (S3) | Attestations, rapports, bilans | 5-20 Go |
| **Backups** | OVH Object Storage (S3) | Sauvegardes quotidiennes | 50-100 Go |

**Regle : jamais de videos sur le disque du VPS.** Toujours sur Object Storage S3.

---

## 5. DEPLOIEMENT

### 5.1 Processus de deploiement

```
Developpeur pousse du code
         │
         ▼
    GitHub (push sur staging ou main)
         │
         ▼
    GitHub Actions CI
    ├── Lint (ruff)
    ├── Tests (pytest)
    └── Build Docker (si mission-qualiopi)
         │
         │  Si tous les tests passent :
         ▼
    GitHub Actions CD
    ├── SSH vers le serveur cible
    ├── Pull du code / image Docker
    ├── Restart des services
    ├── Clear cache (Mako, Redis)
    ├── Collectstatic (CSS/JS)
    └── Smoke test automatique
         │
         ▼
    Service en ligne
```

### 5.2 Deploiement OpenEdX (LMS + CMS)

```bash
# Etapes du deploiement (automatise par CI/CD, reproduit deploy.sh)

# 1. Copier le code custom dans le container
docker cp mission_central_admin/ tutor_local-lms-1:/openedx/edx-platform/lms/djangoapps/
docker cp themes/mission-theme/ tutor_local-lms-1:/openedx/themes/

# 2. Compiler le CSS du theme
docker exec tutor_local-lms-1 npm run compile-sass -- --skip-default

# 3. Collecter les fichiers statiques (JAMAIS avec --clear)
docker exec tutor_local-lms-1 python manage.py lms collectstatic --noinput

# 4. Vider le cache Mako
docker exec tutor_local-lms-1 find /tmp -name "*.mako.py" -delete

# 5. Redemarrer le LMS
docker restart tutor_local-lms-1
```

### 5.3 Deploiement App Qualiopi

```bash
# 1. Pull la nouvelle image
docker pull ghcr.io/missionformations/mission-qualiopi:latest

# 2. Arreter et redemarrer
docker compose -f /root/qualiopi/docker-compose.yml up -d

# 3. Appliquer les migrations si necessaire
docker exec qualiopi-app python manage.py migrate

# 4. Health check
curl -s https://academie.missionformations.com/qualiopi/health
```

### 5.4 Rollback

```bash
# En cas de probleme, revenir a la version precedente

# OpenEdX :
git checkout v1.2.3  # tag de la version stable
./deploy.sh staging  # redeployer

# App Qualiopi :
docker pull ghcr.io/missionformations/mission-qualiopi:v1.2.3  # image taggee
docker compose -f /root/qualiopi/docker-compose.yml up -d
```

### 5.5 Regles de deploiement

| Regle | Detail |
|-------|--------|
| **JAMAIS de collectstatic --clear** | Supprime webpack-stats.json → 500 sur toutes les pages |
| **Toujours vider le cache Mako** | Sinon les anciennes templates sont servies |
| **Toujours docker cp apres git pull** | Le disque ≠ le container |
| **Deployer en heures creuses** | Eviter les deploiements pendant les heures de formation (9h-17h) |
| **Tester en staging avant prod** | Jamais de deploy direct en production |
| **Backup avant deploy prod** | Snapshot MySQL + MongoDB avant chaque deploy production |

---

## 6. SECURITE

### 6.1 Securite reseau

| Mesure | Implementation |
|--------|---------------|
| **Firewall** | `ufw` : ports 22, 80, 443 ouverts uniquement |
| **SSH** | Cle ed25519 uniquement, pas de mot de passe, pas de root login |
| **HTTPS** | Obligatoire partout (Caddy auto-SSL ou Cloudflare) |
| **Cloudflare** | CDN, WAF basique, protection DDoS, cache assets |
| **Reseau Docker** | Services internes non exposes (bridge network) |

### 6.2 Securite applicative

| Mesure | Implementation |
|--------|---------------|
| **Authentification LMS** | Django auth + sessions securisees (HTTPS only cookies) |
| **Authentification API** | JWT RS256 (emis par OpenEdX) |
| **Webhooks** | HMAC-SHA256 (Odoo) + token API (WeWill) + secret interne (LMS) |
| **CSRF** | Active sur tous les formulaires Django |
| **XSS** | Templates Mako avec echappement auto |
| **SQL Injection** | ORM Django (pas de requetes SQL brutes) |
| **Rate limiting** | Par groupe d'endpoints (10-120 req/min selon le type) |
| **CSP** | Content-Security-Policy en Report-Only (monitoring) |

### 6.3 Securite des donnees

| Mesure | Implementation |
|--------|---------------|
| **Secrets** | Variables d'environnement + GitHub Secrets (jamais dans le code) |
| **Backups** | Quotidiens, chiffres GPG, stockes sur OVH Object Storage |
| **Mots de passe** | 12 caracteres min, complexite, blocage apres 5 tentatives |
| **2FA** | Active pour les comptes superuser/admin |
| **Donnees personnelles** | Conformite RGPD (registre des traitements, DPO designe) |
| **Conservation** | 5 ans apres fin de formation (Qualiopi), 10 ans (comptabilite) |
| **Droit a l'effacement** | Procedure documentee (retire_user OpenEdX + suppression Qualiopi + Odoo) |

### 6.4 Veille securite

| Source | Type | Frequence |
|--------|------|-----------|
| GitHub Dependabot | Alertes CVE sur les dependances Python/Node | Auto |
| CERT-FR / ANSSI | Alertes vulnerabilites OS et middleware | Hebdomadaire |
| Ubuntu Security Notices | Patches securite OS | Auto (unattended-upgrades) |
| Docker Security | Vulnerabilites images Docker | Mensuel |

### 6.5 Composants sous veille securite

| Composant | Version | Type |
|-----------|---------|------|
| Ubuntu | 22.04 LTS | OS |
| Docker Engine | 24.x | Container |
| Python | 3.11.8 | Langage |
| Django | 5.2 | Framework |
| Node.js | 24.x | Runtime |
| MySQL | 8.0 | Base de donnees |
| MongoDB | 7.0 | Base de donnees |
| PostgreSQL | 16 | Base de donnees |
| Redis | 7.x | Cache |
| Caddy | Latest | Reverse proxy |
| ReportLab | Latest | Generation PDF |
| Celery | 5.x | Task queue |

---

## 7. CONFORMITE

### 7.1 RGPD

| Obligation | Statut | Responsable |
|-----------|--------|-------------|
| Registre des traitements | A creer | DPO |
| Politique de confidentialite | A publier | DPO |
| Banniere cookies | A implementer | Dev |
| Contrats sous-traitants (art. 28) | A formaliser | DPO |
| Procedure droit a l'effacement | A documenter | DPO |
| Notification de violation (72h CNIL) | A documenter | DPO |
| Analyse d'impact (AIPD) | A evaluer | DPO |

### 7.2 Qualiopi

| Element | Statut |
|---------|--------|
| 32 indicateurs documentes | ✅ (cahier des charges) |
| 22 documents PDF specifies | ✅ |
| Module Qualiopi (app Django) | A developper |
| Referent handicap designe | A faire |
| Reglement interieur | A rediger |

### 7.3 Formation professionnelle

| Obligation | Statut |
|-----------|--------|
| Declaration d'activite (N° DA) | A verifier |
| Exoneration TVA (art. 261-4-4° CGI) | A demander |
| BPF (Bilan Pedagogique et Financier) | 1ere annee = pas encore |
| CGV specifiques formation | A rediger |
| RC Pro | A verifier |

---

## 8. BACKUPS ET PRA

### 8.1 Strategie de backup

| Donnees | Methode | Frequence | Retention | Stockage |
|---------|---------|-----------|-----------|----------|
| MySQL OpenEdX | `mysqldump` | Quotidien 2h00 | 30 jours | OVH S3 |
| MongoDB OpenEdX | `mongodump` | Quotidien 2h15 | 30 jours | OVH S3 |
| PostgreSQL Qualiopi | `pg_dump` | Quotidien 2h30 | 30 jours | OVH S3 |
| PostgreSQL WeWill | `pg_dump` | Quotidien 2h45 | 30 jours | OVH S3 |
| Fichiers config | `tar` de /root/config/ | Quotidien 3h00 | 90 jours | OVH S3 |
| Videos et PDFs | Deja sur S3 | — | Permanent | OVH S3 |

### 8.2 Plan de Reprise d'Activite (PRA)

| Scenario | RTO (delai reprise) | RPO (perte donnees max) | Procedure |
|----------|--------------------|-----------------------|-----------|
| Container crash | 1 min | 0 | Docker restart auto (`unless-stopped`) |
| Deploiement rate | 15 min | 0 | Rollback au tag precedent |
| Base corrompue | 1-2h | 24h max | Restauration depuis backup S3 |
| VPS indisponible | 4-8h | 24h max | Commander nouveau VPS + restaurer backups |
| Perte de donnees S3 | 8-24h | Variable | Contacter OVH support (replication interne) |

### 8.3 Tests de restauration

| Test | Frequence | Responsable |
|------|-----------|-------------|
| Restaurer un backup MySQL sur un container de test | Mensuel | Admin |
| Restaurer un backup MongoDB | Mensuel | Admin |
| Restaurer un backup PostgreSQL Qualiopi | Mensuel | Admin |
| Simuler la perte du VPS et reconstruire | Trimestriel | Admin |

---

## 9. MONITORING ET ALERTES

### 9.1 Outils de monitoring

| Outil | Usage | Cout |
|-------|-------|------|
| **Netdata** | Monitoring serveur (RAM, CPU, disque, reseau, containers) | Gratuit |
| **Uptime Kuma** | Monitoring des URLs (uptime, temps de reponse) | Gratuit |
| **GitHub Actions** | Monitoring des deploiements (succes/echec) | Gratuit |
| **Celery Flower** | Monitoring des workers Celery (taches, files d'attente) | Gratuit |

### 9.2 Alertes

| Alerte | Seuil | Canal |
|--------|-------|-------|
| RAM > 80% | 80% | Email admin |
| Disque > 85% | 85% | Email admin |
| CPU > 90% pendant 5 min | 90% | Email admin |
| Container down | Immediat | Email admin |
| URL LMS non accessible | 3 echecs consecutifs | Email + SMS |
| Deploiement echoue | Immediat | Email admin |
| Backup echoue | Immediat | Email admin |
| Certificat SSL expire dans 7j | 7 jours avant | Email admin |

---

## 10. SLA ET SUPPORT

### 10.1 Niveaux de support

| Niveau | Qui | Role | Canal |
|--------|-----|------|-------|
| **N1 — Self-service** | Apprenant | Consulte la page /aide/, le FAQ, le guide apprenant | Web |
| **N2 — Support standard** | Apprenant / RH entreprise | Contacte le support via le chat WeWill ou le formulaire /contact/ | Chat, email |
| **N3 — Support technique** | Admin Mission Formations | Diagnostique, corrige, deploie un fix | SSH, dashboard |

### 10.2 Engagements de service (SLA cible)

| Metrique | Engagement | Mesure |
|----------|-----------|--------|
| **Disponibilite plateforme** | 99.5% (hors maintenance planifiee) | Uptime Kuma |
| **Temps de reponse pages** | < 3 secondes (95e percentile) | Monitoring |
| **Temps de reponse support N2** | < 24h (jours ouvres) | WeWill |
| **Temps de resolution incidents critiques** | < 4h | Procedure interne |
| **Maintenance planifiee** | Prevenue 48h a l'avance, hors heures formation | Email |
| **Backup** | Quotidien, retention 30 jours | Script cron |
| **RPO (perte de donnees max)** | 24h | Frequence backup |
| **RTO (delai de reprise max)** | 4h (container), 8h (VPS complet) | PRA |

### 10.3 Horaires de support

| Periode | Couverture |
|---------|-----------|
| Lundi — Vendredi, 9h-18h | Support N2 actif (chat + email) |
| Soir et week-end | Support asynchrone (email, reponse J+1 ouvre) |
| Jours feries | Pas de support (sauf incident critique) |

---

## 11. COMMUNICATIONS INTER-SERVICES

### 11.1 Webhooks

| Source | Destination | Evenement | Auth |
|--------|------------|-----------|------|
| OpenEdX (LMS) | App Qualiopi | Enrollment, certificat, grade, login, publish, unenroll | Secret interne |
| Odoo | App Qualiopi | Commande confirmee, paiement, convention signee, facture | HMAC-SHA256 |
| WeWill | App Qualiopi | Nouvelle conversation, tag reclamation/abandon | Token API |
| App Qualiopi | Odoo | Completion apprenant, mise a jour contact | API Odoo (XML-RPC) |
| App Qualiopi | WeWill | Notification agent | API Chatwoot |

### 11.2 Acces base de donnees

| Connexion | Type | User | Droits |
|-----------|------|------|--------|
| App Qualiopi → MySQL OpenEdX | Lecture seule | `qualiopi_ro` | `GRANT SELECT ON openedx.*` |
| App Qualiopi → PostgreSQL Qualiopi | Lecture + ecriture | `qualiopi` | Full access |
| LMS → MySQL OpenEdX | Lecture + ecriture | `openedx` | Full access (natif) |
| WeWill → PostgreSQL WeWill | Lecture + ecriture | `chatwoot` | Full access |

---

## 12. GESTION DES SECRETS

### 12.1 Politique de gestion des secrets

| Regle | Detail |
|-------|--------|
| **Jamais dans le code** | Aucun secret dans le code source ou les fichiers commites |
| **Variables d'environnement** | Tous les secrets sont des variables d'environnement (`.env`) |
| **GitHub Secrets** | Les secrets CI/CD sont dans GitHub Secrets (chiffres) |
| **Rotation** | Rotation des secrets JWT et API tous les 6 mois |
| **Acces** | Seul l'admin a acces aux secrets de production |

### 12.2 Liste des secrets

| Secret | Usage | Ou il est stocke |
|--------|-------|-----------------|
| `SECRET_KEY` | Cle Django OpenEdX | `.env` serveur |
| `JWT_SECRET_KEY` | Signature JWT | `.env` serveur |
| `JWT_RSA_PRIVATE_KEY` | Cle privee JWT RS256 | `.env` serveur |
| `MYSQL_ROOT_PASSWORD` | MySQL OpenEdX | `.env` serveur |
| `QUALIOPI_DB_PASSWORD` | PostgreSQL Qualiopi | `.env` serveur + GitHub Secrets |
| `ODOO_WEBHOOK_SECRET` | HMAC webhooks Odoo | `.env` serveur + GitHub Secrets |
| `OPENEDX_INTERNAL_SECRET` | Webhooks internes LMS ↔ Qualiopi | `.env` serveur + GitHub Secrets |
| `S3_ACCESS_KEY` | OVH Object Storage | `.env` serveur + GitHub Secrets |
| `S3_SECRET_KEY` | OVH Object Storage | `.env` serveur + GitHub Secrets |
| `SMTP_PASSWORD` | Envoi emails | `.env` serveur |
| `CHATWOOT_SECRET_KEY` | WeWill SECRET_KEY_BASE | `.env` serveur |
| `MEILISEARCH_MASTER_KEY` | Meilisearch API | `.env` serveur |

---

## 13. CONVENTION DE NOMMAGE

### 13.1 Nommage des branches Git

| Pattern | Usage | Exemple |
|---------|-------|---------|
| `main` | Production | — |
| `staging` | Pre-production | — |
| `feature/{description}` | Nouvelle fonctionnalite | `feature/qualiopi-scorecard` |
| `fix/{description}` | Correction de bug | `fix/pdf-logo-missing` |
| `hotfix/{description}` | Correctif urgent prod | `hotfix/500-dashboard` |
| `docs/{description}` | Documentation | `docs/api-specification` |

### 13.2 Nommage des commits (Conventional Commits)

| Prefix | Type | Bump version |
|--------|------|-------------|
| `feat:` | Nouvelle fonctionnalite | Minor |
| `fix:` | Correction de bug | Patch |
| `docs:` | Documentation | — |
| `chore:` | Maintenance | — |
| `refactor:` | Refactoring | — |
| `test:` | Tests | — |
| `ci:` | CI/CD | — |
| `perf:` | Performance | — |
| `feat!:` | Breaking change | Major |

### 13.3 Nommage des tags

| Pattern | Exemple | Usage |
|---------|---------|-------|
| `v{major}.{minor}.{patch}` | `v1.3.0` | Release stable |
| `v{major}.{minor}.{patch}-rc.{n}` | `v1.3.0-rc.1` | Release candidate |
| `v{major}.{minor}.{patch}-beta.{n}` | `v1.3.0-beta.1` | Beta |

### 13.4 Nommage des fichiers et documents

| Type | Convention | Exemple |
|------|-----------|---------|
| Document Markdown | UPPER_SNAKE_CASE.md | `CAHIER_DES_CHARGES_QUALIOPI.md` |
| Code Python | snake_case.py | `pdf_generator.py` |
| Templates HTML | snake_case.html | `admin_dashboard.html` |
| CSS/SCSS | kebab-case.scss | `lms-main-v1.scss` |
| Images | kebab-case.png | `logo-mission.png` |
| PDF generes | snake_case_{variables}.pdf | `attestation_VTC_jean_dupont.pdf` |
