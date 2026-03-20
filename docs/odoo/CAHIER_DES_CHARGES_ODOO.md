# Cahier des charges — Integration Odoo × Mission Formations

> Version 1.0 — 19 mars 2026
> Objectif : definir les besoins, l'architecture d'integration, et les flux entre Odoo et l'ecosysteme MF

---

## PARTIE 1 — POURQUOI ODOO ?

### Ce que le LMS OpenEdX ne sait PAS faire

| Besoin | OpenEdX | Odoo |
|--------|---------|------|
| Facturation / devis | Non | Oui (module Facturation) |
| Gestion des contrats B2B | Non (champ texte dans Academy) | Oui (module Ventes + Abonnements) |
| Suivi des paiements | Non | Oui (module Comptabilite) |
| CRM / pipeline commercial | Non | Oui (module CRM) |
| Gestion des OPCO / financeurs | Non | Oui (contacts + tags + workflow) |
| Catalogue produit (formations = produits) | Partiel (discovery) | Oui (module Produits) |
| Relance impaye | Non | Oui (module Comptabilite) |
| Signature electronique | Non | Oui (module Signature) |
| E-commerce (vente en ligne) | Non natif | Oui (module E-commerce) |

### Ce que le module Qualiopi a besoin d'Odoo

| Indicateur Qualiopi | Donnee necessaire | Source Odoo |
|---------------------|-------------------|-------------|
| Ind. 7, 8 | Convention signee + montant | Module Ventes (devis → commande) |
| Ind. 29 | Bilan financier formation | Module Comptabilite (factures par formation) |
| DOC-02 | Convention de formation B2B | Module Ventes (genere depuis le devis) |
| DOC-03 | Contrat individuel | Module Ventes |
| DOC-14 | Bilan financier dans le ZIP auditeur | Module Comptabilite |
| Dashboard admin | Chiffre d'affaires, revenus, frais formateurs | Module Comptabilite |

---

## PARTIE 2 — BESOINS FONCTIONNELS

### Flux 1 : Pipeline commercial (CRM)

```
Prospect → Lead → Opportunite → Devis → Commande → Facture → Paiement
    ↑                                        ↓
  Sources :                           Declencheurs :
  - Formulaire /contact/              - Webhook → OpenEdX (enrollment)
  - Chat (Crisp/Chatwoot)             - Webhook → Qualiopi (convention)
  - Appel telephonique                - Email convocation (DOC-04)
  - Demande OPCO
  - Site missionformations.com
```

| # | Etape | Module Odoo | Webhook vers | Description |
|---|-------|-------------|-------------|-------------|
| OD-01 | Nouveau lead | CRM | — | Lead cree depuis formulaire contact, chat, ou manuellement |
| OD-02 | Qualification | CRM | — | Identifier : individuel, entreprise, OPCO, Mission Locale, CSE |
| OD-03 | Devis | Ventes | — | Generer un devis avec la/les formation(s), tarif, conditions |
| OD-04 | Signature | Signature | — | Signature electronique du devis/convention par le client |
| OD-05 | Commande confirmee | Ventes | **→ OpenEdX** | Webhook : creer l'enrollment + l'academie B2B si necessaire |
| OD-06 | Facture | Comptabilite | — | Facture generee automatiquement a la confirmation |
| OD-07 | Paiement recu | Comptabilite | **→ OpenEdX** | Webhook : activer l'acces a la formation |
| OD-08 | Relance impaye | Comptabilite | — | Emails automatiques de relance |

### Flux 2 : Paiement individuel (CPF / particulier)

```
Apprenant → Page formation → Paiement en ligne → Acces formation
                                    ↓
                          Odoo E-commerce ou
                          Stripe + sync Odoo
```

| # | Etape | Detail |
|---|-------|--------|
| OD-09 | Page produit | La formation sur le site = un produit Odoo (ou lien vers Odoo e-commerce) |
| OD-10 | Paiement CB | Via Stripe (integre a Odoo) ou Odoo Payment |
| OD-11 | Confirmation paiement | Webhook → OpenEdX (enrollment) + Qualiopi (convocation DOC-04) |
| OD-12 | Facture auto | Generee automatiquement dans Odoo |

