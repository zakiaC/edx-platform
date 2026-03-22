# Registre des traitements de donnees personnelles

> Organisme : Mission Formations
> Responsable du traitement : [A completer — nom du gerant]
> DPO / Referent RGPD : [A completer]
> Date de creation : 22 mars 2026
> Derniere mise a jour : 22 mars 2026

---

## Traitement 1 — Gestion des apprenants

| Champ | Detail |
|-------|--------|
| **Finalite** | Gestion des inscriptions, suivi pedagogique, delivrance des certificats |
| **Base legale** | Execution du contrat de formation (art. 6.1.b RGPD) |
| **Categories de personnes** | Apprenants (stagiaires de la formation professionnelle) |
| **Donnees collectees** | Nom, prenom, email, progression dans les cours, notes aux evaluations, resultats quiz, dates de connexion, certificats obtenus |
| **Source** | Formulaire d'inscription, plateforme LMS (OpenEdX) |
| **Destinataires internes** | Responsable pedagogique, formateurs, admin plateforme |
| **Destinataires externes** | OPCO (si financement), employeur (si B2B, rapports de suivi) |
| **Transfert hors UE** | Non |
| **Duree de conservation** | 5 ans apres la fin de la formation (obligation Qualiopi) |
| **Mesures de securite** | HTTPS, authentification par mot de passe, acces par role, base de donnees sur serveur securise en France (OVH) |

---

## Traitement 2 — Gestion des formateurs

| Champ | Detail |
|-------|--------|
| **Finalite** | Gestion des intervenants, suivi des qualifications, conformite Qualiopi |
| **Base legale** | Execution du contrat (art. 6.1.b) + obligation legale Qualiopi (art. 6.1.c) |
| **Categories de personnes** | Formateurs (salaries et independants) |
| **Donnees collectees** | Nom, prenom, email, telephone, CV, diplomes, certifications, RC Pro, contrat/bon de commande |
| **Source** | Saisie manuelle par l'admin |
| **Destinataires internes** | Responsable pedagogique, admin |
| **Destinataires externes** | Auditeur Qualiopi (lors des audits) |
| **Transfert hors UE** | Non |
| **Duree de conservation** | 5 ans apres la fin de la collaboration |
| **Mesures de securite** | Acces restreint aux admins, fichiers stockes sur serveur securise |

---

## Traitement 3 — Gestion commerciale et facturation

| Champ | Detail |
|-------|--------|
| **Finalite** | Prospection, devis, conventions, facturation, suivi paiements |
| **Base legale** | Execution du contrat (art. 6.1.b) + obligation legale comptable (art. 6.1.c) |
| **Categories de personnes** | Clients (individuels et entreprises B2B), contacts OPCO |
| **Donnees collectees** | Nom, prenom, email, telephone, adresse, SIRET (entreprises), donnees de facturation |
| **Source** | Formulaire de contact, CRM (Odoo) |
| **Destinataires internes** | Direction, comptabilite |
| **Destinataires externes** | Expert comptable, OPCO (factures) |
| **Transfert hors UE** | Non (Odoo.sh heberge en EU) |
| **Duree de conservation** | 10 ans (obligation comptable) |
| **Mesures de securite** | Odoo.sh securise (HTTPS, auth, logs), acces restreint |

---

## Traitement 4 — Suivi de l'assiduite (emargement e-learning)

| Champ | Detail |
|-------|--------|
| **Finalite** | Preuve de realisation de la formation (Qualiopi indicateur 9), facturation OPCO |
| **Base legale** | Obligation legale (art. 6.1.c) — Code du travail, Qualiopi |
| **Categories de personnes** | Apprenants |
| **Donnees collectees** | Logs de connexion (date, heure debut, heure fin, duree, modules accedes) |
| **Source** | Plateforme LMS (OpenEdX — tracking automatique) |
| **Destinataires internes** | Formateurs, admin |
| **Destinataires externes** | OPCO, auditeur Qualiopi |
| **Transfert hors UE** | Non |
| **Duree de conservation** | 5 ans (Qualiopi) |
| **Mesures de securite** | Donnees dans la base MySQL du LMS, acces par role |

---

## Traitement 5 — Enquetes de satisfaction

| Champ | Detail |
|-------|--------|
| **Finalite** | Mesure de la qualite des formations, amelioration continue (Qualiopi indicateurs 12, 13, 31) |
| **Base legale** | Interet legitime (art. 6.1.f) — amelioration du service |
| **Categories de personnes** | Apprenants, anciens apprenants |
| **Donnees collectees** | Reponses aux questionnaires (notes, commentaires texte libres), NPS |
| **Source** | Formulaires en ligne (app Qualiopi) |
| **Destinataires internes** | Responsable qualite, formateurs |
| **Destinataires externes** | Auditeur Qualiopi (synthese anonymisee) |
| **Transfert hors UE** | Non |
| **Duree de conservation** | 5 ans |
| **Mesures de securite** | Acces restreint, donnees anonymisees dans les syntheses publiques |

---

## Traitement 6 — Chat support (WeWill)

