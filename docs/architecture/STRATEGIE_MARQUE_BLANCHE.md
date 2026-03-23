# Strategie Marque Blanche — Mission Formations

> Version 1.0 — 23 mars 2026
> Vision : LMS revendable en marque blanche + cross-selling entre academies
> Decisions validees : isolation forte, 4 modeles de facturation, 3 canaux cross-selling

---

## 1. VISION PRODUIT

Mission Formations n'est pas juste un organisme de formation.
C'est une **plateforme SaaS de formation professionnelle** revendable en marque blanche.

```
MISSION FORMATIONS (editeur)
        │
        ├── Utilise la plateforme pour ses propres formations
        │   (Academie VTC, IA, Management, RH, etc.)
        │
        └── Revend la plateforme a d'autres organismes de formation
            │
            ├── Organisme A (marque blanche)
            │   formation.organisme-a.com
            │   Ses formations, ses formateurs, sa marque
            │   Aucune mention "Mission Formations"
            │
            ├── Organisme B (marque blanche + formations MF)
            │   formation.organisme-b.com
            │   Ses formations + formations MF revendues
            │
            └── Organisme C (marque blanche)
                academie.organisme-c.fr
                Uniquement les formations MF sous sa marque
```

### Les 2 offres

| Offre | Description | Client type |
|-------|------------|-------------|
| **Offre Plateforme** | Le client utilise la plateforme sous sa marque avec ses propres formations | Organisme de formation existant qui veut digitaliser |
| **Offre Formations** | Le client revend les formations Mission Formations sous sa marque | Organisme sans contenu qui veut un catalogue pret |

Les deux sont combinables : un client peut prendre la plateforme ET ajouter des formations MF a son catalogue.

---

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Multi-tenant avec isolation forte

```
                    INFRASTRUCTURE MISSION FORMATIONS
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │   VPS OVH 32 Go (→ 64 Go quand scaling)                 │
    │                                                          │
    │   ┌─────────────┐                                        │
    │   │  OpenEdX    │  UNE SEULE INSTANCE                    │
    │   │   LMS       │  Tous les tenants partagent :          │
    │   │   + CMS     │  - le meme code                       │
    │   │   + MySQL   │  - la meme base de donnees            │
    │   │   + Mongo   │  - le meme Studio                     │
    │   │   + Redis   │  Chaque tenant a :                    │
    │   │   + Caddy   │  - son domaine propre                 │
    │   │             │  - son branding (logo, couleurs, nom) │
    │   │             │  - ses formations filtrees             │
    │   │             │  - ses utilisateurs isoles             │
    │   └─────────────┘                                        │
    │                                                          │
    │   Domaines routes par Caddy :                            │
    │   academie.missionformations.com → LMS (tenant MF)       │
    │   formation.organisme-a.com      → LMS (tenant A)        │
    │   formation.organisme-b.com      → LMS (tenant B)        │
    │   academie.organisme-c.fr        → LMS (tenant C)        │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

### 2.2 Isolation par tenant

| Element | Partage | Isole par tenant |
|---------|---------|-----------------|
| Code OpenEdX | ✅ Un seul | — |
| Base MySQL | ✅ Une seule | — |
| Serveur | ✅ Un seul | — |
| **Domaine** | — | ✅ `formation.client.com` (CNAME vers MF) |
| **Branding** | — | ✅ Logo, couleurs, nom, favicon, emails |
| **Formations visibles** | — | ✅ Filtre par org (eox-tenant) |
| **Utilisateurs** | — | ✅ Un user ne voit que son tenant |
| **Certificats** | — | ✅ Design et logo du tenant |
| **Emails** | — | ✅ Expediteur et template du tenant |
| **Dashboard** | — | ✅ KPIs du tenant uniquement |
| **Mentions legales** | — | ✅ CGV, politique confidentialite du tenant |
| **Chat support** | — | ✅ Inbox separee par tenant (ou partagee) |
| **Facturation** | — | ✅ Le tenant ne voit que ses factures |

### 2.3 Zero mention Mission Formations

Pour l'isolation forte, le tenant marque blanche ne doit voir **aucune trace** de Mission Formations :

| Element | Ce qu'il faut masquer |
|---------|---------------------|
| Logo header | → Logo du client |
| Logo footer | → Logo du client |
| Nom plateforme | → "Academie [Client]" au lieu de "Mission Formations" |
| Footer "Propulse par..." | → Rien, ou "Propulse par [marque du client]" |
| Emails (from) | → `formation@client.com` au lieu de `@missionformations.com` |
| URL | → `formation.client.com` (domaine du client) |
| Certificats | → Logo + nom du client |
| Mentions legales | → Celles du client |
| Chat widget | → Branding client (ou masque) |
| Favicon | → Favicon du client |
| Meta title | → "[Client] — Formation professionnelle" |
| Page 404/500 | → Design du client |

**Tout cela est configurable via eox-tenant sans modifier le code.**

---

## 3. CROSS-SELLING ENTRE ACADEMIES

### 3.1 Le probleme

Un apprenant inscrit a l'Academie VTC ne sait pas que Mission Formations propose aussi des formations en IA ou Management. Chaque academie est un silo.

### 3.2 La solution : 3 canaux de decouverte

#### Canal A — Bandeau "Decouvrez aussi" dans le dashboard

```
┌─────────────────────────────────────────────────┐
│  Dashboard Apprenant — Academie VTC             │
│                                                 │
│  Mes formations :                               │
│  [■ Certificat VTC — 73% complete]              │
│  [■ Anglais VTC — 42% complete]                 │
│                                                 │
│  ─────────────────────────────────────────────   │
│  Decouvrez aussi les formations Mission :       │
│  [IA en entreprise] [Management] [Excel]        │
│  → Voir tout le catalogue                       │
│  ─────────────────────────────────────────────   │
└─────────────────────────────────────────────────┘
```

**Implementation** :
- Section optionnelle dans le dashboard apprenant (template Mako)
- Configurable par tenant : active/desactive
- Ne s'affiche PAS sur les tenants marque blanche (sauf si le client le veut)
- S'affiche sur les academies internes MF

#### Canal B — Email de recommandation post-formation

```
De: formation@missionformations.com
A: jean.dupont@email.com
Objet: Bravo Jean ! Et si vous alliez plus loin ?