### Flux 3 : Paiement OPCO / financeur

```
Entreprise → Demande de prise en charge → OPCO valide → Convention → Formation
```

| # | Etape | Detail |
|---|-------|--------|
| OD-13 | Dossier OPCO | Contact OPCO dans Odoo (type "financeur") |
| OD-14 | Numero de prise en charge | Champ custom sur la commande Odoo |
| OD-15 | Convention tripartite | Convention entre MF + entreprise + OPCO (DOC-02 enrichi) |
| OD-16 | Facturation OPCO | Facture adressee a l'OPCO (pas a l'entreprise) |
| OD-17 | Suivi encaissement | Rapprochement paiement OPCO dans Odoo |

### Flux 4 : Gestion B2B (entreprises / academies)

| # | Etape | Detail |
|---|-------|--------|
| OD-18 | Fiche entreprise | Contact Odoo (type entreprise) avec SIRET, RH contact, nb salaries |
| OD-19 | Contrat/abonnement | Module Abonnements : nb places, formations incluses, duree |
| OD-20 | Webhook → OpenEdX | A la signature : creer l'Academy dans OpenEdX + AcademyCourse |
| OD-21 | Ajout stagiaires | L'entreprise communique la liste → enrollment OpenEdX |
| OD-22 | Reporting B2B | Dashboard RH : qui a commence, progression, certificats (depuis OpenEdX → Odoo) |
| OD-23 | Renouvellement | Alerte avant fin de contrat, devis de renouvellement auto |

### Flux 5 : Formateurs et frais

| # | Etape | Detail |
|---|-------|--------|
| OD-24 | Fiche formateur | Contact Odoo (type fournisseur) avec tarif horaire, statut |
| OD-25 | Bon de commande formateur | Pour les intervenants externes (Ind. 21 Qualiopi) |
| OD-26 | Note de frais | Module Notes de frais : deplacements, materiel |
| OD-27 | Facturation formateur | Le formateur independant facture MF via Odoo |
| OD-28 | Reporting frais | Dashboard admin : frais par formation, par formateur, marge |

### Flux 6 : Comptabilite et reporting

| # | Etape | Detail |
|---|-------|--------|
| OD-29 | CA par formation | Ventilation du chiffre d'affaires par formation/academie |
| OD-30 | CA par financeur | OPCO vs individuel vs entreprise vs CPF |
| OD-31 | Marge par formation | CA - frais formateur - frais plateforme |
| OD-32 | Export comptable | Export FEC (Fichier des Ecritures Comptables) pour l'expert comptable |
| OD-33 | TVA | Gestion TVA (exoneration formations si organisme agree) |
| OD-34 | Bilan pedagogique et financier | Alimente DOC-14 (bilan formation) et Ind. 29 Qualiopi |

---

## PARTIE 3 — ARCHITECTURE D'INTEGRATION

### Schema global

