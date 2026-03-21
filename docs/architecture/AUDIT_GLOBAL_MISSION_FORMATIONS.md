# Audit global — Mission Formations

> Version 1.0 — 21 mars 2026
> Audit holistique : tech, produit, commercial, securite, organisation
> Analyse multi-role pour un dev solo gerant un projet d'envergure

---

## PREAMBULE — CE QUE TU ES EN TRAIN DE CONSTRUIRE

Tu ne construis pas "un site de formation". Tu construis un **ecosysteme SaaS B2B2C
de formation professionnelle certifie**, avec :

- Une plateforme LMS (OpenEdX)
- Un ERP (Odoo)
- Un outil de conformite reglementaire (Qualiopi)
- Un chat support (WeWill)
- Un site vitrine commercial
- Une infrastructure multi-tenant (academies B2B)
- Des integrations multi-financeurs (OPCO, CPF, Mission Locale, CSE)
- Des obligations legales (Qualiopi, RGPD, Code du travail)

C'est l'equivalent d'une startup avec 5-8 personnes. Tu es seul.
Cet audit identifie TOUT ce qui manque pour reussir.

---

## PARTIE 1 — AUDIT TECHNIQUE (Role : CTO / Lead Dev)

### 1.1 Ce qui est bien fait

| Element | Commentaire |
|---------|-------------|
| Architecture hybride (Option C) | Bonne decision — isolation LMS, pas de risque pour les apprenants |
| Celery async pour les PDFs | Correct — jamais de blocage du LMS |
| MySQL read-only | Bon compromis couplage/performance |
| Theme Mako custom | Bien structure, CSS pre-compile |
| Tests existants (151+) | Bon depart |
| Documentation exhaustive | Rare pour un dev solo, tres bien |
| CI/CD planifie | GitHub Actions = bon choix |

### 1.2 Points d'amelioration techniques

| # | Probleme | Risque | Recommandation |
|---|----------|--------|----------------|
| T-01 | **Pas de monitoring serveur** | Tu ne sauras pas quand le serveur est en difficulte AVANT qu'il crash | Installer Netdata (1 commande Docker) ou Uptime Kuma pour le monitoring + alertes |
| T-02 | **Pas de backup automatise** | Perte de donnees catastrophique (MySQL, MongoDB, PostgreSQL Qualiopi) | Script cron quotidien → backup sur OVH Object Storage (S3). Tester la restauration une fois |
| T-03 | **Pas de strategie de rollback** | Si un deploy casse la prod, comment tu reviens en arriere ? | Tags Git + Docker images taggees par SHA. Procedure documentee : "en cas de probleme, deploy le tag precedent" |
| T-04 | **Secrets dans le repo** | `.secrets.env` dans tutor-patches/ — meme .gitignore, risque d'erreur | Migrer vers GitHub Secrets + variables d'environnement serveur. Ne jamais avoir de fichier secrets dans le repo |
| T-05 | **Pas de staging automatise** | Le staging n'est pas un miroir fidele de la prod | Procedure "staging = copie de prod" : meme version, meme config, donnees anonymisees |
| T-06 | **2 workers uWSGI** | Avec 100+ apprenants simultanes, 2 workers = goulot | Passer a 4 workers sur le VPS 32 Go. Chaque worker = ~400 Mo RAM |
| T-07 | **Pas de CDN** | Les assets statiques (CSS, JS, images) servis depuis le VPS = lent | Cloudflare gratuit devant le domaine. Cache les assets, protege contre les DDoS |
| T-08 | **Pas de rate limiting sur le LMS** | Un bot ou un scraper peut saturer le serveur | Configurer le rate limiting Caddy ou Django (django-ratelimit) |
| T-09 | **Pas de logs centralises** | Debug = SSH + docker logs + grep a la main | Loki + Grafana (gratuit, Docker) ou au minimum un fichier de log rotated avec logrotate |
| T-10 | **Pas de tests end-to-end** | Les tests unitaires ne garantissent pas que le parcours apprenant fonctionne | Playwright ou Cypress : 3-5 tests E2E critiques (inscription, connexion, cours, quiz, certificat) |
| T-11 | **Pas de health check unifie** | 4 services independants, pas de vue globale | Endpoint `/api/v1/config/health` dans l'app Qualiopi (prevu dans l'API) + page status publique |
| T-12 | **Base MongoDB non securisee** | `no auth, no SSL` dans la config actuelle | Activer l'authentification MongoDB meme en local (principe du moindre privilege) |
| T-13 | **Pas de chiffrement des backups** | Si le bucket S3 est compromis, les donnees sont lisibles | Chiffrer les backups avec GPG avant upload sur S3 |
| T-14 | **Pas de plan de reprise d'activite (PRA)** | Si le VPS meurt, combien de temps pour remonter ? | Documenter : "en cas de perte du VPS, voici les etapes pour remonter en 4h" |

