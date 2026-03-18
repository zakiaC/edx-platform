# Guide WeWill — Equipe Mission Formations

> Documentation pour l'equipe interne : gestion des conversations,
> parametrage, agents, automatisations et reporting.
> URL admin : https://chat.staging.missionformations.com

---

## 1. Connexion a l'interface admin

1. Aller sur `https://chat.staging.missionformations.com`
2. Se connecter avec vos identifiants
3. Vous arrivez sur le **tableau de bord** avec les conversations en cours

### Roles disponibles

| Role | Droits |
|------|--------|
| **Super Admin** | Tout (comptes, facturation, parametres globaux) |
| **Administrateur** | Gestion agents, inboxes, automatisations, rapports |
| **Agent** | Repondre aux conversations, assigner, etiqueter |

---

## 2. Gerer les conversations

### Vue principale

La page **Conversations** affiche toutes les discussions en cours :

- **Mine** : conversations qui vous sont assignees
- **Non assignees** : conversations en attente d'un agent
- **Toutes** : vue globale

### Repondre a un message

1. Cliquer sur la conversation
2. Taper la reponse dans le champ en bas
3. Appuyer sur Entree ou cliquer sur Envoyer
4. Le visiteur recoit la reponse en temps reel dans le widget

### Actions sur une conversation

| Action | Comment | Utilite |
|--------|---------|---------|
| **Assigner** | Clic sur l'agent dans le panneau droit | Distribuer le travail |
| **Etiqueter** | Ajouter un label (ex: "VTC", "Inscription", "Technique") | Organiser et filtrer |
| **Resoudre** | Bouton "Resoudre" en haut | Fermer la conversation |
| **Reouvrir** | Bouton "Reouvrir" | Si le client revient |
| **Snooze** | Reporter la conversation (1h, demain, semaine prochaine) | Traiter plus tard |
| **Note interne** | Onglet "Notes" dans la conversation | Ecrire un memo visible uniquement par l'equipe |
| **Transferer** | Assigner a un autre agent ou equipe | Escalade |

### Reponses predefinies (Canned Responses)

Creer des reponses types pour gagner du temps :

1. **Parametres** → **Reponses predefinies** → **Ajouter**
2. Definir un raccourci (ex: `/bonjour`)
3. Ecrire le texte de la reponse
4. Dans une conversation, taper `/bonjour` et la reponse s'insere

**Reponses suggerees pour Mission Formations :**

| Raccourci | Reponse |
|-----------|---------|
| `/bonjour` | Bonjour ! Bienvenue sur l'Academie Mission Formations. Comment puis-je vous aider ? |
| `/inscription` | Pour vous inscrire, rendez-vous sur notre page d'accueil et cliquez sur "Creer un compte". Vous recevrez un email de confirmation. |
| `/certificat` | Votre certificat est genere automatiquement des que vous atteignez le seuil de reussite (60%). Rafraichissez votre tableau de bord. |
| `/mdp` | Pour reinitialiser votre mot de passe, cliquez sur "Mot de passe oublie" sur la page de connexion. Un lien vous sera envoye par email. |
| `/cpf` | Nos formations sont eligibles au CPF. Rendez-vous sur moncompteformation.gouv.fr ou contactez-nous pour un accompagnement personnalise. |
| `/horaires` | Notre equipe est disponible du lundi au vendredi, 9h-18h. En dehors de ces horaires, laissez un message et nous vous repondrons sous 24h. |
| `/cours_absent` | Verifiez que vous etes connecte avec le meme email utilise lors de l'inscription. Si le probleme persiste, envoyez-nous votre nom complet et le titre du cours. |

---

## 3. Gerer les agents

### Ajouter un agent

1. **Parametres** → **Agents** → **Ajouter un agent**
2. Renseigner : nom, email, role
3. L'agent recoit un email d'invitation
4. Il se connecte et voit les conversations qui lui sont assignees

### Equipes

Creer des equipes pour organiser les agents par competence :

| Equipe suggeree | Agents | Conversations |
|-----------------|--------|---------------|
| **Support pedagogique** | Formateurs | Questions sur les cours, exercices |
| **Support technique** | Admins | Connexion, bugs, certificats |
| **Commercial** | Commerciaux | Inscriptions, CPF, devis B2B |
| **Direction** | Super admin | Escalades, reclamations |

1. **Parametres** → **Equipes** → **Creer une equipe**
2. Nommer l'equipe et ajouter les agents
3. Les conversations peuvent etre assignees a une equipe entiere

---

## 4. Configurer les inboxes

### Inbox actuelle

| Inbox | Type | URL cible |
|-------|------|-----------|
| Academie LMS | Website | academie.staging.missionformations.com |

### Ajouter une inbox pour le site internet

1. **Parametres** → **Inboxes** → **Ajouter**
2. Type : **Website**
3. Nom : "Site Mission Formations"
4. URL : `https://missionformations.com`
5. Couleur du widget : `#0965D0`
6. Copier le token genere et l'ajouter au footer du site

### Ajouter un canal email

1. **Parametres** → **Inboxes** → **Ajouter**
2. Type : **Email**
3. Configurer le SMTP/IMAP avec votre serveur mail
4. Les emails entrants deviennent des conversations WeWill

### Ajouter un canal WhatsApp (optionnel)

1. **Parametres** → **Inboxes** → **Ajouter**
2. Type : **WhatsApp** (via Twilio ou WhatsApp Business API)
3. Configurer le numero et les credentials API

