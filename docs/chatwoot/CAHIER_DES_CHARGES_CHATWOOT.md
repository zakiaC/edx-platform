# Cahier des charges — Module Chat / Messagerie Mission Formations

> Version 1.0 — 19 mars 2026
> Objectif : externaliser le chat, definir les besoins fonctionnels, choisir la bonne solution

---

## PARTIE 1 — ETAT ACTUEL

### Infrastructure actuelle (a supprimer du VPS OpenEdX)

| Container | Rôle | RAM |
|-----------|------|-----|
| chatwoot-rails | App Ruby on Rails (serveur web) | ~400-600 Mo |
| chatwoot-sidekiq | Worker async (jobs, emails, webhooks) | ~200-300 Mo |
| chatwoot-postgres | PostgreSQL avec pgvector (89 tables) | ~200-400 Mo |
| chatwoot-redis | Cache + queues Sidekiq | ~100-200 Mo |
| **Total** | **4 containers** | **~900 Mo - 1.5 Go** |

### Ce qui fonctionne

- Widget chat integre dans le footer du LMS (toutes les pages)
- Interface agent sur chat.staging.missionformations.com
- Conversations stockees dans PostgreSQL local
- Reverse proxy via Caddy (plugin Tutor mission_wewill.py)
- Token widget : `SqDrn962MP4DfDkr6qdWFJ9f`

### Ce qui etait prevu (fork WeWill — CHAT-1 a CHAT-9)

- Fork du repo Chatwoot officiel → rebranding "WeWill"
- Image Docker custom sur GitHub Container Registry
- Traduction francaise complete
- Webhook Odoo (lead a chaque conversation)
- Effort estime : ~20h
- **Recommandation : abandonner le fork** — ROI negatif pour un dev solo

---

## PARTIE 2 — BESOINS FONCTIONNELS

### Besoins essentiels (jour 1)

| # | Besoin | Description | Priorite |
|---|--------|-------------|----------|
| CH-01 | Widget chat sur le LMS | Bulle en bas a droite, accessible sur toutes les pages | Critique |
| CH-02 | Chat en temps reel | Conversation texte entre visiteur/apprenant et equipe support | Critique |
| CH-03 | Interface agent | Dashboard pour l'equipe qui repond aux conversations | Critique |
| CH-04 | Notifications | Email quand un message est recu (agent absent) | Critique |
| CH-05 | Historique conversations | Retrouver les conversations passees par contact | Critique |
| CH-06 | Multi-agents | Plusieurs personnes peuvent repondre (repartition) | Important |

### Besoins avances (phase 2)

| # | Besoin | Description | Priorite |
|---|--------|-------------|----------|
| CH-07 | Identification apprenant | Si l'utilisateur est connecte au LMS, transmettre son nom/email au chat | Important |
| CH-08 | Bot de pre-qualification | Questions automatiques avant transfert a un agent (nom, objet, formation concernee) | Souhaitable |
| CH-09 | Reponses pre-ecrites | Templates de reponses rapides (FAQ, horaires, tarifs) | Souhaitable |
| CH-10 | Webhook → Odoo | Creer un lead Odoo a chaque nouvelle conversation | Phase Odoo |
| CH-11 | Webhook → Qualiopi | Enregistrer la conversation comme preuve de suivi (Ind. 10, 14) | Phase Qualiopi |
| CH-12 | Multicanal | Email, WhatsApp, Facebook Messenger (en plus du widget web) | Phase 2 |
| CH-13 | Formulaire hors-ligne | Si aucun agent connecte, proposer un formulaire (→ email) | Important |
| CH-14 | RGPD | Consentement avant debut de conversation, suppression sur demande | Critique |
| CH-15 | Analytics | Temps de reponse moyen, nb conversations/jour, satisfaction | Souhaitable |

### Besoins Qualiopi lies au chat

| Indicateur | Besoin | Implementation |
|------------|--------|----------------|
| Ind. 10 | Tracer les echanges d'adaptation en cours de formation | Export conversation → piece jointe dans le dossier Qualiopi |
| Ind. 14 | Detecter les signaux d'abandon via le chat | Tag "risque abandon" sur une conversation → alerte dashboard Qualiopi |
| Ind. 32 | Reclamation recue par chat | Bouton "Convertir en reclamation" → cree une entree dans le registre Qualiopi |

---

## PARTIE 3 — ANALYSE DES OPTIONS

### Option 1 : Chatwoot Cloud (SaaS)

