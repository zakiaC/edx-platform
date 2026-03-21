# Preconisations Client — Mission Formations

> Document a fournir aux clients B2B et partenaires
> Prerequis techniques et fonctionnels pour utiliser la plateforme

---

## 1. PRESENTATION DE LA PLATEFORME

Mission Formations est une plateforme de formation professionnelle en ligne
hebergee et geree par Mission Formations (SaaS). Le client n'a **rien a installer**.

| Element | Detail |
|---------|--------|
| **Acces** | Navigateur web (aucune installation) |
| **URL** | `https://academie.missionformations.com` |
| **Disponibilite** | 99.5% (hors maintenance planifiee) |
| **Support** | Chat en ligne + email + telephone |
| **Certification** | Organisme certifie Qualiopi |

---

## 2. PREREQUIS TECHNIQUES — APPRENANT

### 2.1 Equipement minimum

| Element | Minimum requis | Recommande |
|---------|---------------|-----------|
| **Ordinateur** | Tout ordinateur avec navigateur web | PC ou Mac recent (< 5 ans) |
| **Tablette** | iPad ou tablette Android recente | — |
| **Smartphone** | Possible mais non recommande pour les formations longues | — |
| **Ecran** | 1280 × 720 pixels minimum | 1920 × 1080 |

### 2.2 Navigateur web

| Navigateur | Version minimum | Recommande |
|-----------|----------------|-----------|
| **Google Chrome** | Version 90+ | ✅ Recommande |
| **Mozilla Firefox** | Version 90+ | ✅ Recommande |
| **Microsoft Edge** | Version 90+ | ✅ Compatible |
| **Safari** | Version 14+ | ✅ Compatible |
| **Internet Explorer** | — | ❌ Non supporte |

**JavaScript doit etre active** dans le navigateur.
**Les cookies doivent etre acceptes** pour la plateforme.

### 2.3 Connexion internet

| Type | Debit minimum | Recommande |
|------|-------------|-----------|
| **Cours texte + quiz** | 1 Mbps | 5 Mbps |
| **Cours avec videos** | 5 Mbps | 10 Mbps |
| **Visioconference / classe virtuelle** | 5 Mbps | 15 Mbps |
| **Masterclass en streaming** | 10 Mbps | 20 Mbps |

### 2.4 Audio et video (si classes virtuelles)

| Element | Requis |
|---------|--------|
| **Casque ou haut-parleurs** | Oui (pour les videos et visios) |
| **Micro** | Oui (pour les classes virtuelles interactives) |
| **Webcam** | Recommandee (non obligatoire) |

### 2.5 Logiciels

| Logiciel | Usage | Obligatoire ? |
|----------|-------|--------------|
| **Navigateur web** | Acces a la plateforme | Oui |
| **Lecteur PDF** | Telechargement des attestations et documents | Oui (integre aux navigateurs) |
| **Zoom / BigBlueButton** | Classes virtuelles (si prevues dans la formation) | Selon la formation |

---

## 3. PREREQUIS TECHNIQUES — ENTREPRISE (B2B)

### 3.1 Aucune installation requise

Mission Formations est une solution **100% SaaS**. L'entreprise n'a pas besoin de :
- ❌ Installer de logiciel sur les postes
- ❌ Configurer de serveur
- ❌ Ouvrir de ports dans le pare-feu
- ❌ Mettre en place de VPN
- ❌ Modifier la configuration reseau

### 3.2 Acces reseau

| Element | Detail |
|---------|--------|
| **Protocole** | HTTPS (port 443) |
| **Domaine** | `*.missionformations.com` |
| **Proxy d'entreprise** | Compatible (HTTPS standard) |
| **Filtrage URL** | Autoriser `*.missionformations.com` si le proxy filtre les sites |

**Si l'entreprise utilise un proxy filtrant**, demander au service informatique d'autoriser :
```
academie.missionformations.com
studio.missionformations.com
apps.missionformations.com
chat.missionformations.com
```

### 3.3 Comptes utilisateurs

| Element | Detail |
|---------|--------|
| **Creation de compte** | Par l'admin Mission Formations ou auto-inscription |
| **Identifiant** | Adresse email professionnelle du stagiaire |
| **Mot de passe** | Defini par le stagiaire lors de la premiere connexion |
| **SSO** | Non disponible actuellement (prevu en V2) |

### 3.4 Responsable de la formation cote client

L'entreprise doit designer un **referent formation** qui sera l'interlocuteur de Mission Formations pour :
- Fournir la liste des stagiaires (nom, prenom, email)
- Signer la convention de formation
- Suivre la progression des collaborateurs
- Recevoir les bilans pedagogiques