---

## 5. Automatisations

### Regles d'assignation automatique

1. **Parametres** → **Automatisation** → **Ajouter une regle**
2. Exemples :

| Condition | Action |
|-----------|--------|
| Message contient "inscription" | Assigner a l'equipe Commerciale |
| Message contient "certificat" | Assigner a l'equipe Support pedagogique |
| Message contient "bug" ou "erreur" | Assigner a l'equipe Support technique |
| Conversation non assignee depuis 5 min | Envoyer notification a tous les agents |

### Message d'accueil automatique

1. **Parametres** → **Inboxes** → cliquer sur l'inbox → **Configuration**
2. **Welcome message** : activer
3. Texte : "Bonjour ! Bienvenue sur l'Academie Mission. Comment pouvons-nous vous aider ?"

### Horaires de disponibilite

1. **Parametres** → **Inboxes** → cliquer sur l'inbox → **Horaires**
2. Definir : Lundi-Vendredi 9h-18h
3. En dehors : afficher un message automatique "Notre equipe est absente, nous repondrons sous 24h."

### Bot de pre-qualification

1. **Parametres** → **Inboxes** → **Pre-chat form** → activer
2. Demander avant le chat :
   - Nom (obligatoire)
   - Email (obligatoire)
   - Sujet : Inscription / Probleme technique / Question sur un cours / Autre

---

## 6. Etiquettes (Labels)

Creer des etiquettes pour classifier les conversations :

| Etiquette | Couleur | Usage |
|-----------|---------|-------|
| `vtc` | Vert | Questions liees aux formations VTC |
| `inscription` | Bleu | Demandes d'inscription |
| `technique` | Rouge | Bugs, problemes de connexion |
| `cpf` | Orange | Questions financement CPF/OPCO |
| `b2b` | Violet | Entreprises clientes |
| `urgent` | Rouge vif | A traiter en priorite |
| `certificat` | Jaune | Questions sur les certificats |

1. **Parametres** → **Etiquettes** → **Ajouter**
2. Les agents peuvent ajouter/retirer des etiquettes sur chaque conversation

---

## 7. Rapports et statistiques

### Tableau de bord rapports

1. **Rapports** dans le menu lateral
2. Metriques disponibles :

| Metrique | Description |
|----------|-------------|
| **Conversations** | Nombre de conversations ouvertes/resolues |
| **Temps de premiere reponse** | Delai moyen avant la 1ere reponse |
| **Temps de resolution** | Duree moyenne pour resoudre |
| **Messages** | Nombre de messages envoyes/recus |
| **Satisfaction (CSAT)** | Note de satisfaction client (si active) |

### Activer le CSAT

1. **Parametres** → **Inboxes** → cliquer sur l'inbox → **Configuration**
2. Activer **CSAT** (Customer Satisfaction)
3. Apres resolution, le visiteur recoit un sondage de satisfaction
4. Les resultats sont dans **Rapports** → **CSAT**

### Export des donnees

- **Rapports** → **Exporter** (CSV)
- Filtrer par periode, agent, equipe, etiquette

---

## 8. Personnalisation du widget

### Apparence

1. **Parametres** → **Inboxes** → cliquer sur l'inbox → **Widget**
2. Modifier :
   - Couleur : `#0965D0` (bleu Mission)
   - Position : Bas droite
   - Type de bulle : Standard ou etendu
   - Langue : Francais

### Message hors ligne

1. **Parametres** → **Inboxes** → **Configuration**
2. **Hors ligne** : "Notre equipe est actuellement indisponible. Laissez-nous un message et nous vous repondrons sous 24h ouvrables."

### Avatar et branding

1. **Parametres** → **Compte** → **Logo**
2. Uploader le logo Mission Formations
3. Ce logo apparait dans le widget et les emails

---

## 9. Notifications

### Configurer les notifications

Chaque agent peut configurer ses alertes :

1. **Profil** → **Notifications**
2. Options :

| Notification | Email | Push navigateur | Son |
|-------------|-------|-----------------|-----|
| Nouvelle conversation | Oui | Oui | Oui |
| Conversation assignee | Oui | Oui | Non |
| Nouvelle mention | Oui | Oui | Oui |
| Conversation non assignee | Non | Oui | Non |

### Mentions

Dans une conversation, taper `@prenom` pour mentionner un collegue. Il recevra une notification.

---

## 10. Integrations possibles

| Integration | Usage | Configuration |
|-------------|-------|---------------|
| **Slack** | Recevoir les conversations dans un channel Slack | Parametres → Integrations → Slack |
| **Webhooks** | Envoyer les evenements a une URL | Parametres → Integrations → Webhooks |
| **API REST** | Automatiser la creation de contacts/conversations | Documentation API WeWill |
| **Odoo** (futur) | Creer un lead Odoo a chaque nouvelle conversation | Via webhook → API Odoo |

---

## 11. Bonnes pratiques equipe

1. **Repondre en moins de 5 minutes** pendant les heures ouvrables
2. **Toujours saluer** le visiteur par son prenom si disponible
3. **Etiqueter** chaque conversation avant de la resoudre
4. **Utiliser les reponses predefinies** pour les questions frequentes
5. **Ecrire des notes internes** quand on escalade
6. **Ne jamais resoudre** sans avoir confirme avec le visiteur que son probleme est regle
7. **Verifier les rapports** chaque lundi pour suivre les KPIs
