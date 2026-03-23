# Analyse concurrentielle — Loop Formations vs Mission Formations

> Date : 23 mars 2026
> Source : https://loop-formations.fr/documentation/
> Objectif : enrichir le cahier des charges Qualiopi avec les fonctionnalites manquantes

---

## 1. CE QUE LOOP FAIT ET QUE NOUS N'AVONS PAS PREVU

### 1.1 Emargement electronique avance

Loop a 14 fonctionnalites d'emargement vs notre DOC-06 basique :

| Loop a | Nous avons | A ajouter |
|--------|-----------|-----------|
| QR code projete en salle pour signature collective | ❌ | ✅ A ajouter (presentiel/hybride) |
| Signature sur tous les appareils (mobile, tablette) | ❌ | ✅ A ajouter |
| Mode restrictif (ne peut pas signer sans etre present) | ❌ | ✅ Geolocalisation optionnelle |
| Suivi des absences automatique avec relance | ❌ partiel (detection inactivite) | ✅ Enrichir le workflow 4 |
| Templates d'emargement personnalisables | ❌ (1 seul format) | ✅ Ajouter des templates |
| Statistiques d'assiduite par formation | ✅ (prevu dans scorecard) | OK |

### 1.2 Gestion commerciale integree

Loop a un CRM complet integre. Nous on delegue a Odoo — c'est mieux, mais il manque :

| Loop a | Nous avons | A ajouter |
|--------|-----------|-----------|
| Pipeline visuel avec automatisation | ✅ (Odoo CRM) | OK |
| Devis auto-generes avec tags dynamiques | ❌ | ✅ Template Odoo avec 300+ tags |
| Suivi ouverture/clic emails | ❌ | ✅ A integrer (Odoo Email Marketing) |
| Commission formateurs avec stats individuelles | ❌ | ✅ Ajouter dans le dashboard formateur |
| Tarification multiple par formation | ❌ | ✅ Ajouter dans Odoo (prix OPCO vs individuel vs B2B) |
| Catalogues publics illimites avec iframe | ✅ (/catalogue/) | Enrichir |

### 1.3 Tags dynamiques (300+)

Loop genere les documents avec 300+ tags dynamiques (`{apprenant.nom}`, `{formation.duree}`, `{session.date_debut}`, etc.). Nous avons prevu les variables dans les PDFs mais pas un systeme de tags generique.

**A ajouter** : un systeme de tags/variables reutilisable dans TOUS les documents (PDFs, emails, conventions).

### 1.4 E-learning integre (vs notre OpenEdX)

| Loop a | Nous avons | Avantage |
|--------|-----------|----------|
| Editeur e-learning integre | OpenEdX Studio | **Nous** — Studio est bien plus puissant |
| Quiz varies (vrai/faux, association, zones cliquables) | OpenEdX XBlocks | **Nous** — plus de types de quiz |
| SCORM support | OpenEdX SCORM XBlock | **Egal** |
| Visioconference 100 participants | A configurer (BBB/Zoom) | **Loop** — integre nativement |
| Suivi temps par contenu | OpenEdX tracking | **Egal** |
| Mode progression (libre/sequentiel/mixte) | OpenEdX gating | **Egal** |

### 1.5 Workflows et automatisations

Loop a des workflows conditionnels configurables. Nos 12 workflows sont plus complets mais hardcodes.

**A ajouter** : un editeur de workflows visuel dans le dashboard admin (phase 2-3).

### 1.6 Gestion financiere