```
┌─────────────────────────────────────────────────────────────────┐
│                     ECOSYSTEME MISSION FORMATIONS               │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ OpenEdX  │    │ Qualiopi │    │   Odoo   │    │  Crisp   │  │
│  │  (LMS)   │    │  (App)   │    │  (ERP)   │    │  (Chat)  │  │
│  │          │    │          │    │          │    │          │  │
│  │ Cours    │    │ 32 ind.  │    │ CRM      │    │ Widget   │  │
│  │ Grades   │◄──►│ PDFs     │◄──►│ Ventes   │◄───│ Leads    │  │
│  │ Tracking │    │ Registres│    │ Compta   │    │ Support  │  │
│  │ Certifs  │    │ Alertes  │    │ Factures │    │          │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │        │
│       └───────────────┴───────┬───────┴───────────────┘        │
│                               │                                 │
│                        Webhooks / API                           │
│                     (JSON, REST, OAuth2)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Webhooks : qui envoie quoi a qui ?

| Evenement | Source | Destination | Payload | Action |
|-----------|--------|-------------|---------|--------|
| Nouveau lead chat | **Crisp** | **Odoo** | email, nom, message | Creer lead CRM |
| Formulaire contact | **OpenEdX** | **Odoo** | email, nom, profil, sujet | Creer lead CRM |
| Commande confirmee | **Odoo** | **OpenEdX** | user_email, course_id, academy_id | Creer enrollment + academy |
| Paiement recu | **Odoo** | **OpenEdX** | user_email, course_id | Activer acces formation |
| Paiement recu | **Odoo** | **Qualiopi** | user_email, course_id, formation | Generer convocation (DOC-04) |
| Certificat obtenu | **OpenEdX** | **Odoo** | user_email, course_id, grade | MAJ fiche contact (formation terminee) |
| Certificat obtenu | **OpenEdX** | **Qualiopi** | user_email, course_id | Generer attestation (DOC-07) |
| Convention signee | **Odoo** | **Qualiopi** | convention_id, entreprise, formation | Enregistrer dans registre Qualiopi |
| Reclamation chat | **Crisp** | **Qualiopi** | conversation_id, contact, sujet | Creer reclamation (Ind. 32) |
| Facture emise | **Odoo** | **Qualiopi** | facture_id, formation, montant | Alimenter le bilan financier (DOC-14) |
| Abandon detecte | **Qualiopi** | **Odoo** | user_email, course_id, cause | MAJ fiche contact (risque perte) |

### API Odoo (endpoints cles)

```
# Odoo XML-RPC ou REST API (module custom ou Odoo.sh API)

# CRM
POST /api/crm/lead          → creer un lead
GET  /api/crm/lead/{id}     → consulter un lead

# Ventes
POST /api/sale/order         → creer un devis
GET  /api/sale/order/{id}    → consulter une commande
POST /api/sale/order/{id}/confirm → confirmer (declenche webhook)

# Comptabilite
GET  /api/account/invoice    → lister les factures
GET  /api/account/invoice/{id}/pdf → telecharger la facture PDF

# Contacts
GET  /api/res/partner        → lister les contacts (clients, formateurs, OPCO)
POST /api/res/partner        → creer un contact