Bonjour Jean,

Felicitations pour votre certificat VTC !

Vous pourriez aussi etre interesse par :
- Maitriser l'IA en entreprise (Academie IA)
- Leadership et Management (Academie Management)
- Excel et Outils numeriques (Academie Digital)

[Decouvrir le catalogue complet]
```

**Implementation** :
- Email envoye a J+7 apres l'obtention du certificat
- Template configurable par tenant
- Desactivable pour les tenants marque blanche
- Les formations recommandees sont basees sur :
  - Le domaine de la formation terminee
  - Les formations les plus populaires
  - Les formations complementaires (mapping manuel)

#### Canal C — Catalogue global

```
catalogue.missionformations.com (ou /catalogue/ sur le portail)

┌─────────────────────────────────────────────────┐
│  Toutes les formations Mission Formations       │
│                                                 │
│  Filtrer par academie :                         │
│  [Toutes] [VTC] [IA] [Management] [Digital]     │
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ VTC     │  │ IA      │  │ Mgmt    │         │
│  │ Certif  │  │ Entrep  │  │ Leader  │         │
│  │ 35h     │  │ 21h     │  │ 14h     │         │
│  │ 1500€   │  │ 990€    │  │ 790€    │         │
│  │[S'inscrire]│[S'inscrire]│[S'inscrire]│       │
│  └─────────┘  └─────────┘  └─────────┘         │
│                                                 │
│  Clic "S'inscrire" → redirige vers l'academie   │
│  correspondante (vtc.academie.mf.com)           │
└─────────────────────────────────────────────────┘
```

**Implementation** :
- Page sur le site vitrine ou le portail academie.mf.com
- Liste toutes les formations de toutes les academies
- Filtre par academie / domaine / prix / duree
- Clic → redirige vers le sous-domaine de l'academie

**Pour les tenants marque blanche** :
- Le catalogue du tenant ne montre QUE ses formations
- MAIS peut inclure les formations MF revendues (si le client a choisi l'Offre Formations)

### 3.3 Mapping des formations complementaires

| Formation terminee | Recommandations |
|-------------------|-----------------|
| Certificat VTC | Anglais VTC, Securite, Management |
| IA en entreprise | Workflows IA, Excel, Management |
| Leadership | Gestion RH, Negociation commerciale |
| Excel | IA en entreprise, Comptabilite |
| Comptabilite | Excel, Gestion financiere |
| Droit du travail | Gestion RH |

Ce mapping est configurable dans l'admin (pas en dur dans le code).

---

## 4. MODELES DE FACTURATION

### 4.1 Les 4 modeles

| Modele | Comment | Pour qui | Exemple |
|--------|---------|----------|---------|
| **Abonnement** | X€/mois pour l'acces a la plateforme | Client qui veut juste la techno | 299€/mois (jusqu'a 100 apprenants) |
| **Par apprenant** | X€ par apprenant inscrit | Client avec volume variable | 15€/apprenant/mois |
| **Par formation** | X€ par formation hebergee | Client qui ajoute beaucoup de contenu | 50€/formation/mois |
| **Revenue share** | X% sur chaque vente de formation | Client qui revend les formations MF | 30% pour MF, 70% pour le client |

### 4.2 Grille tarifaire recommandee

| Pack | Abonnement | Apprenants inclus | Formations incluses | Surplus apprenant | Surplus formation |
|------|-----------|-------------------|--------------------|-----------------|--------------------|
| **Starter** | 199€/mois | 50 | 10 | 5€/apprenant | 20€/formation |
| **Business** | 499€/mois | 200 | 30 | 3€/apprenant | 15€/formation |
| **Enterprise** | 999€/mois | 500 | Illimite | 2€/apprenant | — |
| **Custom** | Sur devis | Sur devis | Sur devis | Sur devis | Sur devis |

### 4.3 Revenue share (formations MF revendues)

| Qui vend | Qui a cree le contenu | Partage |
|---------|----------------------|---------|
| Client revend une formation MF | Mission Formations | 30% MF / 70% client |
| Client vend sa propre formation | Client | 0% MF (inclus dans l'abonnement) |
| MF vend via le catalogue global | Mission Formations | 100% MF |

### 4.4 Implementation dans Odoo

```
Odoo :
├── Produit "Pack Starter" (abonnement mensuel)
│   └── Facturation recurrente (module Abonnements)
├── Produit "Surplus apprenant" (facturation a l'usage)
│   └── Comptage automatique via API OpenEdX
├── Produit "Formation MF revendue" (revenue share)
│   └── Facturation mensuelle basee sur les ventes du client
└── Dashboard client (portail Odoo)
    └── Le client voit ses factures, son usage, ses stats
```

---

## 5. ONBOARDING D'UN CLIENT MARQUE BLANCHE

### 5.1 Processus

```
ETAPE 1 — Commercial (J0)
  │  Le client signe le contrat (Pack Starter/Business/Enterprise)
  │  Convention signee electroniquement (Odoo Signature)
  ▼
ETAPE 2 — Setup technique (J+1 a J+3)
  │  1. Creer le tenant dans eox-tenant
  │  2. Configurer le domaine client (CNAME)
  │  3. Configurer le branding (logo, couleurs, favicon)
  │  4. Configurer les emails (expediteur @client.com)
  │  5. Creer le compte admin du client
  │  6. Creer la categorie Odoo pour le client
  ▼
ETAPE 3 — Contenu (J+3 a J+7)
  │  Option A : le client cree ses propres formations dans Studio
  │  Option B : MF importe des formations du catalogue MF
  │  Option C : mix des deux
  ▼
ETAPE 4 — Test et validation (J+7 a J+10)
  │  Le client teste son espace
  │  Verification branding, formations, certificats
  ▼
ETAPE 5 — Go live (J+10)
  │  Le client communique son URL a ses apprenants
  │  Le support demarre
  ▼
ETAPE 6 — Suivi mensuel
  │  Reporting usage (apprenants, formations, CA)
  │  Facturation automatique (Odoo)
  │  Support technique
```

### 5.2 Ce que le client recoit

| Element | Detail |
|---------|--------|
| **URL** | `formation.client.com` (son domaine, CNAME vers MF) |
| **Admin Studio** | Compte admin pour creer/editer ses formations |
| **Dashboard admin** | KPIs de SON tenant uniquement |
| **Support** | Chat WeWill (inbox dediee ou partagee) |
| **Documentation** | Guide admin, guide formateur, guide apprenant |
| **Certificats** | Brandes avec le logo du client |
| **Emails** | Expediteur @client.com |
| **Qualiopi** | Scorecard du tenant (si le client est certifie Qualiopi) |

### 5.3 Ce que le client NE recoit PAS

| Element | Pourquoi |
|---------|----------|
| Acces au code source | C'est du SaaS, pas de l'open source |
| Acces a la base de donnees | Multi-tenant = donnees partagees |
| Acces aux autres tenants | Isolation forte |
| Acces au serveur | Tout passe par l'interface web |

---

## 6. ARCHITECTURE DONNEES MULTI-TENANT

### 6.1 Comment eox-tenant isole les donnees

```python
# eox-tenant injecte un filtre automatique sur les requetes

# Quand un user se connecte sur formation.client-a.com :
# 1. eox-tenant detecte le domaine → charge la config du tenant A
# 2. Filtre les cours : CourseOverview.objects.filter(org__in=['CLIENT-A-ORG'])
# 3. Filtre les enrollments : seulement ceux du tenant A
# 4. Injecte le branding : logo, couleurs, nom du tenant A

# Le code OpenEdX est le meme — seul le contexte change
```

### 6.2 Schema des organisations

| Tenant | Org OpenEdX | Formations | Domaine |
|--------|------------|------------|---------|
| **Mission Formations** | MF-VTC, MF-IA, MF-MGMT, etc. | Toutes les formations MF | academie.mf.com |
| **Academie VTC** (interne) | MF-VTC | Formations VTC uniquement | vtc.academie.mf.com |
| **Client A** (marque blanche) | CLIENT-A | Formations du client A | formation.client-a.com |
| **Client B** (marque blanche + MF) | CLIENT-B, MF-IA | Formations client B + formations MF IA | formation.client-b.com |

### 6.3 Formations MF revendues

Quand un client marque blanche revend des formations MF :

```
Formation "IA en entreprise" (org = MF-IA)
     │
     │ Rattachee au tenant du client via AcademyCourse
     ▼
AcademyCourse(academy=client_b, course_id="MF-IA+IA001", is_featured=True)
     │
     │ eox-tenant config du client B :
     │ course_org_filter: ['CLIENT-B', 'MF-IA']  ← inclut l'org MF-IA
     ▼
Le client B voit la formation IA dans son catalogue
Le certificat porte le logo du client B (override par tenant)
```

---

## 7. IMPACT SUR LE BUSINESS MODEL

### 7.1 Sources de revenus

```
MISSION FORMATIONS — Sources de revenus
│
├── 1. Vente de formations (B2C et B2B)
│      Apprenants individuels + entreprises
│      → Odoo e-commerce + OPCO
│
├── 2. Abonnements plateforme (SaaS marque blanche)
│      Organismes de formation clients
│      → Odoo Abonnements (recurrent)
│
├── 3. Surplus a l'usage (apprenants / formations)
│      Facturation mensuelle du depassement
│      → Odoo facturation automatique
│
├── 4. Revenue share (formations MF revendues)
│      30% sur chaque vente via un client marque blanche
│      → Odoo commission automatique
│
└── 5. Services (setup, personnalisation, support premium)
       Accompagnement a la mise en place
       → Facturation ponctuelle
```

### 7.2 Projection revenus marque blanche

| Annee | Clients MB | Revenu abonnement | Revenu usage | Revenu share | Total MB |
|-------|-----------|-------------------|-------------|-------------|---------|
| 2026 | 2-3 | 6-18k€ | 2-5k€ | 1-3k€ | ~10-25k€ |
| 2027 | 5-10 | 30-120k€ | 10-30k€ | 5-15k€ | ~45-165k€ |
| 2028 | 10-20 | 60-240k€ | 20-60k€ | 10-30k€ | ~90-330k€ |

---

## 8. PREREQUIS TECHNIQUES

### 8.1 Ce qu'il faut AVANT de proposer la marque blanche

| Prerequis | Statut | Effort |
|-----------|--------|--------|
| eox-tenant configure et teste | A faire | 3h |
| DNS wildcard | A faire | 15 min |
| Caddy wildcard SSL | A faire | 2h |
| S3 Object Storage | A faire | 2h |
| Upgrade VPS 32 Go (minimum) | A faire | 1h |
| Process de creation de tenant automatise | A faire | 4h |
| Branding dynamique (logo, couleurs, emails) | A faire | 3h |
| Certificats par tenant | Partiellement fait (20 templates par org) | 2h |
| Dashboard admin filtrable par tenant | A faire | 3h |
| Odoo : module abonnement + facturation recurrente | A faire | 4h |
| Documentation client (guide admin, formateur, apprenant) | Partiellement fait | 4h |
| Contrat SaaS / CGU marque blanche | A faire | Legal |

### 8.2 Ce qu'il faut AVANT de vendre le premier pack

| Element | Obligatoire | Effort |
|---------|------------|--------|
| 1 tenant de demo fonctionnel | Oui | 2h |
| Plaquette commerciale "Offre plateforme" | Oui | 3h |
| Grille tarifaire validee | Oui | 1h |
| Contrat type SaaS | Oui | Legal (avocat) |
| SLA documente | Oui | 1h (deja fait) |
| Process onboarding client (section 5) | Oui | 2h |
| Au moins 5 formations MF pretes a revendre | Oui | Sprint contenu |

---

## 9. PLAN D'IMPLEMENTATION

### Phase 1 — Fondations multi-tenant (Sprint 1)

| Tache | Effort |
|-------|--------|
| DNS wildcard *.academie.staging.mf.com | 15 min |
| Caddy wildcard SSL | 2h |
| Configurer eox-tenant | 3h |
| Premier tenant test : vtc.academie.staging.mf.com | 1h |
| Valider : isolation, branding, filtrage cours | 2h |

### Phase 2 — Academies internes MF (Sprint 2)

| Tache | Effort |
|-------|--------|
| Creer les 7 academies internes | 2h |
| Automatiser la creation dans Academy Manager | 4h |
| Dashboard admin filtrable par academie | 3h |
| Cross-selling Canal A (bandeau "Decouvrez aussi") | 3h |
| Cross-selling Canal C (catalogue global) | 4h |

### Phase 3 — Marque blanche (Sprint 3-4)

| Tache | Effort |
|-------|--------|
| Support du domaine custom (CNAME client) | 2h |
| Branding complet par tenant (zero mention MF) | 4h |
| Emails par tenant (expediteur custom) | 3h |
| Certificats par tenant | 2h |
| Tenant de demo pour les prospects | 2h |

### Phase 4 — Facturation (Sprint 4-5)

| Tache | Effort |
|-------|--------|
| Odoo : module abonnement recurrent | 4h |
| Comptage automatique apprenants par tenant | 3h |
| Facturation surplus a l'usage | 3h |
| Revenue share (commissions) | 3h |
| Portail client Odoo (factures, usage, stats) | 4h |

### Phase 5 — Cross-selling + scaling (Sprint 5-6)

| Tache | Effort |
|-------|--------|
| Cross-selling Canal B (email recommandation J+7) | 3h |
| Mapping formations complementaires (admin) | 2h |
| Onboarding automatise client MB | 4h |
| Documentation client complete | 4h |

**Effort total : ~70-80h supplementaires**

---

## 10. RESUME DES DECISIONS

| Decision | Choix valide |
|----------|-------------|
| Architecture | Multi-tenant une seule instance + eox-tenant |
| Isolation | **Forte** — domaine propre, zero mention MF |
| Offre | Plateforme + formations pretes (les 2) |
| Cross-selling | 3 canaux (bandeau + email + catalogue global) |
| Facturation | 4 modeles (abonnement + apprenant + formation + revenue share) |
| Priorite | Academies internes MF d'abord → marque blanche ensuite |
