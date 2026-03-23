# Avis strategique — Enrichissement du projet Mission Formations

> Date : 23 mars 2026
> Contexte : apres definition de la strategie marque blanche
> Objectif : idees a implementer dans un second temps

---

## 1. FORCES DU PROJET

### Positionnement unique

Un LMS Qualiopi-natif en marque blanche, en francais, base sur OpenEdX — ca n'existe pas.
Les concurrents font soit le LMS (Moodle, 360Learning) soit le suivi Qualiopi (Digiforma, Dendreo, Teetche) mais aucun ne combine les deux.

### Business model scalable

La marque blanche transforme Mission Formations d'un organisme de formation (CA limite par les propres formations) en un editeur SaaS (CA recurrent × nombre de clients). Business 10× plus scalable.

### Cross-selling intelligent

Chaque client marque blanche qui ajoute des formations MF a son catalogue rapporte du revenue share SANS effort commercial supplementaire.

---

## 2. ENRICHISSEMENTS A IMPLEMENTER (PHASE 2-3)

### 2.1 Marketplace de formations

**Concept** : une place de marche ou des formateurs independants publient leurs formations.

| Element | Detail |
|---------|--------|
| **Qui** | Formateurs independants, experts metier |
| **Quoi** | Ils publient leurs formations sur la plateforme MF |
| **Revenue** | Commission par vente (ex: 30% MF / 70% formateur) |
| **Avantage client MB** | Les clients marque blanche piochent dans ce catalogue pour enrichir leur offre |
| **Modele** | Comme Udemy mais pour la formation professionnelle certifiee |

**Prerequis** : 10+ clients actifs, process de validation pedagogique, contrat type formateur.

### 2.2 Module analytics avance

**Concept** : dashboard analytics en self-service pour les clients marque blanche.

| Metrique | Detail |
|----------|--------|
| Temps passe par module | Heatmap d'activite (quand les apprenants se connectent) |
| Taux de completion par module | Identifier les modules ou les apprenants decrochent |
| Parcours type | Visualisation du chemin moyen dans le cours |
| Comparaison cohortes | Session A vs session B |
| Export automatique | PDF mensuel envoye au RH client |

**Prerequis** : tracking events OpenEdX (xAPI) + outil de visualisation (Metabase ou Grafana).

### 2.3 IA comme differenciateur

**Concept** : utiliser l'IA DANS la plateforme (pas juste comme formation).

| Fonctionnalite | Detail |
|----------------|--------|
| Recommandation personnalisee | Algorithme qui recommande des formations basees sur le profil, la progression, le domaine |
| Resume de progression pour le RH | L'IA genere un resume en langage naturel de la progression d'un apprenant |
| Chatbot FAQ integre au cours | RAG sur le contenu pedagogique — l'apprenant pose une question, le bot repond avec le contenu du cours |
| Correction automatique | Les reponses ouvertes sont evaluees par l'IA (avec validation formateur) |
| Generation de quiz | L'IA propose des quiz basees sur le contenu du module |

**Prerequis** : API Claude/OpenAI, contenu pedagogique structure, budget API.

### 2.4 API publique documentee

**Concept** : documentation Swagger/OpenAPI pour que les clients integrent la plateforme dans leur SI.

| Endpoint public | Usage client |
|----------------|-------------|
| GET /api/v1/enrollments | Lister les inscriptions (synchro SIRH) |
| GET /api/v1/progress | Progression des apprenants (dashboard RH custom) |
| GET /api/v1/certificates | Certificats obtenus (archivage client) |
| POST /api/v1/enroll | Inscrire un apprenant depuis le SIRH |
| GET /api/v1/catalog | Catalogue des formations disponibles |

**Prerequis** : API hub Qualiopi stable, authentification OAuth2, rate limiting, doc Swagger.

### 2.5 Programme partenaire / revendeur

**Concept** : reseau de revendeurs qui recommandent la plateforme.

| Type de partenaire | Role | Commission |
|-------------------|------|-----------|
| **Consultant Qualiopi** | Recommande la plateforme a ses clients OF | 10-15% recurrent |
| **Integrateur** | Configure la plateforme pour le client | 15-20% setup + 5% recurrent |
| **Apporteur d'affaires** | Met en relation avec un prospect | 10% premiere annee |

**Modele inspire de** : Provence AI avec Atol CD (integrateur).

### 2.6 Certification des formateurs

**Concept** : badge "Formateur certifie Mission Formations" pour les formateurs qui maitrisent l'outil.

| Niveau | Contenu | Badge |
|--------|---------|-------|
| Bronze | Prise en main Studio (creer un cours) | "Formateur MF" |
| Argent | Gestion avancee (quiz, evaluations, rapports) | "Expert Studio MF" |
| Or | Administration plateforme + Qualiopi | "Administrateur MF" |

**Avantage** : fidelisation formateurs, reseau, credibilite.

---

## 3. PRIORITES

| Priorite | Quand | Enrichissement |
|----------|-------|---------------|
| **1 — Maintenant** | Sprint 1-6 | Multi-tenant + marque blanche + premier client |
| **2 — Apres 3 clients** | Mois 3-6 | Analytics avance + API publique |
| **3 — Apres 5 clients** | Mois 6-9 | Programme partenaire + certification formateurs |
| **4 — Apres 10 clients** | Mois 9-12 | Marketplace + IA dans la plateforme |

### Ce qu'il ne faut PAS faire maintenant

| Idee | Pourquoi attendre |
|------|-------------------|
| Marketplace de formations | Pas de volume, pas de formateurs independants encore |
| IA dans la plateforme | La stabilite de base n'est pas encore assuree |
| Programme partenaire | Il faut d'abord prouver le modele avec des clients directs |
| API publique Swagger | L'API interne n'est pas encore construite |

---

## 4. LA PRIORITE ABSOLUE

**Signer le premier client.**

Tout le reste n'a de valeur que si des clients paient. La formation VTC est prete. Le staging est stable. L'architecture est documentee.

### Ce qu'il faut pour le premier client

| Element | Effort | Statut |
|---------|--------|--------|
| Kit commercial (plaquette + tarifs) | 3h | A faire |
| 10 prospects identifies | 2h | A faire |
| 3 demos | 3 × 1h | A faire |
| 1 signature | — | Objectif |
| Multi-tenant fonctionnel (pour la demo) | 8h | A faire |