# Produits (formations)
GET  /api/product/template   → lister les formations/produits
```

---

## PARTIE 4 — OPTIONS D'HEBERGEMENT ODOO

### Option 1 : Odoo.sh (SaaS officiel)

| Critere | Detail |
|---------|--------|
| **Prix** | 7.25€/user/mois (One App) ou 24.90€/user/mois (Standard) ou 37.40€/user/mois (Custom) |
| **Maintenance** | Zero (Odoo gere tout) |
| **Mises a jour** | Automatiques |
| **API** | XML-RPC + JSON-RPC natifs |
| **Modules** | Tous les modules officiels disponibles |
| **Personnalisation** | Limitee (pas d'acces serveur sur One App/Standard) |
| **RGPD** | Hebergement EU disponible |
| **Backup** | Automatique |
| **Verdict** | **Recommande** pour un dev solo |

### Option 2 : Odoo self-hosted (autre VPS)

| Critere | Detail |
|---------|--------|
| **Prix** | VPS 4-8 Go (10-20€/mois) + Odoo Community (gratuit) ou Enterprise (licence) |
| **Maintenance** | Moyenne (mises a jour, backup PostgreSQL, securite) |
| **Modules** | Community = limite (pas de Signature, pas d'Abonnements, pas de Studio) |
| **API** | XML-RPC natif |
| **Personnalisation** | Totale |
| **Verdict** | Economique mais plus de travail |

### Option 3 : Odoo self-hosted sur le meme VPS qu'OpenEdX

| Critere | Detail |
|---------|--------|
| **Verdict** | **ABSOLUMENT PAS** — Odoo = Python + PostgreSQL + workers = 2-4 Go RAM minimum |

### Matrice de decision

| Critere | Poids | Odoo.sh | Self-hosted VPS | Meme VPS |
|---------|-------|---------|-----------------|----------|
| Maintenance dev solo | 5 | 5 | 2 | 1 |
| Cout | 3 | 3 | 4 | 4 |
| Modules disponibles | 4 | 5 | 3 | 3 |
| API / webhooks | 4 | 5 | 5 | 5 |
| RAM VPS OpenEdX preservee | 5 | 5 | 5 | 1 |
| Fiabilite | 4 | 5 | 3 | 1 |
| **Score** | | **120/125** | **90/125** | **55/125** |

**Recommandation : Odoo.sh** (plan Standard a 24.90€/user/mois pour 2-3 users admin)

---

## PARTIE 5 — MODULES ODOO NECESSAIRES

### Modules essentiels (jour 1)

| Module | Usage | Plan Odoo.sh |
|--------|-------|-------------|
| **CRM** | Pipeline commercial, leads, opportunites | Standard |
| **Ventes** | Devis, commandes, conventions de formation | Standard |
| **Facturation** | Factures, avoirs, relances | Standard |
| **Contacts** | Clients, entreprises, OPCO, formateurs | Standard |
| **Signature** | Signature electronique des conventions | Standard |

### Modules phase 2

| Module | Usage | Plan Odoo.sh |
|--------|-------|-------------|
| **E-commerce** | Vente en ligne des formations (CPF, individuel) | Standard |
| **Abonnements** | Contrats B2B recurrents (academies entreprise) | Standard |
| **Notes de frais** | Frais formateurs | Standard |
| **Comptabilite** | Grand livre, FEC, bilan | Standard |
| **Email Marketing** | Campagnes, newsletters, relance prospects | Standard |

### Modules optionnels

| Module | Usage |
|--------|-------|
| **Helpdesk** | Si tu ne prends pas Crisp (mais doublon) |
| **Documents** | GED centralisee (conventions, factures) |
| **Planification** | Planning formateurs / salles |
| **Projet** | Suivi des projets B2B |

---

## PARTIE 6 — CONFIGURATION ODOO POUR MISSION FORMATIONS

### Produits = Formations

Chaque formation OpenEdX = un produit Odoo :

| Champ Odoo | Valeur | Correspondance OpenEdX |
|------------|--------|------------------------|
| Nom du produit | "Certificat VTC" | display_name du cours |
| Reference interne | "MF-VTC-001" | course_id |
| Categorie | "Formations VTC" | org (MF-VTC) |
| Prix de vente | 1500€ HT | — |
| Type | Service | — |
| Description | Objectifs, duree, modalites | short_description |
| Champ custom : course_id | "course-v1:MF-VTC+VTC001+2025" | Pour le webhook enrollment |
| Champ custom : duree_heures | 35 | — |
| Champ custom : modalite | "distanciel" | — |

### Contacts

| Type de contact | Champs specifiques |
|-----------------|-------------------|
| **Apprenant individuel** | email (= email OpenEdX), formation, OPCO si applicable, statut CPF |
| **Entreprise B2B** | SIRET, contact RH, nb salaries, academy_id OpenEdX |
| **OPCO** | Nom OPCO, code, contact, adresse de facturation |
| **Mission Locale** | Idem OPCO |
| **CSE** | Idem entreprise |
| **Formateur** | Tarif horaire, statut (salarie/independant), RC Pro, specialites |

### Pipeline CRM

| Etape | Actions |
|-------|---------|
| **Nouveau lead** | Auto (formulaire contact, chat Crisp, demande site) |
| **Qualifie** | Identifier le type (individuel/entreprise/OPCO) + la formation |
| **Devis envoye** | Generer le devis + convention (DOC-02 ou DOC-03) |
| **Negocie** | Echanges, ajustements, validation OPCO |
| **Gagne** | Commande confirmee → webhook OpenEdX (enrollment) |
| **Perdu** | Raison documentee (prix, delai, concurrent, etc.) |

---

## PARTIE 7 — DONNEES ECHANGEES AVEC LE DASHBOARD ADMIN OPENEDX

Le dashboard admin OpenEdX affiche actuellement des onglets avec des donnees hardcodees.
Odoo va alimenter ces onglets :

| Onglet dashboard | Etat actuel | Source Odoo |
|-----------------|-------------|-------------|
| **Overview — CA hero** | Hardcode | `GET /api/account/invoice?state=posted` → somme des montants |
| **Overview — Graphique revenus** | Hardcode | Factures par mois |
| **Revenus** | Tout hardcode | Factures + paiements |
| **Frais formateurs** | Tout hardcode | Notes de frais + factures fournisseurs |
| **Factures** | Tout hardcode | Liste des factures (numero, client, montant, statut) |
| **Parametres** | Tout hardcode | Config Odoo (tarifs, conditions, etc.) |

### Comment le dashboard OpenEdX recupere les donnees Odoo

**Option A : API directe (LMS → Odoo)**
- Le dashboard admin dans le LMS appelle l'API Odoo en temps reel
- Probleme : ajoute de la latence + charge sur le LMS

**Option B : Via l'app Qualiopi (recommande)**
- L'app Qualiopi (separee) se connecte a Odoo ET a OpenEdX
- Elle agrege les donnees et les expose via sa propre API
- Le dashboard LMS affiche un iframe ou appelle l'API Qualiopi
- Avantage : un seul point d'integration, pas de charge sur le LMS

```
OpenEdX (LMS)                    App Qualiopi              Odoo
    │                                │                       │
    │  iframe /qualiopi/dashboard    │                       │
    │──────────────────────────────►│                       │
    │                                │  API : factures       │
    │                                │──────────────────────►│
    │                                │◄──────────────────────│
    │                                │  API : grades         │
    │◄───────────────────────────────│  (MySQL read-only)    │
    │       HTML rendu               │                       │
    │◄──────────────────────────────│                       │