| Critere | Detail |
|---------|--------|
| **Effort migration** | 2h (changer l'URL du widget + supprimer les containers Docker) |
| **Cout** | Plan Hacker : gratuit (limité) / Business : 19$/agent/mois |
| **Maintenance** | Zero |
| **RAM liberee** | ~900 Mo - 1.5 Go |
| **Containers supprimes** | 4 (rails, sidekiq, postgres, redis) |
| **Fonctionnalites** | Toutes celles de la version self-hosted + mises a jour auto |
| **Webhooks** | Oui (Odoo, Qualiopi, n'importe quel endpoint) |
| **RGPD** | Hebergement EU disponible (plan Business) |
| **Personnalisation** | Widget personnalisable (couleurs, textes), pas de branding custom complet |
| **Donnees** | Stockees chez Chatwoot (pas chez toi) |
| **Verdict** | **Recommande** pour un dev solo |

### Option 2 : Chatwoot self-hosted externalise (autre VPS)

| Critere | Detail |
|---------|--------|
| **Effort migration** | 4-6h (deployer sur nouveau VPS, migrer la DB, reconfigurer DNS) |
| **Cout** | 5-10€/mois (petit VPS 4 Go OVH) |
| **Maintenance** | Moyenne (mises a jour Docker, backup PostgreSQL) |
| **RAM liberee sur VPS principal** | ~900 Mo - 1.5 Go |
| **Fonctionnalites** | Identiques a aujourd'hui |
| **Personnalisation** | Totale (acces au code) |
| **Donnees** | Chez toi (sur ton VPS) |
| **Verdict** | Acceptable si tu veux garder le controle des donnees |

### Option 3 : Crisp

| Critere | Detail |
|---------|--------|
| **Effort** | 1h (remplacer le widget JS) |
| **Cout** | Gratuit (2 agents) / Pro : 25€/mois (4 agents) |
| **Maintenance** | Zero |
| **RAM liberee** | ~900 Mo - 1.5 Go |
| **Fonctionnalites** | Chat, bot, CRM integre, base de connaissances, status page |
| **Webhooks** | Oui |
| **RGPD** | Hebergement EU (France), conforme RGPD natif |
| **En francais** | Oui, natif |
| **Verdict** | **Meilleure alternative** si tu quittes Chatwoot |

### Option 4 : Tawk.to

| Critere | Detail |
|---------|--------|
| **Effort** | 1h |
| **Cout** | Gratuit (100% gratuit, modele pub/branding) |
| **Maintenance** | Zero |
| **Fonctionnalites** | Chat, tickets, base de connaissances |
| **Webhooks** | Limites |
| **RGPD** | Serveurs US (problematique) |
| **Verdict** | Budget zero, mais RGPD non conforme |

### Option 5 : Construire from scratch

| Critere | Detail |
|---------|--------|
| **Effort** | 100-200h minimum (WebSocket, interface agent, historique, notifications) |
| **Cout** | 0€ mais temps enorme |
| **Maintenance** | Tres lourde |
| **Verdict** | **A proscrire absolument** — aucun ROI |

### Matrice de decision

| Critere | Poids | Chatwoot Cloud | Chatwoot VPS | Crisp | Tawk.to | From scratch |
|---------|-------|---------------|-------------|-------|---------|-------------|
| Cout | 3 | 4 | 4 | 5 | 5 | 5 |
| Effort de mise en place | 4 | 5 | 3 | 5 | 5 | 1 |
| Maintenance dev solo | 5 | 5 | 3 | 5 | 5 | 1 |
| RAM liberee | 4 | 5 | 5 | 5 | 5 | 3 |
| Webhooks (Odoo, Qualiopi) | 4 | 5 | 5 | 4 | 2 | 5 |
| RGPD / donnees EU | 3 | 4 | 5 | 5 | 2 | 5 |
| Fonctionnalites | 3 | 5 | 5 | 5 | 3 | 2 |
| **Score** | | **124/130** | **109/130** | **127/130** | **101/130** | **67/130** |

**Top 2 : Crisp (127) puis Chatwoot Cloud (124)**

---

## PARTIE 4 — RECOMMANDATION

### Solution recommandee : Crisp (plan Pro) ou Chatwoot Cloud

**Critere de choix final entre les deux :**

| | Crisp | Chatwoot Cloud |
|---|---|---|
| Hebergement | **France** (RGPD natif) | EU disponible (plan Business) |
| Langue | **Francais natif** | Francais disponible |
| Prix 2 agents | **Gratuit** | Gratuit (limite) |
| Prix 4 agents | 25€/mois | 76$/mois (19$/agent × 4) |
| CRM integre | **Oui** | Oui |
| Bot | **Oui** (inclus) | Oui |
| Base de connaissances | **Oui** (inclus) | Non |
| Status page | **Oui** | Non |

**Pour Mission Formations → Crisp** est le meilleur choix :
- Heberge en France (conforme RGPD organisme de formation)
- Francais natif
- Gratuit pour 2 agents (suffisant au lancement)
- CRM integre (peut remplacer une partie d'Odoo pour les leads)
- Base de connaissances integree (peut enrichir la page /aide/)

---

## PARTIE 5 — PLAN DE MIGRATION

### Etape 1 : Creer le compte Crisp (ou Chatwoot Cloud)
- Creer le workspace Mission Formations
- Configurer les agents (admin + support)
- Personnaliser le widget (couleurs MF, textes FR)

### Etape 2 : Integrer le widget dans le LMS
- Remplacer le script Chatwoot dans `footer.html` par le script Crisp
- Transmettre l'identite de l'utilisateur connecte (email, nom)
```javascript
// Exemple Crisp — identification user connecte au LMS
if (window.__user_email) {
  $crisp.push(["set", "user:email", [window.__user_email]]);
  $crisp.push(["set", "user:nickname", [window.__user_name]]);
}
```

### Etape 3 : Configurer les webhooks
- Webhook nouvelle conversation → Odoo (creer lead)
- Webhook tag "reclamation" → Qualiopi (creer reclamation)
- Webhook tag "abandon" → Qualiopi (alerte abandon)

### Etape 4 : Supprimer Chatwoot du VPS OpenEdX
- Arreter les 4 containers (rails, sidekiq, postgres, redis)
- Supprimer les volumes Docker
- Supprimer le plugin Tutor `mission_wewill.py`
- Supprimer la config Caddy reverse proxy
- Nettoyer le DNS (supprimer chat.staging.missionformations.com)

### Etape 5 : Exporter les donnees (si necessaire)
- Exporter les conversations existantes depuis Chatwoot (API)
- Archiver pour conformite

**Effort total : 2-4 heures**
**RAM liberee : ~900 Mo - 1.5 Go**
**Containers supprimes : 4**