| Champ | Detail |
|-------|--------|
| **Finalite** | Assistance et support technique aux apprenants et prospects |
| **Base legale** | Interet legitime (art. 6.1.f) — support client |
| **Categories de personnes** | Visiteurs du site, apprenants, prospects |
| **Donnees collectees** | Nom (si fourni), email (si fourni), messages de conversation, adresse IP |
| **Source** | Widget chat WeWill sur le site |
| **Destinataires internes** | Equipe support |
| **Destinataires externes** | Aucun |
| **Transfert hors UE** | Non (WeWill self-hosted sur VPS OVH France) |
| **Duree de conservation** | 2 ans apres la derniere conversation |
| **Mesures de securite** | Serveur securise, HTTPS, acces par authentification |

---

## Traitement 7 — Cookies et analytics

| Champ | Detail |
|-------|--------|
| **Finalite** | Fonctionnement de la plateforme (authentification, session) |
| **Base legale** | Cookies strictement necessaires (exempt de consentement, art. 82 loi Informatique et Libertes) |
| **Categories de personnes** | Tous les utilisateurs du site |
| **Donnees collectees** | Cookies de session (sessionid), cookies de preferences (langue), CSRF token |
| **Source** | Navigateur web |
| **Destinataires** | Aucun (cookies internes uniquement) |
| **Transfert hors UE** | Non |
| **Duree de conservation** | Session (supprime a la fermeture du navigateur) ou 12 mois max |
| **Mesures de securite** | Cookies securises (Secure, HttpOnly), HTTPS uniquement |

**Note** : Mission Formations n'utilise PAS de cookies tiers (pas de Google Analytics, pas de Facebook Pixel, pas de tracking publicitaire). Seuls les cookies strictement necessaires au fonctionnement sont utilises.

---

## Traitement 8 — Reclamations

| Champ | Detail |
|-------|--------|
| **Finalite** | Gestion des reclamations clients (Qualiopi indicateur 32) |
| **Base legale** | Obligation legale (art. 6.1.c) — Qualiopi |
| **Categories de personnes** | Apprenants, entreprises clientes, formateurs |
| **Donnees collectees** | Nom, email, objet de la reclamation, historique des echanges, resolution |
| **Source** | Formulaire, chat, email |
| **Destinataires internes** | Responsable qualite |
| **Destinataires externes** | Auditeur Qualiopi |
| **Transfert hors UE** | Non |
| **Duree de conservation** | 5 ans |
| **Mesures de securite** | Registre interne securise, acces restreint |

---

## Sous-traitants (article 28 RGPD)

| Sous-traitant | Donnees traitees | Localisation | Garanties |
|---------------|-----------------|-------------|-----------|
| **OVH** | Hebergement de toutes les donnees (VPS) | France (Roubaix/Gravelines) | ISO 27001, SOC 1/2/3, HDS, DPA signe |
| **Odoo SA** (Odoo.sh) | Donnees commerciales et facturation | Belgique (EU) | RGPD EU, DPA inclus dans les CGU |
| **Stripe** (si paiement CB) | Donnees de paiement | Irlande (EU) | PCI-DSS, RGPD EU, DPA disponible |
| **SMTP Provider** (si emails) | Adresses email des destinataires | A verifier | A verifier |

**Chaque sous-traitant doit avoir un DPA (Data Processing Agreement) archive.**

---

## Droits des personnes

| Droit | Comment l'exercer | Delai de reponse |
|-------|-------------------|-----------------|
| **Acces** | Email a dpo@missionformations.com | 30 jours |
| **Rectification** | Email ou modification directe dans le profil | 30 jours |
| **Effacement** | Email a dpo@missionformations.com | 30 jours (sauf obligation legale de conservation) |
| **Portabilite** | Export CSV des donnees sur demande | 30 jours |
| **Opposition** | Email a dpo@missionformations.com | 30 jours |
| **Limitation** | Email a dpo@missionformations.com | 30 jours |

### Procedure de suppression des donnees

```
1. Demande recue par email
2. Verification de l'identite du demandeur
3. Suppression dans OpenEdX (commande retire_user)
4. Suppression dans Odoo (anonymisation des donnees)
5. Suppression dans WeWill (suppression des conversations)
6. Confirmation par email au demandeur
7. Delai : 30 jours maximum
```

**Exception** : les donnees necessaires a la conformite Qualiopi (attestations, emargement) et a la comptabilite (factures) ne peuvent pas etre supprimees avant l'expiration du delai legal de conservation.

---

## Notification de violation (article 33 RGPD)

En cas de violation de donnees personnelles :

| Etape | Delai | Action |
|-------|-------|--------|
| 1 | Immediat | Identifier la violation (type, ampleur, donnees concernees) |
| 2 | < 72h | Notifier la CNIL (https://notifications.cnil.fr/) |
| 3 | < 72h | Notifier les personnes concernees si risque eleve |
| 4 | < 7 jours | Documenter l'incident (cause, mesures prises, prevention) |

### Contact CNIL
- Site : https://www.cnil.fr/
- Notification : https://notifications.cnil.fr/
- Telephone : 01 53 73 22 22

---

## Mise a jour du registre

Ce registre doit etre mis a jour :
- A chaque nouveau traitement de donnees
- A chaque changement de sous-traitant
- A chaque modification significative d'un traitement existant
- Au minimum une fois par an (revue annuelle)