---

## 4. SERVICES INCLUS

### 4.1 Pour l'apprenant

| Service | Description | Inclus |
|---------|------------|--------|
| **Acces aux cours** | Formations en ligne (videos, textes, quiz, exercices) | ✅ |
| **Dashboard personnel** | Progression, certificats, statistiques | ✅ |
| **Quiz et evaluations** | QCM, exercices, cas pratiques | ✅ |
| **Certificat de fin de formation** | PDF telecharge depuis la plateforme | ✅ |
| **Attestation de formation** | PDF conforme au Code du travail | ✅ |
| **Chat support** | Assistance en temps reel via le widget de chat | ✅ |
| **Centre d'aide** | FAQ et guides en ligne | ✅ |
| **Forum de discussion** | Echanges entre apprenants et formateur | ✅ |

### 4.2 Pour l'entreprise (B2B)

| Service | Description | Inclus |
|---------|------------|--------|
| **Espace academie dedie** | Sous-domaine personnalise (ex: `abc.academie.missionformations.com`) | ✅ |
| **Dashboard de suivi RH** | Progression des collaborateurs, taux de completion | ✅ |
| **Convention de formation** | PDF genere et signe electroniquement | ✅ |
| **Feuille d'emargement** | Generee automatiquement depuis les logs de connexion | ✅ |
| **Rapport de suivi pedagogique** | Bilan periodique des progressions | ✅ |
| **Bilan de formation** | Dossier complet en fin de session (ZIP) | ✅ |
| **Certificats de realisation** | Un par stagiaire, conforme OPCO/CPF | ✅ |
| **Facturation OPCO** | Facture adressable a l'OPCO directement | ✅ |

### 4.3 Pour le formateur

| Service | Description | Inclus |
|---------|------------|--------|
| **Acces Studio** | Creation et modification des contenus de formation | ✅ |
| **Dashboard formateur** | Suivi des apprenants, notes, rapports | ✅ |
| **Export des resultats** | CSV des notes et progressions | ✅ |
| **Messagerie interne** | Communication avec les apprenants | ✅ |

---

## 5. SERVICES COMPLEMENTAIRES (en option)

| Service | Description | Tarif |
|---------|------------|-------|
| **Creation de formation sur mesure** | Contenu pedagogique personnalise pour l'entreprise | Sur devis |
| **Branding academie** | Logo et couleurs de l'entreprise sur la plateforme | Sur devis |
| **Integration SI** | Connecteur avec le SIRH de l'entreprise | Sur devis |
| **Formation des formateurs** | Prise en main de Studio et du dashboard | Inclus (1 session) |
| **Accompagnement Qualiopi** | Aide a la constitution du dossier Qualiopi | Sur devis |

---

## 6. DONNEES ET CONFIDENTIALITE

### 6.1 Hebergement

| Element | Detail |
|---------|--------|
| **Hebergeur** | OVH (France) |
| **Localisation** | Datacenter en France (Roubaix / Gravelines) |
| **Conformite** | RGPD, loi francaise |
| **Certification hebergeur** | OVH certifie ISO 27001, SOC 1/2/3, HDS |

### 6.2 Donnees collectees

| Donnee | Finalite | Duree de conservation |
|--------|----------|----------------------|
| Nom, prenom, email | Identification et acces | 5 ans apres fin de formation |
| Progression dans les cours | Suivi pedagogique | 5 ans |
| Resultats des evaluations | Certification et Qualiopi | 5 ans |
| Logs de connexion | Emargement e-learning (Qualiopi) | 5 ans |
| Enquetes de satisfaction | Amelioration continue (Qualiopi) | 5 ans |
| Donnees de facturation | Comptabilite | 10 ans |

### 6.3 Engagements

| Engagement | Detail |
|-----------|--------|
| **Pas de revente de donnees** | Les donnees des apprenants ne sont jamais vendues ni partagees |
| **Acces restreint** | Seuls les administrateurs Mission Formations et le formateur accedent aux donnees |
| **Droit a l'effacement** | Sur demande, toutes les donnees d'un apprenant peuvent etre supprimees |
| **Portabilite** | Export des donnees au format CSV sur demande |
| **Notification de violation** | En cas de breche, notification dans les 72h (CNIL + personnes concernees) |

---

## 7. PROCESSUS D'ONBOARDING CLIENT B2B

### 7.1 Etapes