### 1.3 Dette technique identifiee

| # | Dette | Impact | Priorite |
|---|-------|--------|----------|
| DT-01 | `mission_central_admin` fait 2 623 lignes et gere trop de choses (dashboard, PDFs, emails, academy, middleware) | Difficile a maintenir, monolithique | Haute — la migration vers mission-qualiopi resoudra ca |
| DT-02 | 8 migrations fake-applied sans tables (signale dans le TODO) | Risque de conflit lors d'un upgrade Tutor | Moyenne — a evaluer et corriger avant upgrade |
| DT-03 | Le dashboard admin a des donnees hardcodees (revenus, analytics, planning) | Les onglets ne servent a rien tant qu'ils ne sont pas connectes | Basse — sera resolu par l'integration Odoo (Sprint 4) |
| DT-04 | Les MFEs non utilises consomment des ressources | Charge CPU inutile sur les API LMS | Moyenne — desactiver Communications, ORA Grading, Profile |
| DT-05 | Pas de versionning semantique | Impossible de savoir quelle version tourne en staging/prod | Haute — implementer avec le CI/CD |

---

## PARTIE 2 — AUDIT PRODUIT (Role : Product Manager)

### 2.1 Vision produit — ce qui manque

| # | Element | Statut | Impact |
|---|---------|--------|--------|
| P-01 | **Personas documentes** | Absent | Tu developpes sans savoir precisement pour qui. Il faut 4 personas : apprenant individuel, RH entreprise, formateur, auditeur Qualiopi |
| P-02 | **Parcours utilisateur (user journeys)** | Absent | Chaque persona a un parcours. Ex : "RH entreprise" = decouverte → devis → convention → inscription collaborateurs → suivi → bilan. Ces parcours doivent etre documentes et testes |
| P-03 | **MVP vs V2 vs V3** | Flou | Tu as 265h de travail planifie mais tout est au meme niveau de priorite. Il faut un MVP strict : qu'est-ce qui est INDISPENSABLE pour le premier client payant ? |
| P-04 | **Proposition de valeur unique** | Non formalisee | Pourquoi un client choisirait Mission Formations plutot que 360Learning, Digiforma, Dendreo, ou un LMS gratuit ? |
| P-05 | **Pricing strategy** | Absent | Comment tu factures ? Par apprenant ? Par formation ? Par academie ? Abonnement mensuel ? A la carte ? OPCO = forfait ? |
| P-06 | **Onboarding client** | Absent | Le premier client B2B arrive, que se passe-t-il ? Qui cree l'academie ? Qui importe les stagiaires ? Qui configure les formations ? |
| P-07 | **Feedback loop** | Absent | Comment tu collectes les retours des premiers utilisateurs pour ameliorer le produit ? (les enquetes Qualiopi ne suffisent pas, c'est de la conformite, pas du produit) |
| P-08 | **Roadmap produit vs roadmap technique** | Confondu | La roadmap actuelle est 100% technique. Il faut une roadmap produit : quelles fonctionnalites pour quels clients a quelle date |

### 2.2 Definition du MVP (Minimum Viable Product)

**Question cle : que faut-il pour accueillir le PREMIER client payant ?**

| Indispensable (MVP) | Peut attendre (V2) |
|---------------------|-------------------|
| 1 formation complete dans Studio | 100+ formations |
| Inscription manuelle par l'admin | Inscription auto via Odoo e-commerce |
| Paiement par virement (hors plateforme) | Paiement Stripe en ligne |
| Attestation PDF (DOC-07) | Les 22 PDFs Qualiopi |
| Dashboard apprenant basique | Dashboard apprenant enrichi |
| Email de bienvenue manuel | 12 workflows automatises |
| Scorecard Qualiopi basique (checklist) | Scorecard auto avec Celery beat |
| Convention B2B en Word/PDF | Convention generee + signature electronique |
| Chat WeWill fonctionnel | Chat avec webhooks Odoo |
| Site vitrine simple | Site complet avec e-commerce |

**Le MVP c'est ~80h, pas 265h.** Tu peux avoir ton premier client en 4-6 semaines au lieu de 14.

### 2.3 Metriques produit a suivre

| Metrique | Pourquoi | Source |
|----------|----------|--------|
| **Taux de completion** | Les apprenants finissent-ils les formations ? | OpenEdX grades |
| **Taux de satisfaction** | La qualite percue | Enquetes satisfaction (Qualiopi) |
| **Taux d'abandon** | Alerte qualite + perte de revenus | Qualiopi workflow 4 |
| **NPS** | Recommandation = croissance organique | Enquetes satisfaction |
| **Time to first course** | Combien de temps entre l'inscription et le 1er module ? | Tracking OpenEdX |
| **Revenue per learner** | Rentabilite par apprenant | Odoo |
| **Customer Acquisition Cost** | Combien coute un nouveau client ? | Odoo CRM + marketing |
| **Churn rate** | Les clients B2B renouvellent-ils ? | Odoo abonnements |
| **Time to resolution** | Delai de reponse aux reclamations | Qualiopi registre |
| **Uptime** | Disponibilite de la plateforme | Monitoring |

---

## PARTIE 3 — AUDIT COMMERCIAL (Role : Directeur Commercial)

### 3.1 Ce qui manque pour vendre

| # | Element | Statut | Impact |
|---|---------|--------|--------|
| C-01 | **Page de vente par formation** | Absente (page /catalogue/ = liste basique) | Le prospect ne peut pas comprendre la valeur de chaque formation ni s'inscrire en ligne |
| C-02 | **Processus de devis/commande** | Manuel (email, telephone) | Friction enorme. Un prospect qui ne peut pas acheter en 3 clics = prospect perdu |
| C-03 | **Page "Entreprises"** | Absente (prevue Sprint 4.3) | Les RH ne trouvent pas les informations B2B (volume, sur-mesure, OPCO) |
| C-04 | **Temoignages / preuves sociales** | Absents | Aucune credibilite. "0 avis" = pas de confiance |
| C-05 | **SEO** | Non travaille | Le site n'apparait pas dans Google. Pas de contenu blog, pas de mots-cles, pas de backlinks |
| C-06 | **Tunnel de conversion** | Inexistant | Prospect → Lead → Devis → Client : aucune automatisation, aucun suivi |
| C-07 | **Email marketing** | Non configure | Pas de newsletter, pas de nurturing, pas de relance prospects |
| C-08 | **Presence sur les annuaires** | Non faite | MonCompteFormation (CPF), DataDock, annuaires OPCO, Google Business |
| C-09 | **Partenariats** | Non formalises | OPCO, Mission Locale, CCI, Pole Emploi — aucune convention signee |
| C-10 | **Kit commercial** | Inexistant | Plaquette PDF, presentation PowerPoint, grille tarifaire — rien de pret pour envoyer a un prospect |

### 3.2 Strategie commerciale recommandee

**Phase 1 — Les 3 premiers clients (mois 1-2)**

| Action | Comment |
|--------|---------|
| Identifier 10 prospects B2B dans ton reseau | Liste de contacts existants, LinkedIn |
| Preparer un kit commercial basique | 1 plaquette PDF + 1 grille tarifaire + 1 demo en ligne |
| Faire 10 demos en visio | Montrer le LMS + le dashboard + les formations |
| Signer 3 conventions | Objectif : 3 entreprises × 5-10 stagiaires |
| Delivrer la formation VTC (deja prete) | Prouver que ca marche |

**Phase 2 — Referencement et visibilite (mois 3-4)**

| Action | Comment |
|--------|---------|
| S'inscrire sur MonCompteFormation | CPF = flux de clients automatique |
| Contacter les OPCO cles | OPCO Mobilites (VTC), Atlas (bureautique/IA), etc. |
| Publier 5 articles SEO | Blog sur le site : "formation VTC", "financement OPCO", etc. |
| Creer un profil Google Business | Visibilite locale |
| Collecter les premiers temoignages | Demander aux 3 premiers clients |

**Phase 3 — Scaling (mois 5-12)**

| Action | Comment |
|--------|---------|
| E-commerce (Odoo + Stripe) | Achat en ligne sans friction |
| Campagnes email (Odoo Email Marketing) | Nurturing prospects |
| Partenariats formalises | Conventions CCI, Mission Locale, CSE |
| Embaucher un commercial | Quand CA > 10k€/mois |

### 3.3 Kit commercial a creer

| Document | Format | Contenu | Priorite |
|----------|--------|---------|----------|
| Plaquette commerciale | PDF 4 pages | Presentation MF, formations, certif Qualiopi, contact | Urgente |
| Grille tarifaire | PDF 1 page | Prix par formation, degressivite volume, OPCO | Urgente |
| Presentation deck | PowerPoint/PDF 15 slides | Pour les demos en visio | Haute |
| Page de vente par formation | Web | Objectifs, programme, tarif, CTA inscription | Haute |
| Dossier de prise en charge OPCO | PDF pre-rempli | Faciliter la demande OPCO pour le client | Moyenne |
| Etude de cas / temoignage | PDF 1 page | Retour d'experience d'un client | Apres les 3 premiers clients |

---

## PARTIE 4 — AUDIT ARCHITECTURE ET INFRASTRUCTURE (Role : Architecte Solutions)

### 4.1 Points d'attention architecture

| # | Element | Risque | Recommandation |
|---|---------|--------|----------------|
| A-01 | **Single point of failure** | Le VPS OVH est unique. S'il tombe, tout est down | Court terme : backup quotidien + PRA documente. Long terme : 2 VPS (LMS + services) |
| A-02 | **Pas de load balancer** | Impossible de scaler horizontalement | Pas necessaire avant 500+ apprenants. Mais prevoir dans l'architecture |
| A-03 | **Pas de cache applicatif** | Les pages LMS sont generees a chaque requete | Activer le cache Memcached ou Redis pour les pages lourdes (catalogue, dashboard) |
| A-04 | **Object Storage pas configure** | Les videos seront sur le disque du VPS | Configurer OVH Object Storage AVANT d'uploader des videos. C'est un prerequis absolu |
| A-05 | **DNS sans failover** | Le DNS pointe vers une seule IP | Cloudflare en proxy = failover, cache, DDoS protection, SSL gratuit |
| A-06 | **Pas de separation DB** | MySQL contient les donnees OpenEdX ET le plugin custom | La migration vers Qualiopi (PostgreSQL separe) resout ce probleme |
| A-07 | **Pas d'environnement de dev local** | Tu developpes directement sur staging ? | Docker Compose local qui reproduit l'environnement complet (LMS + Qualiopi + Redis + MySQL) |
| A-08 | **Pas de feature flags** | Toute nouvelle fonctionnalite est deployee pour tout le monde ou personne | Django Waffle ou feature flags simples dans QualiopiConfig |
| A-09 | **WeWill sur le meme VPS** | 900 Mo de RAM pour un chat | Externaliser sur un petit VPS dedie (8€/mois) ou Chatwoot Cloud |

### 4.2 Architecture cible a 12 mois

```
                        ARCHITECTURE CIBLE — DECEMBRE 2026
                    ═══════════════════════════════════════════

                              Cloudflare (CDN + DDoS + SSL)
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            VPS 1 — LMS         VPS 2 — Services     Odoo.sh (SaaS)
            (32 Go RAM)         (8-16 Go RAM)
            ┌──────────┐       ┌──────────────┐     ┌──────────┐
            │ OpenEdX  │       │ App Qualiopi │     │ CRM      │
            │ LMS+CMS  │◄────►│ (Django+DRF) │◄───►│ Ventes   │
            │ MySQL    │       │ PostgreSQL   │     │ Compta   │
            │ MongoDB  │       │ Celery       │     │ Factures │
            │ Redis    │       │ Redis        │     └──────────┘
            │ Meili    │       │ WeWill       │
            │ Caddy    │       │ Monitoring   │
            └──────────┘       └──────────────┘

                    ┌──────────────────────────────────┐
                    │     OVH Object Storage (S3)      │
                    │  Videos, PDFs, backups, medias    │
                    └──────────────────────────────────┘
```

### 4.3 Scalabilite — plan de croissance infra

| Seuil | Action | Cout |
|-------|--------|------|
| **0-50 apprenants** | VPS 32 Go unique + Odoo.sh | ~120€/mois |
| **50-200 apprenants** | + VPS 8 Go pour services (Qualiopi + WeWill) | +40€/mois |
| **200-500 apprenants** | VPS 64 Go LMS + VPS 16 Go services + CDN | ~250€/mois |
| **500-1000 apprenants** | Cluster Kubernetes OVH ou migration cloud | ~400-600€/mois |
| **1000+ apprenants** | Architecture distribuee complete | Budget a reevaluer |

---

## PARTIE 5 — AUDIT SECURITE (Role : RSSI / DPO)

### 5.1 Conformite RGPD

| # | Obligation | Statut | Action |
|---|-----------|--------|--------|
| S-01 | **Registre des traitements** | Absent | Creer le registre RGPD (obligatoire pour un OF). Lister tous les traitements de donnees personnelles |
| S-02 | **DPO / referent RGPD** | Non designe | Designer un responsable (peut etre toi). Publier ses coordonnees sur le site |
| S-03 | **Politique de confidentialite** | Redirect vers missionformations.com | Creer une vraie politique detaillee pour la plateforme LMS (cookies, tracking, donnees, duree conservation) |
| S-04 | **Consentement cookies** | Absent | Installer une banniere cookies (conforme CNIL). Le LMS OpenEdX utilise des cookies de session + tracking |
| S-05 | **Droit a l'effacement** | Non implemente | Procedure pour supprimer toutes les donnees d'un apprenant sur demande. OpenEdX a des commandes `retire_user` mais il faut aussi les bases Qualiopi et Odoo |
| S-06 | **Duree de conservation** | Non definie | Definir combien de temps les donnees sont conservees (ex: 5 ans apres fin de formation pour Qualiopi, 10 ans pour la comptabilite) |
| S-07 | **Sous-traitants** | Non documentes | Lister tous les sous-traitants qui traitent des donnees : OVH, Odoo.sh, (Chatwoot Cloud si applicable), Stripe, SMTP provider |
| S-08 | **Contrats sous-traitance RGPD** | Absents | Chaque sous-traitant doit avoir un contrat RGPD (article 28). OVH et Odoo.sh en ont par defaut, mais il faut les archiver |
| S-09 | **Analyse d'impact (AIPD)** | Non faite | Recommandee pour les donnees de formation (evaluations, progression, connexion = suivi systematique) |
| S-10 | **Notification de violation** | Pas de procedure | Que faire si une breche de donnees est detectee ? Procedure : 72h pour notifier la CNIL, informer les personnes concernees |

### 5.2 Securite technique

| # | Risque | Statut | Action |
|---|--------|--------|--------|
| S-11 | **Secrets exposes dans l'historique Git** | Detecte (JWT, Meilisearch) | Rotation immediate des secrets. Utiliser `git-filter-repo` pour nettoyer l'historique si necessaire |
| S-12 | **MongoDB sans authentification** | Confirme | Activer l'auth MongoDB. Creer un user dedie pour OpenEdX |
| S-13 | **Pas de WAF (Web Application Firewall)** | Non configure | Cloudflare Free inclut un WAF basique. Suffisant pour commencer |
| S-14 | **Pas d'audit de securite** | Jamais fait | Faire un scan OWASP ZAP (gratuit) sur le site staging. Corriger les vulnerabilites critiques |
| S-15 | **Pas de politique de mots de passe** | Defaut OpenEdX | Verifier : longueur minimale 12 caracteres, complexite, blocage apres 5 tentatives |
| S-16 | **Pas de 2FA pour les admins** | Non active | Activer le 2FA pour les comptes superuser (toi + futurs admins) |
| S-17 | **SSH root direct** | Probable | Creer un user `deploy` avec sudo. Desactiver le login root SSH. Cle SSH uniquement (pas de mot de passe) |
| S-18 | **Pas de pare-feu** | A verifier | Configurer `ufw` : ouvrir uniquement 22 (SSH), 80 (HTTP), 443 (HTTPS). Tout le reste ferme |
| S-19 | **Pas de mise a jour automatique** | A verifier | Activer `unattended-upgrades` pour les patches de securite Ubuntu |
| S-20 | **Pas de scan de dependances** | Non configure | GitHub Dependabot ou Snyk gratuit : alerte quand une dependance Python/Node a une CVE |

### 5.3 Plan de securite prioritise

| Priorite | Actions | Effort |
|----------|---------|--------|
| **Urgente (cette semaine)** | Rotation secrets (S-11), pare-feu (S-18), SSH securise (S-17) | 2h |
| **Haute (Sprint 0)** | MongoDB auth (S-12), 2FA admins (S-16), Cloudflare (S-13, A-05) | 3h |
| **Moyenne (Sprint 1)** | Registre RGPD (S-01), politique confidentialite (S-03), banniere cookies (S-04) | 4h |
| **Normale (Sprint 2+)** | OWASP scan (S-14), Dependabot (S-20), procedure effacement (S-05) | 3h |

---

## PARTIE 6 — AUDIT ORGANISATIONNEL (Role : COO / Chef de projet)

### 6.1 Le probleme du dev solo

| Risque | Description | Mitigation |
|--------|------------|------------|
| **Bus factor = 1** | Si tu es malade, en vacances, ou indisponible, tout s'arrete | Documentation exhaustive (deja bien faite), runbooks, procedures |
| **Surcharge cognitive** | Tu es dev + admin sys + commercial + comptable + support + formateur | Prioriser impitoyablement. Dire non a tout ce qui n'est pas le MVP |
| **Pas de revue de code** | Personne ne relit ton code. Les bugs passent | Tests automatises + CI/CD = ta "revue de code" automatique |
| **Pas de separation des preoccupations** | Tu penses prod, commercial, Qualiopi, et infra en meme temps | Bloquer des creneaux : lundi-mardi = dev, mercredi = commercial, jeudi = admin/Qualiopi, vendredi = support/ops |
| **Isolement** | Pas de collegues pour discuter des decisions | Les sessions avec les IA (Claude, Gemini, etc.) remplacent partiellement. Mais chercher une communaute (forum OpenEdX, meetups formation pro) |

### 6.2 Organisation recommandee

**Rythme hebdomadaire :**

| Jour | Focus | Activites |
|------|-------|-----------|
| **Lundi** | Dev (build) | Coder les fonctionnalites, merger les PRs |
| **Mardi** | Dev (build) | Coder, tests, deployer staging |
| **Mercredi** | Commercial + Produit | Prospection, demos, devis, suivi clients |
| **Jeudi** | Admin + Qualiopi | Documents admin, mise a jour registres, veille |
| **Vendredi** | Ops + Support | Monitoring, maintenance, support apprenants, backups |

**Rythme mensuel :**

| Semaine | Focus |
|---------|-------|
| Semaine 1 | Sprint dev (nouvelles fonctionnalites) |
| Semaine 2 | Sprint dev (suite + tests) |
| Semaine 3 | Commercial + contenu (nouvelles formations, demos) |
| Semaine 4 | Admin + Qualiopi + bilan du mois |

### 6.3 Outils d'organisation recommandes

| Besoin | Outil | Cout |
|--------|-------|------|
| Gestion de taches | **GitHub Issues + Projects** (deja dans l'ecosysteme) | Gratuit |
| Notes et docs | **mission-docs** (repo Git) ou **Notion** | Gratuit |
| Comptabilite | **Odoo Comptabilite** (deja prevu) | Inclus Odoo.sh |
| Email pro | Deja configure (missionformations.com) | Existant |
| Visio pour les demos | **Google Meet** ou **Zoom** (gratuit pour 1-1) | Gratuit |
| Calendrier | **Google Calendar** | Gratuit |
| Signature electronique | **Odoo Signature** (prevu) | Inclus Odoo.sh |

### 6.4 Quand embaucher / externaliser

| Seuil | Poste | Pourquoi |
|-------|-------|----------|
| **CA > 5k€/mois** | Assistant administratif (freelance, mi-temps) | Decharger la gestion OPCO, factures, relances |
| **CA > 10k€/mois** | Commercial (freelance ou stage) | Prospection, demos, suivi pipeline |
| **CA > 20k€/mois** | Developpeur junior (freelance) | Maintenance, bugs, petites features |
| **10+ formations** | Ingenieur pedagogique (freelance) | Creer le contenu des formations (texte, quiz, structure) |
| **Audit Qualiopi** | Consultant Qualiopi (ponctuel) | Preparer l'audit, verifier la conformite |

---

## PARTIE 7 — AUDIT LEGAL ET REGLEMENTAIRE (Role : Juriste / Responsable conformite)

### 7.1 Obligations legales d'un organisme de formation

| # | Obligation | Statut | Urgence |
|---|-----------|--------|---------|
| L-01 | **Declaration d'activite** (N° DA aupres du prefet de region) | A verifier | Bloquante — sans N° DA, tu ne peux pas facturer de la formation |
| L-02 | **Bilan pedagogique et financier (BPF)** | Pas encore (normal, premiere annee) | Annuel — a faire avant le 30 avril de l'annee suivante |
| L-03 | **Certification Qualiopi** | En preparation | Obligatoire pour les financements publics (OPCO, CPF) depuis 2022 |
| L-04 | **CGV specifiques formation pro** | Redirect vers site principal | A creer : CGV specifiques conformes au Code du travail (L.6353-1 et suivants) |
| L-05 | **Reglement interieur** | DOC-05 prevu | Obligatoire pour tout OF. Doit etre affiche et communique |
| L-06 | **Assurance RC Pro** | A verifier | Obligatoire pour exercer. Verifier la couverture (formation pro + e-learning) |
| L-07 | **Exoneration TVA** | A demander | Les OF peuvent etre exoneres de TVA (art. 261-4-4° du CGI). Demande aupres de la DIRECCTE |
| L-08 | **Mentions legales du site** | A verifier | Obligatoires : editeur, hebergeur, DPO, N° DA, SIRET |
| L-09 | **Accessibilite (RGAA)** | Non evaluee | Les OF certifies Qualiopi doivent avoir un referent handicap et documenter l'accessibilite |
| L-10 | **Contrats formateurs** | A formaliser | Les formateurs independants doivent avoir un contrat ou bon de commande AVANT chaque intervention (Ind. 21) |

### 7.2 Conformite specifique e-learning

| # | Obligation | Comment |
|---|-----------|---------|
| LE-01 | Prouver la realisation effective (pas juste "il s'est connecte") | Feuille d'emargement basee sur les logs de connexion + activites realisees (quiz, modules completes) |
| LE-02 | Duree effective ≠ duree prevue | Tracker le temps reel passe (pas juste la duree du cours). Documenter les ecarts |
| LE-03 | Accompagnement pedagogique | Prouver qu'un formateur est disponible (pas juste un LMS auto-gere). Chat, forum, visio, suivi |
| LE-04 | Evaluation des acquis | Les QCM OpenEdX suffisent si ils sont bien documentes et notes |
| LE-05 | Certificat de realisation | Obligatoire pour chaque financement (OPCO, CPF). DOC-08 prevu |

---

## PARTIE 8 — AUDIT CONTENU ET PEDAGOGIE (Role : Responsable pedagogique)

### 8.1 Etat des formations

| Formation | Contenu | Pret pour un vrai apprenant ? |
|-----------|---------|-------------------------------|
| Certificat VTC (MF-VTC) | OLX complet (8 chapters, 27 HTML, 17 quiz) | **Oui** (texte uniquement, pas de video) |
| MF-VTC-2025 | OLX complet | **Oui** |
| 8 autres formations | Cours vides (crees dans Studio) | **Non** — structure a creer |

### 8.2 Ce qui manque pour des formations de qualite

| # | Element | Statut | Impact |
|---|---------|--------|--------|
| PED-01 | **Videos pedagogiques** | Aucune | L'e-learning sans video = faible engagement. Prevoir 5-10 videos par formation |
| PED-02 | **Cas pratiques / mises en situation** | Absents | Les quiz QCM ne suffisent pas pour la certification. Ajouter des cas pratiques, simulations |
| PED-03 | **Ressources telechargeables** | Absentes | Fiches memo, supports de cours PDF, templates — les apprenants veulent du materiel |
| PED-04 | **Forum / communaute** | MFE Discussions installe mais pas utilise | L'interaction entre apprenants = meilleur engagement et completion |
| PED-05 | **Sessions live (visio)** | Non configure | Masterclass, classes virtuelles, Q&A — necessaire pour Qualiopi (prouver l'accompagnement) |
| PED-06 | **Parcours adaptatifs** | Non implemente | Les apprenants avances sautent les bases, les debutants ont du contenu supplementaire |
| PED-07 | **Gamification** | Non implementee | Badges, points, classements = meilleur engagement |
| PED-08 | **Accessibilite** | Non evaluee | Sous-titres videos, transcriptions, compatibilite lecteur d'ecran |

### 8.3 Strategie contenu recommandee

**Phase 1 (MVP) :**
- Formation VTC deja prete → la livrer telle quelle
- Ajouter 2-3 formations courtes (< 10h) dans des domaines a forte demande

**Phase 2 :**
- Ajouter des videos (filmer soi-meme ou acheter du stock)
- Integrer des classes virtuelles (BigBlueButton ou Zoom XBlock)
- Ajouter des cas pratiques

**Phase 3 :**
- Gamification (badges OpenEdX)
- Parcours adaptatifs
- Sous-titres et accessibilite

---

## PARTIE 9 — PLAN D'ACTION PRIORITISE (tous roles confondus)

### Urgences absolues (avant tout developpement)

| # | Action | Role | Effort | Bloquant pour |
|---|--------|------|--------|---------------|
| 1 | Verifier le N° de declaration d'activite | Legal | 1h | Facturation |
| 2 | Rotation des secrets exposes | Securite | 30min | Securite prod |
| 3 | Configurer le pare-feu (ufw) | Securite | 15min | Securite prod |
| 4 | Securiser SSH (pas de root, cle uniquement) | Securite | 30min | Securite prod |
| 5 | Configurer les backups automatiques | Infra | 2h | Continuite |

### Haute priorite (Sprint 0)

| # | Action | Role | Effort |
|---|--------|------|--------|
| 6 | Upgrade VPS 32 Go | Infra | 1h |
| 7 | Tuning RAM (MongoDB, MySQL) | Infra | 30min |
| 8 | Cloudflare devant le domaine | Infra + Securite | 1h |
| 9 | Definir les personas (4 fiches) | Produit | 2h |
| 10 | Definir le MVP strict | Produit | 2h |
| 11 | Creer la plaquette commerciale | Commercial | 3h |
| 12 | Creer la grille tarifaire | Commercial | 1h |
| 13 | Creer l'organisation GitHub + 8 repos | Tech | 1h |

### Moyenne priorite (Sprint 1-2)

| # | Action | Role | Effort |
|---|--------|------|--------|
| 14 | Registre RGPD + politique confidentialite | Legal/RGPD | 4h |
| 15 | CGV specifiques formation pro | Legal | 3h |
| 16 | App Qualiopi (squelette) | Tech | 22h |
| 17 | 22 PDFs brandes | Tech | 40h |
| 18 | CI/CD GitHub Actions | Tech | 10h |
| 19 | Page "Entreprises" sur le site | Commercial | 4h |
| 20 | Contacter 10 prospects B2B | Commercial | 5h |

### Normale priorite (Sprint 3+)

| # | Action | Role | Effort |
|---|--------|------|--------|
| 21 | Setup Odoo.sh | Tech + Commercial | 10h |
| 22 | Webhooks inter-services | Tech | 15h |
| 23 | 8 nouvelles formations dans Studio | Pedagogie | 30h |
| 24 | Videos pedagogiques | Pedagogie | 20h+ |
| 25 | SEO + blog | Marketing | Continu |
| 26 | Inscription MonCompteFormation (CPF) | Commercial + Legal | 5h |
| 27 | Partenariats OPCO | Commercial | Continu |

---

## PARTIE 10 — CE QUE TU NE VOIS PAS (angles morts)

### 10.1 Risques business

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| **Pas de client pendant 3 mois** | Moyenne | Critique (tresorerie) | Commencer la prospection MAINTENANT, pas apres le dev. Le MVP suffit pour signer |
| **Qualiopi refuse a l'audit** | Faible (si bien prepare) | Haute (pas de financements publics) | Consultant Qualiopi ponctuel pour preparer l'audit. Le module Qualiopi aide mais ne remplace pas la preparation |
| **OpenEdX trop complexe pour les apprenants** | Moyenne | Haute (abandon) | Tester avec 5 vrais utilisateurs AVANT la mise en prod. Simplifier l'UX si necessaire |
| **Un concurrent sort un produit similaire** | Elevee | Moyenne | Se differencier par le service, pas la tech. L'accompagnement humain + Qualiopi integre = avantage |
| **Burnout du dev solo** | Elevee | Critique | Planifier des pauses, externaliser tot (assistant admin des 5k€/mois), ne pas tout faire en meme temps |

### 10.2 Risques techniques

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| **Upgrade Tutor casse le plugin** | Moyenne | Haute | Tests CI avant upgrade. Rester sur Tutor v21 tant que ca marche. Ne pas upgrader sans raison |
| **OVH en panne** | Faible | Critique | Backup sur un autre provider (Scaleway, AWS S3). PRA documente |
| **Fuite de donnees** | Faible | Critique (RGPD + reputation) | Securite (partie 5), chiffrement backups, audit OWASP |
| **Le hub API Qualiopi = single point of failure** | Moyenne | Haute | Health check + restart automatique (Docker restart: unless-stopped) + monitoring |
| **Performance degradee avec 100+ formations** | Moyenne | Haute | Test de charge AVANT la mise en prod. Optimiser les requetes MySQL, ajouter des index |

### 10.3 Ce que les autres ne te diront pas

1. **Tu n'as pas besoin de 100 formations pour lancer.** 1 formation bien faite + 3 clients = mieux que 100 formations vides + 0 clients.

2. **Le code parfait n'existe pas pour un dev solo.** Accepte la dette technique raisonnable. Refactore quand ca fait mal, pas avant.

3. **Le commercial est plus important que le dev a ce stade.** Tu as un LMS fonctionnel. Ce qui manque c'est des clients, pas des features.

4. **L'audit Qualiopi n'est pas un examen technique.** L'auditeur verifie les processus et les preuves, pas le code. Un Excel bien rempli vaut mieux qu'une app Qualiopi vide.

5. **La veille RSS automatique est du nice-to-have.** Pour l'audit, un Google Alert + un fichier de notes suffit. L'automatisation viendra apres.

6. **Les 12 workflows automatises sont de l'over-engineering pour le jour 1.** Commence par des boutons manuels. Automatise quand tu as le volume qui le justifie (> 50 apprenants).

7. **La separation en 8 repos est correcte pour l'organisation mais pas urgente.** Tu peux garder le monorepo quelques mois de plus. La separation a du sens quand tu as un CI/CD en place.

8. **Le plus grand risque n'est pas technique, c'est de ne pas vendre.** Consacre 30% de ton temps au commercial des maintenant.

---

## RESUME EXECUTIF

### Les 5 actions les plus importantes (dans l'ordre)

| # | Action | Pourquoi |
|---|--------|----------|
| **1** | **Securiser le serveur** (secrets, pare-feu, SSH, backups) | Tu ne peux pas mettre en prod un serveur non securise avec des apprenants payants |
| **2** | **Definir le MVP et arreter de planifier** | Tu as 8 500 lignes de documentation et 0 client. Commence a vendre |
| **3** | **Creer le kit commercial** (plaquette + tarifs + demo) | Sans ca, impossible de prospecter |
| **4** | **Signer 3 clients avec la formation VTC** | Prouver le modele avant de construire 100 features |
| **5** | **Implementer le module Qualiopi (MVP)** | Necessaire pour les financements OPCO/CPF qui representent le gros du marche |

### Budget mensuel cible

| Poste | Cout |
|-------|------|
| VPS OVH 32 Go | ~45€ |
| Odoo.sh (3 users) | ~75€ |
| OVH Object Storage | ~10€ |
| Cloudflare | Gratuit |
| Domaine | ~5€ |
| WeWill (VPS dedie 4 Go) | ~8€ |
| **Total** | **~143€/mois** |

### Objectif a 6 mois

| Metrique | Cible |
|----------|-------|
| Formations actives | 5-10 |
| Apprenants inscrits | 50-100 |
| Clients B2B | 3-5 |
| CA mensuel | 5-10k€ |
| Taux satisfaction | > 4/5 |
| Taux completion | > 70% |
| Conformite Qualiopi | Pret pour l'audit |