```

---

## PARTIE 8 — DOCUMENTS ODOO BRANDES MISSION FORMATIONS

Odoo genere ses propres PDFs. Il faut les personnaliser avec le design MF.

| Document Odoo | Personnalisation necessaire |
|---------------|----------------------------|
| **Devis** | Header MF (logo, couleurs), footer (SIRET, N° DA, Qualiopi), mentions legales formation pro |
| **Facture** | Idem + mention exoneration TVA si applicable + N° prise en charge OPCO |
| **Bon de commande** | Idem |
| **Convention de formation** | Template specifique (DOC-02 du cahier Qualiopi) — peut etre genere par Odoo OU par l'app Qualiopi |
| **Contrat individuel** | Template specifique (DOC-03) |
| **Avoir** | Header/footer MF |
| **Relance impaye** | Ton professionnel, mentions legales |

### Branding Odoo

Dans Odoo, la personnalisation des documents passe par :
1. **Report Designer** (module Studio, plan Custom) ou
2. **QWeb templates** (XML, modifiable dans le code)

Elements a personnaliser :
- Logo Mission Formations
- Couleurs (bleu MF, vert MF)
- Police (Montserrat / Open Sans)
- Footer : "Mission Formations — Organisme de formation certifie Qualiopi — SIRET XXX — N° DA XXX — Adresse"
- Mentions legales specifiques formation professionnelle :
  - "Exonere de TVA au titre de la formation professionnelle continue (art. 261-4-4° du CGI)"
  - "Organisme certifie Qualiopi au titre de la categorie Actions de formation"
  - Numero de declaration d'activite

---

## PARTIE 9 — PLAN DE MISE EN PLACE

### Phase 0 — Configuration Odoo (1-2 jours)

| Tache | Detail |
|-------|--------|
| Creer le compte Odoo.sh | Plan Standard, 2-3 users |
| Configurer la societe | Mission Formations, SIRET, adresse, logo |
| Installer les modules | CRM, Ventes, Facturation, Contacts, Signature |
| Creer les produits | 10 formations initiales (depuis le catalogue OpenEdX) |
| Configurer le pipeline CRM | 6 etapes (lead → gagne/perdu) |
| Personnaliser les templates PDF | Logo, couleurs, footer, mentions legales |
| Creer les contacts initiaux | OPCO connus, entreprises prospects, formateurs |

### Phase 1 — Webhooks entrants (Crisp/formulaire → Odoo) (1 jour)

| Tache | Detail |
|-------|--------|
| Webhook Crisp → Odoo | Nouvelle conversation → lead CRM |
| Webhook formulaire contact → Odoo | POST /api/crm/lead |
| Test | Verifier que les leads arrivent dans le pipeline |

### Phase 2 — Webhooks sortants (Odoo → OpenEdX) (2-3 jours)

| Tache | Detail |
|-------|--------|
| Module custom Odoo | Webhook a la confirmation de commande |
| Endpoint OpenEdX | POST /api/webhook/odoo/enrollment (a creer dans mission_central_admin) |
| Logique | Creer le user si inexistant + enrollment + academy B2B si applicable |
| Securite | Signature HMAC du webhook + IP whitelist |
| Test | Confirmer une commande Odoo → verifier l'inscription dans OpenEdX |

### Phase 3 — Webhooks sortants (Odoo → Qualiopi) (1-2 jours)

| Tache | Detail |
|-------|--------|
| Webhook paiement → Qualiopi | Declencher la generation de convocation (DOC-04) |
| Webhook convention → Qualiopi | Enregistrer dans le registre conventions |
| Webhook facture → Qualiopi | Alimenter le bilan financier |

### Phase 4 — Dashboard admin connecte (2-3 jours)

| Tache | Detail |
|-------|--------|
| API Qualiopi → Odoo | Recuperer CA, factures, frais formateurs |
| Onglets dashboard | Remplacer les donnees hardcodees par les donnees Odoo |
| Cache | Cacher les donnees Odoo (refresh toutes les 15 min) |

### Phase 5 — E-commerce (phase 2, 3-5 jours)

| Tache | Detail |
|-------|--------|
| Module E-commerce Odoo | Activer la boutique en ligne |
| Pages produits | Formations vendables en ligne |
| Paiement Stripe | Integrer Stripe dans Odoo |
| Webhook paiement → OpenEdX | Enrollment automatique apres paiement CB |
| Page confirmation | Redirection vers le LMS apres achat |

---

## PARTIE 10 — BUDGET ESTIME

### Odoo.sh

| Poste | Cout mensuel |
|-------|-------------|
| Odoo.sh Standard (3 users) | 3 × 24.90€ = **74.70€/mois** |
| Domaine custom (odoo.missionformations.com) | Inclus |
| Stockage | Inclus (50 Go) |
| Backup | Inclus |
| **Total** | **~75€/mois** |

### Alternative economique : Odoo Community self-hosted

| Poste | Cout mensuel |
|-------|-------------|
| VPS 4 Go OVH | **8€/mois** |
| Odoo Community | Gratuit |
| Maintenance | Ton temps (mises a jour, backup) |
| **Total** | **~8€/mois** |
| **Modules manquants** | Signature, Abonnements, Studio, support officiel |

---

## RECAPITULATIF : ARCHITECTURE CIBLE COMPLETE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   VPS OVH 32 Go (upgrade)              Services externes (SaaS)        │
│   ┌──────────────────────┐             ┌─────────────────────┐         │
│   │     OpenEdX LMS      │             │   Odoo.sh           │         │
│   │  (formations,        │◄──webhook──►│   (CRM, ventes,     │         │
│   │   apprenants,        │             │    facturation)      │         │
│   │   grades, certifs)   │             │   ~75€/mois          │         │
│   ├──────────────────────┤             ├─────────────────────┤         │
│   │   App Qualiopi       │◄───API────►│   Crisp              │         │
│   │  (container Docker)  │             │   (chat, support)    │         │
│   │  (32 indicateurs,    │             │   0-25€/mois         │         │
│   │   PDFs, registres)   │             └─────────────────────┘         │
│   └──────────────────────┘                                             │
│                                        ┌─────────────────────┐         │
│                                        │   OVH Object Storage│         │
│                                        │   (videos, PDFs)     │         │
│                                        │   ~5-15€/mois        │         │
│                                        └─────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Budget mensuel total :
- VPS 32 Go      : ~35-50€
- Odoo.sh        : ~75€
- Crisp          : 0-25€
- Object Storage : ~5-15€
- TOTAL          : ~115-165€/mois
```