```
1. CONTACT INITIAL
   │  Prise de contact (formulaire, chat, telephone)
   │  Identification du besoin (formations, nombre de stagiaires, financement)
   ▼
2. DEVIS ET CONVENTION
   │  Envoi du devis personnalise
   │  Convention de formation (signature electronique)
   │  Dossier OPCO si financement externe
   ▼
3. CONFIGURATION
   │  Creation de l'academie (espace entreprise)
   │  Inscription des stagiaires (liste fournie par le referent RH)
   │  Attribution des formations
   ▼
4. LANCEMENT
   │  Email de bienvenue envoye a chaque stagiaire
   │  Convocation avec identifiants de connexion
   │  Session de prise en main (optionnelle)
   ▼
5. SUIVI
   │  Dashboard RH accessible au referent formation
   │  Rapports de suivi periodiques
   │  Points intermediaires avec le referent
   ▼
6. CLOTURE
   │  Attestations de fin de formation
   │  Certificats de realisation
   │  Bilan de formation (dossier complet)
   │  Enquete de satisfaction
   │  Facturation finale
```

### 7.2 Delais

| Etape | Delai |
|-------|-------|
| Devis | 24-48h apres la demande |
| Convention signee → acces plateforme | 48h |
| Inscription des stagiaires | 24h apres reception de la liste |
| Debut effectif de la formation | Selon les dates convenues |

### 7.3 Informations a fournir par le client

| Information | Format | Obligatoire |
|------------|--------|------------|
| **Raison sociale** | Texte | Oui |
| **SIRET** | 14 chiffres | Oui |
| **Adresse** | Texte | Oui |
| **Referent formation** (nom, email, telephone) | Texte | Oui |
| **Liste des stagiaires** (nom, prenom, email) | CSV ou Excel | Oui |
| **OPCO** (si financement OPCO) | Nom + numero de prise en charge | Si applicable |
| **Logo entreprise** (si espace personnalise) | PNG/SVG, 200×200 px min | Optionnel |

---

## 8. SUPPORT ET ASSISTANCE

### 8.1 Canaux de support

| Canal | Disponibilite | Temps de reponse |
|-------|-------------|-----------------|
| **Chat en ligne** (widget sur la plateforme) | Lun-Ven 9h-18h | < 15 min (heures ouvertes) |
| **Email** (contact@missionformations.com) | 24/7 (reponse heures ouvrees) | < 24h |
| **Telephone** | Lun-Ven 9h-18h | Immediat |
| **Centre d'aide** (FAQ en ligne) | 24/7 | Self-service |

### 8.2 Types de demandes

| Type | Exemples | Qui traite |
|------|----------|-----------|
| **Utilisation** | Comment acceder a mon cours ? Ou est mon certificat ? | Support N1 (FAQ) ou N2 (chat) |
| **Technique** | Page qui ne charge pas, erreur de connexion | Support N2 (chat/email) |
| **Administratif** | Facture, convention, attestation | Admin Mission Formations |
| **Pedagogique** | Question sur le contenu d'un cours | Formateur |

---

## 9. TARIFICATION

### 9.1 Modeles de tarification

| Modele | Description | Pour qui |
|--------|------------|----------|
| **A la formation** | Prix fixe par formation et par apprenant | Individuel, CPF |
| **Pack entreprise** | Tarif degressif par volume (5-10-20+ stagiaires) | Entreprises B2B |
| **Abonnement academie** | Acces illimite a un catalogue de formations | Grands comptes |

### 9.2 Ce qui est inclus dans le tarif

| Element | Inclus |
|---------|--------|
| Acces a la formation (duree illimitee dans la periode) | ✅ |
| Support technique et pedagogique | ✅ |
| Attestation de fin de formation (PDF) | ✅ |
| Certificat de realisation (PDF) | ✅ |
| Convention de formation | ✅ |
| Feuille d'emargement | ✅ |
| Rapport de suivi pedagogique | ✅ |
| Bilan de formation (dossier complet) | ✅ |
| Hebergement et maintenance de la plateforme | ✅ |

### 9.3 Modalites de paiement

| Mode | Detail |
|------|--------|
| **Virement bancaire** | Sur presentation de facture |
| **Carte bancaire** | Paiement en ligne securise (Stripe) |
| **OPCO** | Facturation directe a l'OPCO sur numero de prise en charge |
| **CPF** | Via MonCompteFormation (quand disponible) |

---

## 10. CONTACTS

| Role | Nom | Email | Telephone |
|------|-----|-------|-----------|
| **Direction** | [A completer] | direction@missionformations.com | [A completer] |
| **Support technique** | Support MF | contact@missionformations.com | [A completer] |
| **Referent handicap** | [A completer] | handicap@missionformations.com | [A completer] |
| **DPO** | [A completer] | dpo@missionformations.com | [A completer] |
| **Responsable pedagogique** | [A completer] | pedagogie@missionformations.com | [A completer] |