| Loop a | Nous avons | A ajouter |
|--------|-----------|-----------|
| Facturation automatique | ✅ (Odoo) | OK |
| Multi-financeurs (repartition des couts) | ❌ | ✅ Important pour les dossiers OPCO + entreprise + apprenant |
| Calcul de marge par formation | ✅ (prevu dans Odoo) | OK |
| Generation BPF automatique | ❌ | ✅ A ajouter (Bilan Pedagogique et Financier annuel) |
| Interface OPCO | ❌ | ✅ A ajouter (format d'echange OPCO) |

### 1.7 Gestion des centres de formation multiples

Loop gere plusieurs centres/sites physiques. Pertinent pour nous quand on aura du presentiel :

| Fonctionnalite | A prevoir |
|----------------|-----------|
| Gestion des salles/lieux | Modele `Lieu` avec adresse, capacite, equipements |
| Detection de conflits planning | Verifier qu'une salle n'est pas reservee 2 fois |
| Gestion multi-centre | Filtrer par centre dans le dashboard |

---

## 2. CE QUE NOUS AVONS ET QUE LOOP N'A PAS

| Notre avantage | Detail |
|----------------|--------|
| **LMS OpenEdX complet** | Studio, XBlocks, ORA peer review, forums — Loop a un e-learning basique |
| **Multi-tenant / marque blanche** | Loop n'a pas de marque blanche avec domaine custom |
| **20 templates de certificats par domaine** | Loop a des certificats generiques |
| **Architecture microservices** | LMS + Qualiopi + Odoo + Chat + GED — Loop est monolithique |
| **Open source (OpenEdX)** | Loop est proprietaire |
| **Cross-selling entre academies** | Loop n'a pas ce concept |
| **App Qualiopi avec 91 endpoints API** | Loop n'a pas d'API publique documentee comme la notre |

---

## 3. ENRICHISSEMENTS DU CAHIER DES CHARGES

### Release 1 (MVP — Sprint 1-2)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| 20 modeles Qualiopi (registres, formulaires) | CDC existant | 4h |
| 22 PDFs brandes | CDC existant | 40h |
| 7 onglets dashboard scorecard | CDC existant | 12h |
| Health check API | CDC existant | 15min |
| Django Admin pour tous les modeles | CDC existant | 2h |
| Celery + Redis | CDC existant | 1h |

### Release 2 (Automatisations — Sprint 3)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| 12 workflows Celery | CDC existant | 12h |
| 17 templates email | CDC existant | 6h |
| Signal forwarder LMS → Qualiopi | CDC existant | 4h |
| Veille RSS automatique | CDC existant | 4h |
| Alertes qualite (SLA reclamations, CV expires, etc.) | CDC existant | 4h |

### Release 3 (Emargement avance — Sprint 4)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| QR code pour emargement presentiel | Loop | 4h |
| Signature mobile/tablette | Loop | 3h |
| Mode restrictif (geolocalisation optionnelle) | Loop | 2h |
| Dashboard assiduite avec statistiques | Loop + CDC | 3h |
| Templates emargement personnalisables | Loop | 2h |
| Suivi absences automatique avec relance email | Loop + CDC | 2h |

### Release 4 (Gestion financiere — Sprint 5)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| Multi-financeurs (repartition couts OPCO + entreprise + apprenant) | Loop | 4h |
| Generation BPF automatique (Bilan Pedagogique et Financier) | Loop | 6h |
| Interface OPCO (format d'echange standard) | Loop | 4h |
| Commission formateurs avec stats individuelles | Loop | 3h |
| Tarification multiple par formation (OPCO vs individuel vs B2B) | Loop (Odoo) | 2h |

### Release 5 (Tags dynamiques + documents — Sprint 6)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| Systeme de tags dynamiques (300+ variables) | Loop | 6h |
| Editeur de templates de documents (WYSIWYG) | Loop | 8h |
| Signature electronique multi-parties (3 signataires) | Loop | 4h |
| Generation batch de documents (ZIP) | CDC existant | 3h |
| Drive integre avec dossiers automatiques par session | Loop + GED Alfresco | 4h |

### Release 6 (Workflows visuels + avance — Phase 2)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| Editeur de workflows visuel (drag & drop) | Loop | 12h |
| Workflows conditionnels configurables | Loop | 8h |
| Declencheurs automatiques personnalisables | Loop | 4h |
| Actions en masse (bulk operations) | Loop | 3h |

### Release 7 (Gestion des lieux / presentiel — Phase 2)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| Modele Lieu (adresse, capacite, equipements, accessibilite PMR) | Loop | 2h |
| Planning des salles avec detection de conflits | Loop | 4h |
| Calendrier visuel interactif (drag & drop) | Loop | 6h |
| Gestion multi-centre | Loop | 3h |

### Release 8 (Visioconference integree — Phase 2)

| Fonctionnalite | Source | Effort |
|----------------|--------|--------|
| Integration BigBlueButton natif dans le LMS | Loop | 4h |
| Enregistrement automatique des sessions | Loop | 2h |
| Suivi de presence en visio (logs connexion) | Loop | 3h |
| Chat + sondages integres | Loop | 2h |

---

## 4. MODELES DJANGO SUPPLEMENTAIRES (a ajouter aux 43 existants)

| Modele | Release | Champs principaux |
|--------|---------|-------------------|
| `TagTemplate` | R5 | name, slug, description, category, expression |
| `DocumentTemplate` | R5 | name, type, body_html, tags_used, is_active |
| `SignatureRequest` | R5 | document, signataires (M2M), statut, date_envoi, date_signature |
| `Lieu` | R7 | name, adresse, capacite, equipements, accessibilite_pmr, centre |
| `ReservationSalle` | R7 | lieu, formation, session, date, heure_debut, heure_fin |
| `FinanceurRepartition` | R4 | convention, financeur, type (OPCO/entreprise/individuel), montant, pourcentage |
| `CommissionFormateur` | R4 | formateur, formation, session, montant, taux, statut_paiement |
| `BPF` | R4 | annee, donnees_json, genere_le, pdf_url |
| `WorkflowRule` | R6 | name, trigger_event, conditions_json, actions_json, is_active, priority |
| `VisioSession` | R8 | formation, session, url_bbb, date, duree, enregistrement_url |

**Total modeles mis a jour : ~53**

---

## 5. RESUME PAR RELEASE

| Release | Focus | Nb fonctionnalites | Effort |
|---------|-------|-------------------|--------|
| **R1** | MVP Qualiopi (modeles + PDFs + dashboard) | ~30 | ~60h |
| **R2** | Automatisations (workflows + emails + veille) | ~15 | ~30h |
| **R3** | Emargement avance (QR code, mobile, geoloc) | ~6 | ~16h |
| **R4** | Finance (multi-financeurs, BPF, commissions) | ~5 | ~19h |
| **R5** | Tags dynamiques + documents avances | ~5 | ~25h |
| **R6** | Workflows visuels configurables | ~4 | ~27h |
| **R7** | Gestion lieux / presentiel | ~4 | ~15h |
| **R8** | Visioconference integree | ~4 | ~11h |
| **TOTAL** | | **~73** | **~203h** |
