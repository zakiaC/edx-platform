# Cahier des charges — Module Qualiopi Mission Formations

> Version 1.0 — 19 mars 2026
> Objectif : specification complete du module Qualiopi externalise (app Django separee)

---

## PARTIE 1 — DOCUMENTS A GENERER (PDFs brandes Mission Formations)

### Charte graphique commune a tous les documents

| Element | Valeur |
|---------|--------|
| Logo | Logo Mission Formations (header gauche) |
| Couleur principale | Bleu MF (#1a1a2e ou selon charte) |
| Couleur secondaire | Vert MF (#16a085 ou selon charte) |
| Couleur texte | Dark (#2c3e50) |
| Police titre | Montserrat Bold (ou equivalent PDF) |
| Police corps | Open Sans Regular (ou equivalent PDF) |
| Footer | "Mission Formations — Organisme de formation certifie Qualiopi" + N° SIRET + N° DA + adresse + page X/Y |
| Header | Logo gauche + nom du document centre + date droite |
| Filigrane | Optionnel : "CONFIDENTIEL" sur certains documents |
| Format | A4 portrait (sauf emargement = paysage) |
| Marge | 2 cm tous cotes |

---

### DOC-01 : Programme de formation

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 1, 5, 7, 15 |
| **Declenchement** | Manuel (admin) depuis le dashboard Qualiopi |
| **Source donnees** | Structure OLX du cours (chapters, sequentials) + metadonnees Studio |
| **Destinataire** | Apprenant, employeur, OPCO, auditeur |

**Contenu obligatoire :**
- Intitule de la formation
- Objectifs pedagogiques (liste)
- Public vise et prerequis
- Duree totale (heures) et modalites (presentiel / distanciel / mixte)
- Programme detaille (modules, chapitres, contenus par section)
- Methodes pedagogiques utilisees (videos, quiz, masterclass, visio, etc.)
- Moyens techniques (plateforme LMS, outils)
- Modalites d'evaluation (QCM, exercices, cas pratiques, examen final)
- Modalites de suivi (tracking LMS, points intermediaires)
- Profil du/des formateur(s)
- Tarif (HT et TTC)
- Dates de session (si applicable)
- Delai d'acces
- Accessibilite handicap (referent + adaptations possibles)
- Contact et coordonnees

---

### DOC-02 : Convention de formation (B2B entreprise)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 5, 7, 8 |
| **Declenchement** | Manuel (admin) pour chaque entreprise/academie B2B |
| **Source donnees** | Academy (modele existant) + formation + apprenants inscrits |
| **Destinataire** | Entreprise cliente, OPCO |

**Contenu obligatoire :**
- Numero de convention unique (auto-genere)
- Entre : Mission Formations (SIRET, N° DA, adresse) ET l'entreprise (raison sociale, SIRET, adresse, representant)
- Intitule de la formation
- Objectifs (repris du programme)
- Duree, dates, horaires
- Lieu (plateforme LMS pour distanciel, adresse pour presentiel)
- Nombre de stagiaires (liste nominative en annexe)
- Prix total HT/TTC + modalites de paiement
- Modalites de reglement (OPCO, virement, echeancier)
- Delai de retractation (14 jours)
- Conditions d'annulation et de report
- Obligations des parties
- Signature + cachet des deux parties
- Date et lieu de signature

---

### DOC-03 : Contrat de formation (individuel / CPF)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 5, 7, 8 |
| **Declenchement** | Manuel (admin) pour chaque apprenant individuel |
| **Source donnees** | User OpenEdX + formation + enrollment |
| **Destinataire** | Apprenant individuel |

**Contenu obligatoire :**
- Entre : Mission Formations ET le stagiaire (nom, prenom, adresse, email)
- Intitule et objectifs de la formation
- Duree, dates, modalites
- Prix TTC + modalites de paiement
- Delai de retractation (14 jours, article L.6353-5 Code du travail)
- Conditions generales de vente (en annexe ou au verso)
- Signature des deux parties

---

### DOC-04 : Convocation du stagiaire

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 9 |
| **Declenchement** | Manuel (admin) — apres confirmation inscription/paiement |
| **Source donnees** | User + formation + dates + lieu |
| **Destinataire** | Apprenant (par email + PDF joint) |

**Contenu obligatoire :**
- Nom et prenom du stagiaire
- Intitule de la formation
- Dates et horaires
- Lieu (URL plateforme pour distanciel, adresse pour presentiel)
- Identifiants de connexion (ou lien d'activation)
- Documents a fournir (piece d'identite, etc.)
- Contact support technique
- Plan d'acces (presentiel) ou guide de connexion (distanciel)
- Rappel du reglement interieur (en annexe ou lien)

---

### DOC-05 : Reglement interieur

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 9, 15, 16 |
| **Declenchement** | Document statique (genere une fois, mis a jour annuellement) |
| **Source donnees** | Texte redige par l'admin |
| **Destinataire** | Tous les apprenants (affiche sur le site + joint a la convocation) |

**Contenu obligatoire (articles du Code du travail L.6352-3 et R.6352-1) :**
- Article 1 : Objet et champ d'application
- Article 2 : Conditions d'acces a la formation (distanciel : equipement, connexion)
- Article 3 : Assiduite, ponctualite, participation
- Article 4 : Absence et retard (procedure de signalement)
- Article 5 : Comportement et discipline
- Article 6 : Utilisation du materiel et de la plateforme LMS
- Article 7 : Propriete intellectuelle (contenus de formation)
- Article 8 : Confidentialite et RGPD
- Article 9 : Sanctions disciplinaires (avertissement, exclusion)
- Article 10 : Procedure disciplinaire (entretien, notification)
- Article 11 : Representation des stagiaires (si sessions > 500h)
- Article 12 : Reclamations (procedure, delai, contact)
- Article 13 : Hygiene et securite (presentiel)
- Article 14 : Responsabilite
- Article 15 : Entree en vigueur et modification
- Date d'entree en vigueur + signature du responsable

---

### DOC-06 : Feuille d'emargement / Attestation de presence

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 9, 11 |
| **Declenchement** | Manuel (admin/formateur) — par session ou par mois |
| **Format** | **Paysage** (tableau large) |
| **Source donnees** | Logs de connexion OpenEdX (StudentModule, tracking) |
| **Destinataire** | OPCO, auditeur, employeur |

**Contenu obligatoire :**
- Intitule de la formation
- Nom du formateur
- Dates de la periode couverte
- **Tableau :**
  - Colonne 1 : Nom et prenom du stagiaire
  - Colonnes suivantes : dates/creneaux (matin/apres-midi ou sessions)
  - Cellules : duree de connexion ou signature
- Pour le e-learning : remplacement de la signature par les **logs de connexion** (heure de debut, heure de fin, duree, modules accedes)
- Total d'heures par stagiaire
- Signature du formateur
- Mention legale : "Emargement genere automatiquement a partir des logs de connexion de la plateforme LMS"

---

### DOC-07 : Attestation de fin de formation

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 11, 32 |
| **Declenchement** | Manuel (admin/formateur) — quand l'apprenant a termine |
| **Source donnees** | Grades, certificates, progression OpenEdX |
| **Destinataire** | Apprenant, employeur, OPCO |

**Contenu obligatoire (article L.6353-1 Code du travail) :**
- Nom et prenom du stagiaire
- Intitule de la formation
- Dates de debut et de fin
- Duree totale (heures)
- Objectifs de la formation
- Nature de l'action (adaptation, qualification, etc.)
- Resultats de l'evaluation des acquis (note, mention, competences validees)
- Mention "a suivi avec assiduite" ou "a suivi partiellement"
- Signature du responsable de l'organisme
- Cachet de l'organisme
- **Existe deja** dans `pdf_reports.py` → a migrer et enrichir

---

### DOC-08 : Certificat de realisation

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 11 |
| **Declenchement** | Manuel (admin) — obligatoire pour OPCO/CPF |
| **Source donnees** | Enrollment + completion + dates reelles |
| **Destinataire** | OPCO, France Competences, Caisse des Depots (CPF) |

**Contenu obligatoire (modele Caisse des Depots) :**
- Intitule de la formation
- Objectif de l'action de formation
- Nature de l'action (article L.6313-1)
- Duree prevue vs duree realisee
- Dates de debut et de fin
- Modalites de deroulement (presentiel, distanciel, mixte)
- Nom et prenom du stagiaire
- Nom de l'organisme de formation + N° DA
- Signature du responsable
- **Format impose** par la Caisse des Depots (template specifique)

---

### DOC-09 : Evaluation pre-formation (positionnement)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 5, 6 |
| **Declenchement** | Manuel (admin) envoye avant le debut de la formation |
| **Source donnees** | Formulaire rempli par l'apprenant |
| **Destinataire** | Admin, formateur, dossier apprenant |

**Contenu :**
- Nom et prenom du stagiaire
- Intitule de la formation
- Date
- Questions de positionnement (QCM ou echelle 1-5) :
  - Niveau de connaissance du sujet
  - Experience professionnelle liee
  - Attentes specifiques
  - Objectifs personnels
  - Contraintes (handicap, horaires, materiel)
- Score de positionnement (automatique)
- Recommandation d'adaptation du parcours

---

### DOC-10 : Evaluation post-formation (acquis)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 11 |
| **Declenchement** | Manuel (admin/formateur) en fin de formation |
| **Source donnees** | Resultats quiz OpenEdX + formulaire complementaire |
| **Destinataire** | Apprenant, employeur, dossier |

**Contenu :**
- Memes questions que l'eval pre-formation (pour mesurer la progression)
- Grille de competences acquises (acquis / en cours / non acquis)
- Note globale / score
- Comparaison avant/apres (graphique radar si possible)
- Commentaire du formateur
- Signature formateur + stagiaire

---

### DOC-11 : Enquete de satisfaction a chaud

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 12, 31 |
| **Declenchement** | Manuel (admin) en fin de session — lien envoye par email |
| **Source donnees** | Formulaire rempli par l'apprenant (dans le dashboard apprenant) |
| **Destinataire** | Admin, formateur, auditeur (synthese) |

**Contenu du formulaire :**
- Satisfaction globale (1-5 etoiles)
- Qualite du contenu pedagogique (1-5)
- Qualite de l'animation / du formateur (1-5)
- Qualite des supports (1-5)
- Qualite de la plateforme LMS (1-5)
- Adequation avec les objectifs annonces (1-5)
- Rythme de la formation (trop lent / adapte / trop rapide)
- Recommanderiez-vous cette formation ? (NPS 0-10)
- Points forts (texte libre)
- Points a ameliorer (texte libre)
- Commentaire libre

**PDF de synthese (pour l'auditeur) :**
- Taux de retour (objectif > 80%)
- Moyennes par critere
- NPS global
- Nuage de mots des commentaires
- Graphiques (barres, radar)

---

### DOC-12 : Enquete de satisfaction a froid (3-6 mois)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 13, 31 |
| **Declenchement** | Manuel (admin) — 3 a 6 mois apres la fin de la formation |
| **Source donnees** | Formulaire envoye par email |
| **Destinataire** | Admin, auditeur (synthese) |

**Contenu du formulaire :**
- La formation a-t-elle repondu a vos attentes ? (1-5)
- Avez-vous pu mettre en pratique les acquis ? (oui/partiellement/non)
- Impact sur votre activite professionnelle (1-5)
- Avez-vous eu besoin de formation complementaire ?
- Situation professionnelle actuelle (si applicable : emploi, evolution, etc.)
- Suggestions d'amelioration
- Recommanderiez-vous cette formation ? (NPS 0-10)

**PDF de synthese** : memes principes que l'enquete a chaud

---

### DOC-13 : Rapport de suivi pedagogique

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 9, 10, 11, 17 |
| **Declenchement** | Manuel (admin/formateur) — periodique ou a la demande |
| **Source donnees** | Progression OpenEdX (StudentModule, grades, completion) |
| **Destinataire** | Employeur (B2B), OPCO, auditeur |

**Contenu :**
- Intitule de la formation
- Periode couverte
- Formateur(s)
- **Par stagiaire :**
  - Progression globale (%)
  - Modules completes / total
  - Temps passe (heures)
  - Notes aux evaluations
  - Assiduite (connexions)
- **Statistiques globales :**
  - Taux de completion moyen
  - Taux de reussite
  - Note moyenne
  - Taux d'assiduite
- Observations du formateur
- Actions correctives si necessaire
- **Existe deja** dans `pdf_reports.py` → a migrer et enrichir

---

### DOC-14 : Bilan de formation (dossier complet)

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 29, 30 |
| **Declenchement** | Manuel (admin) — en fin de session pour chaque formation |
| **Format** | **ZIP** contenant tous les PDFs ci-dessous |
| **Destinataire** | OPCO, financeur, auditeur |

**Contenu du ZIP :**
- Programme de formation (DOC-01)
- Convention ou contrat (DOC-02 ou DOC-03)
- Liste des stagiaires (CSV + PDF)
- Feuilles d'emargement (DOC-06)
- Attestations de fin de formation (DOC-07, une par stagiaire)
- Certificats de realisation (DOC-08, un par stagiaire)
- Resultats des evaluations pre/post (DOC-09, DOC-10)
- Synthese satisfaction a chaud (DOC-11)
- Rapport de suivi pedagogique (DOC-13)
- Bilan financier (recettes, cout formateur, marge)
- Note de synthese globale (texte redige par l'admin)

---

### DOC-15 : Livret d'accueil du stagiaire

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 1, 4, 9, 15 |
| **Declenchement** | Manuel (admin) — joint a la convocation ou accessible en ligne |
| **Source donnees** | Texte statique + donnees dynamiques (formation, dates) |
| **Destinataire** | Apprenant |

**Contenu :**
- Mot de bienvenue du responsable pedagogique
- Presentation de Mission Formations
- Presentation de la formation (objectifs, programme resume)
- Modalites pratiques (connexion plateforme, horaires, contact support)
- Reglement interieur (resume ou lien)
- Referent handicap (nom, contact, procedure d'adaptation)
- Referent pedagogique (nom, contact)
- Procedure de reclamation
- Charte informatique / RGPD
- FAQ

---

### DOC-16 : Attestation d'assiduite

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 9 |
| **Declenchement** | Manuel (admin) — pour les financeurs qui exigent ce document specifique |
| **Source donnees** | Logs de connexion + progression |
| **Destinataire** | OPCO, Mission Locale, Pole Emploi |

**Contenu :**
- Nom et prenom du stagiaire
- Intitule de la formation
- Dates de debut et de fin
- Duree prevue vs duree realisee (heures)
- Taux d'assiduite (%) calcule depuis les logs de connexion
- Mention : "atteste que le stagiaire a suivi la formation avec une assiduite de X%"
- Signature du responsable

---

### DOC-17 : PV de reunion pedagogique

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 23 |
| **Declenchement** | Manuel (admin) — apres chaque reunion (min 2/an) |
| **Source donnees** | Formulaire rempli par l'admin |
| **Destinataire** | Equipe, auditeur |

**Contenu :**
- Date, heure, lieu (ou visio)
- Participants (liste nominative + fonction)
- Ordre du jour
- Points abordes (texte structure)
- Decisions prises
- Actions a mener (responsable + echeance)
- Date de la prochaine reunion
- Signature du responsable pedagogique

---

### DOC-18 : Fiche formateur

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 20, 21, 22 |
| **Declenchement** | Manuel (admin) — a la creation/mise a jour du profil formateur |
| **Source donnees** | Formulaire + uploads (CV, diplomes) |
| **Destinataire** | Auditeur, dossier interne |

**Contenu :**
- Photo (optionnel)
- Nom, prenom, statut (salarie, independant, sous-traitant)
- Domaines d'expertise
- Formations enseignees chez Mission Formations
- CV synthetique (parcours, experience)
- Diplomes et certifications (liste + copies jointes)
- Attestation de formation continue (actions suivies dans l'annee)
- RC Pro (si independant)
- Contrat ou bon de commande (si sous-traitant, Ind. 21)
- Date de derniere mise a jour

---

### DOC-19 : Convention de sous-traitance

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 19, 21 |
| **Declenchement** | Manuel (admin) — pour chaque sous-traitant |
| **Source donnees** | Formulaire |
| **Destinataire** | Sous-traitant, auditeur |

**Contenu :**
- Entre : Mission Formations ET le sous-traitant
- Objet (formations confiees)
- Obligations du sous-traitant (qualite, respect programme, reporting)
- Obligations de Mission Formations (moyens, remuneration)
- Confidentialite et RGPD
- Assurance RC Pro
- Duree et conditions de resiliation
- Tarification
- Signatures

---

### DOC-20 : Recepisse de reclamation

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 32 |
| **Declenchement** | Automatique a la saisie d'une reclamation dans le registre |
| **Source donnees** | Modele Reclamation |
| **Destinataire** | Reclamant (apprenant, employeur, formateur) |

**Contenu :**
- Numero de reclamation (auto-genere)
- Date de reception
- Identite du reclamant
- Objet de la reclamation (resume)
- Responsable du traitement
- Delai de reponse engage (max 30 jours)
- Contact pour le suivi
- Signature du responsable qualite

---

### DOC-21 : Plan d'amelioration annuel

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 30 |
| **Declenchement** | Manuel (admin) — annuel |
| **Source donnees** | Formulaire structure |
| **Destinataire** | Direction, auditeur |

**Contenu :**
- Annee de reference
- Bilan de l'annee precedente (actions prevues vs realisees)
- Indicateurs de pilotage (taux satisfaction, taux reussite, taux abandon, NPS)
- Non-conformites identifiees
- Actions correctives planifiees (description, responsable, echeance)
- Objectifs qualite pour l'annee suivante
- Budget qualite
- Signature de la direction

---

### DOC-22 : Revue de direction

| Champ | Description |
|-------|-------------|
| **Indicateurs Qualiopi** | 30 |
| **Declenchement** | Manuel (admin) — annuel (minimum) |
| **Source donnees** | Agregation de toutes les donnees Qualiopi |
| **Destinataire** | Direction, auditeur |

**Contenu :**
- Date de la revue
- Participants
- Donnees d'entree :
  - Resultats des audits internes
  - Retours clients (satisfaction a chaud + a froid)
  - Reclamations (nombre, types, delais)
  - Indicateurs de performance (taux reussite, completion, abandon)
  - Etat des actions correctives precedentes
  - Evolutions reglementaires
- Decisions prises
- Plan d'actions
- Prochaine revue planifiee
- Signature de la direction

---

## RECAPITULATIF DES 22 DOCUMENTS

| # | Document | Format | Pages | Declenchement | Frequence |
|---|----------|--------|-------|---------------|-----------|
| DOC-01 | Programme de formation | PDF portrait | 2-4 | Manuel | Par formation |
| DOC-02 | Convention de formation B2B | PDF portrait | 3-5 | Manuel | Par entreprise × formation |
| DOC-03 | Contrat de formation individuel | PDF portrait | 2-3 | Manuel | Par apprenant individuel |
| DOC-04 | Convocation stagiaire | PDF portrait | 1-2 | Manuel | Par apprenant × formation |
| DOC-05 | Reglement interieur | PDF portrait | 3-5 | Annuel | 1 fois/an |
| DOC-06 | Feuille d'emargement | PDF **paysage** | 1-3 | Manuel | Par session/mois |
| DOC-07 | Attestation de fin de formation | PDF portrait | 1 | Manuel | Par apprenant |
| DOC-08 | Certificat de realisation | PDF portrait | 1 | Manuel | Par apprenant (OPCO/CPF) |
| DOC-09 | Evaluation pre-formation | PDF portrait | 2 | Manuel | Par apprenant |
| DOC-10 | Evaluation post-formation | PDF portrait | 2 | Manuel | Par apprenant |
| DOC-11 | Enquete satisfaction a chaud | Formulaire + PDF synthese | 2-3 | Manuel | Par session |
| DOC-12 | Enquete satisfaction a froid | Formulaire + PDF synthese | 2-3 | Manuel | 3-6 mois apres |
| DOC-13 | Rapport de suivi pedagogique | PDF portrait | 3-6 | Manuel | Periodique |
| DOC-14 | Bilan de formation | **ZIP** | N/A | Manuel | Par session terminee |
| DOC-15 | Livret d'accueil stagiaire | PDF portrait | 4-8 | Manuel | Par formation |
| DOC-16 | Attestation d'assiduite | PDF portrait | 1 | Manuel | Par apprenant (OPCO) |
| DOC-17 | PV reunion pedagogique | PDF portrait | 2-3 | Manuel | Min 2/an |
| DOC-18 | Fiche formateur | PDF portrait | 2-3 | Manuel | Par formateur |
| DOC-19 | Convention de sous-traitance | PDF portrait | 3-4 | Manuel | Par sous-traitant |
| DOC-20 | Recepisse de reclamation | PDF portrait | 1 | Auto (saisie registre) | Par reclamation |
| DOC-21 | Plan d'amelioration annuel | PDF portrait | 3-5 | Manuel | Annuel |
| DOC-22 | Revue de direction | PDF portrait | 4-6 | Manuel | Annuel |

---

## PARTIE 2 — LES 32 INDICATEURS ET LEUR IMPLEMENTATION

### Critere 1 — Information du public (Ind. 1-4)

#### Ind. 1 — Conditions d'acces precises

| Element | Implementation |
|---------|---------------|
| **Preuve** | Page catalogue du site + DOC-01 (programme) |
| **Dans le dashboard** | Checklist auto : tarifs presents ? prerequis ? delais ? modalites ? |
| **Verification** | Script qui scanne les pages publiques et verifie la presence des infos |
| **Statut** | Vert (tout present) / Orange (partiel) / Rouge (manquant) |
| **Action admin** | Bouton "Voir la page publique" + bouton "Generer le programme PDF" |

#### Ind. 2 — Delais d'acces communiques

| Element | Implementation |
|---------|---------------|
| **Preuve** | Delai affiche sur le site + delai reel calcule |
| **Dans le dashboard** | Champ configurable "Delai moyen d'acces" (ex: "15 jours") |
| **Verification auto** | Calcul du delai reel moyen (date demande → date debut formation) depuis les enrollments |
| **Statut** | Vert (delai affiche = delai reel +/- 5j) / Orange / Rouge |

#### Ind. 3 — Indicateurs de resultats publies

| Element | Implementation |
|---------|---------------|
| **Preuve** | KPIs affiches sur le site public |
| **Dans le dashboard** | Calcul automatique depuis OpenEdX : |
| | - Taux de satisfaction (depuis enquetes DOC-11) |
| | - Taux de reussite (depuis grades/certificates) |
| | - Taux d'insertion (depuis enquetes DOC-12) |
| **Verification** | Date de derniere MAJ < 12 mois |
| **Action admin** | Bouton "Publier les indicateurs sur le site" |

#### Ind. 4 — Accessibilite handicap

| Element | Implementation |
|---------|---------------|
| **Preuve** | Referent identifie + procedure documentee |
| **Dans le dashboard** | Formulaire : nom referent, email, telephone, procedure d'adaptation |
| **Verification** | Champs remplis = Vert / vides = Rouge |
| **Action admin** | Bouton "Publier sur le site" |

---

### Critere 2 — Analyse des besoins (Ind. 5-8)

#### Ind. 5 — Analyse des besoins realisee

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-09 (eval pre-formation) ou entretien trace |
| **Dans le dashboard** | Par apprenant : statut "Recueil des besoins" (fait/non fait) |
| **KPI** | % d'apprenants avec recueil complete (objectif 100%) |
| **Action admin** | Bouton "Envoyer le questionnaire de besoins" |

#### Ind. 6 — Prerequis verifies

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-09 (evaluation pre-formation) + grille de prerequis |
| **Dans le dashboard** | Par apprenant : statut "Prerequis verifies" (oui/non) |
| **KPI** | % d'apprenants avec prerequis verifies (objectif 100%) |

#### Ind. 7 — Parcours adapte

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-02 ou DOC-03 (convention/contrat) avec objectifs individualises |
| **Dans le dashboard** | Par apprenant : convention signee ? objectifs personnalises ? |
| **Action admin** | Bouton "Generer la convention" (DOC-02 ou DOC-03) |

#### Ind. 8 — Objectifs definis avec le beneficiaire

| Element | Implementation |
|---------|---------------|
| **Preuve** | Signature du beneficiaire sur les objectifs |
| **Dans le dashboard** | Par apprenant : document signe uploade ? |
| **Action admin** | Upload du document signe (scan ou signature electronique) |

---

### Critere 3 — Suivi et evaluation (Ind. 9-14)

#### Ind. 9 — Realisation suivie et tracee

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-06 (feuille d'emargement) |
| **Dans le dashboard** | Bouton "Generer l'emargement" par formation/periode |
| **Donnees auto** | Logs de connexion OpenEdX (StudentModule, tracking) |
| **KPI** | 100% des sessions avec feuille d'emargement |

#### Ind. 10 — Mecanismes d'adaptation

| Element | Implementation |
|---------|---------------|
| **Preuve** | Compte-rendu de point intermediaire |
| **Dans le dashboard** | Formulaire "Point de suivi" : date, participants, constats, ajustements |
| **KPI** | Min 1 point intermediaire par formation > 2 jours |

#### Ind. 11 — Acquis evalues

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-10 (eval post-formation) + resultats quiz OpenEdX |
| **Dans le dashboard** | Resultats automatiques depuis les grades OpenEdX |
| **KPI** | 100% des apprenants avec evaluation des acquis |
| **Action admin** | Bouton "Generer l'attestation" (DOC-07) |

#### Ind. 12 — Satisfaction a chaud

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-11 (enquete satisfaction) |
| **Dans le dashboard** | Taux de retour + resultats agreges |
| **KPI** | Taux de retour > 80% |
| **Action admin** | Bouton "Envoyer l'enquete" (email avec lien formulaire) |

#### Ind. 13 — Suivi post-formation

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-12 (enquete a froid) |
| **Dans le dashboard** | Liste des formations a evaluer (3-6 mois apres fin) |
| **KPI** | Taux de reponse > 50% |
| **Alerte** | Notification quand une formation arrive a 3 mois post-fin |

#### Ind. 14 — Abandons geres

| Element | Implementation |
|---------|---------------|
| **Preuve** | Registre des abandons |
| **Dans le dashboard** | Detection auto d'inactivite (> 30 jours sans connexion) |
| **Donnees auto** | Derniere connexion depuis OpenEdX |
| **Donnees manuelles** | Cause de l'abandon, plan de remediation, signalement OPCO |
| **KPI** | Taux d'abandon < 15% |
| **Alerte** | Notification quand un apprenant est inactif > 15 jours |

---

### Critere 4 — Moyens pedagogiques (Ind. 15-19)

#### Ind. 15 — Moyens adaptes

| Element | Implementation |
|---------|---------------|
| **Preuve** | Inventaire des supports + dates de MAJ |
| **Dans le dashboard** | Liste des formations avec date de derniere MAJ du contenu |
| **Donnees auto** | Date de modification du cours dans Studio |
| **KPI** | 100% des supports mis a jour < 2 ans |
| **Alerte** | Notification si un cours n'a pas ete MAJ depuis > 18 mois |

#### Ind. 16 — Environnement numerique securise

| Element | Implementation |
|---------|---------------|
| **Preuve** | Registre RGPD, politique confidentialite, DPO identifie |
| **Dans le dashboard** | Checklist : DPO ? Registre ? Politique publiee ? Support technique ? |
| **Statut** | Vert (tout coche) / Rouge |

#### Ind. 17 — Encadrement suffisant

| Element | Implementation |
|---------|---------------|
| **Preuve** | Planning formateurs + ratio |
| **Dans le dashboard** | Calcul auto : nb inscrits / nb formateurs par formation |
| **Donnees auto** | CourseEnrollment + CourseAccessRole (instructor) |
| **KPI** | Ratio max 1/15 (presentiel) ou 1/20 (distanciel) |
| **Alerte** | Si ratio depasse le seuil |

#### Ind. 18 — Locaux conformes

| Element | Implementation |
|---------|---------------|
| **Preuve** | Fiche locaux (bail, accessibilite PMR, equipements) |
| **Dans le dashboard** | Formulaire + upload documents |
| **Statut** | Applicable uniquement si presentiel/hybride |

#### Ind. 19 — Sous-traitants encadres

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-19 (convention sous-traitance) + registre |
| **Dans le dashboard** | CRUD sous-traitants avec statut contrat (signe/en attente/expire) |
| **KPI** | 100% des sous-traitants avec contrat signe avant intervention |

---

### Critere 5 — Qualification formateurs (Ind. 20-23)

#### Ind. 20 — Competences requises

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-18 (fiche formateur) |
| **Dans le dashboard** | CRUD formateurs avec CV, diplomes, certifications |
| **KPI** | 100% des CV mis a jour < 2 ans |
| **Alerte** | Notification si un CV date de > 18 mois |

#### Ind. 21 — Intervenants exterieurs qualifies

| Element | Implementation |
|---------|---------------|
| **Preuve** | Contrat + bon de commande + RC Pro |
| **Dans le dashboard** | CRUD intervenants avec upload documents |
| **KPI** | 100% avec bon de commande AVANT formation |

#### Ind. 22 — Plan de dev competences formateurs

| Element | Implementation |
|---------|---------------|
| **Preuve** | Plan de formation annuel + attestations |
| **Dans le dashboard** | CRUD actions de formation par formateur |
| **KPI** | Min 1 action par formateur par an |

#### Ind. 23 — Coordination pedagogique

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-17 (PV reunion pedagogique) |
| **Dans le dashboard** | CRUD reunions avec upload CR |
| **KPI** | Min 2 reunions par an |
| **Alerte** | Notification si aucune reunion depuis > 5 mois |

---

### Critere 6 — Veille et environnement pro (Ind. 24-30)

#### Ind. 24 — Veille reglementaire

| Element | Implementation |
|---------|---------------|
| **Dans le dashboard** | Journal de veille : CRUD entrees (date, source, resume, impact) |
| **KPI** | Min 1 entree par trimestre |
| **Alerte** | Notification si aucune entree depuis > 80 jours |

#### Ind. 25 — Veille sectorielle

| Element | Implementation |
|---------|---------------|
| **Dans le dashboard** | Journal de veille par domaine de formation |
| **KPI** | Min 1 entree par domaine par an |

#### Ind. 26 — Veille pedagogique

| Element | Implementation |
|---------|---------------|
| **Dans le dashboard** | Registre evolutions pedagogiques (description, date, impact) |
| **KPI** | Min 1 evolution documentee par an |

#### Ind. 27 — Partenariats

| Element | Implementation |
|---------|---------------|
| **Dans le dashboard** | CRUD partenaires (nom, type, convention, date signature) |
| **KPI** | Min 1 partenariat formalise (convention signee) |

#### Ind. 28 — Resultats insertion

| Element | Implementation |
|---------|---------------|
| **Preuve** | Enquetes d'insertion a 6 mois |
| **Dans le dashboard** | Lien avec DOC-12 (enquete a froid) enrichie |
| **KPI** | Taux de reponse > 40%, resultats exploites annuellement |

#### Ind. 29 — Financeurs informes

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-14 (bilan de formation) envoye aux OPCO |
| **Dans le dashboard** | Par financeur : bilan envoye ? date ? accuse reception ? |
| **KPI** | Bilans transmis dans les delais |

#### Ind. 30 — Amelioration continue

| Element | Implementation |
|---------|---------------|
| **Preuve** | DOC-21 (plan amelioration) + DOC-22 (revue de direction) |
| **Dans le dashboard** | Formulaire annuel avec suivi des actions |
| **KPI** | Revue annuelle documentee |

---

### Critere 7 — Appreciations et reclamations (Ind. 31-32)

#### Ind. 31 — Appreciations recueillies

| Element | Implementation |
|---------|---------------|
| **Preuve** | Synthese satisfaction (a chaud + a froid + employeurs) |
| **Dans le dashboard** | Agregation automatique des DOC-11 et DOC-12 |
| **KPI** | Taux de satisfaction global calcule, diffuse, exploite |
| **Action admin** | Bouton "Generer la synthese annuelle satisfaction" |

#### Ind. 32 — Reclamations traitees

| Element | Implementation |
|---------|---------------|
| **Preuve** | Registre des reclamations + DOC-20 (recepisse) |
| **Dans le dashboard** | CRUD reclamations avec : |
| | - N° auto |
| | - Date reception |
| | - Reclamant |
| | - Objet |
| | - Responsable traitement |
| | - Date reponse |
| | - Statut (en cours / traite / clos) |
| | - Delai (calcule auto, alerte si > 30j) |
| **KPI** | 0 reclamation sans reponse > 30 jours |
| **Alerte** | Notification a J+20 si pas de reponse |

---

## PARTIE 3 — MODELES DJANGO NECESSAIRES

### Modeles pour les registres et formulaires

| Modele | Champs principaux | Indicateurs |
|--------|-------------------|-------------|
| `QualiopiConfig` | referent_handicap, dpo_name, delai_acces, politique_rgpd_url | 1, 2, 4, 16 |
| `RecueilBesoin` | apprenant, formation, date, questionnaire_json, score, statut | 5, 6 |
| `Convention` | numero, type (B2B/individuel), entreprise, formation, montant, statut_signature, pdf_url | 7, 8 |
| `Emargement` | formation, periode, donnees_json (logs), pdf_url, genere_le | 9 |
| `PointSuivi` | formation, date, participants, constats, ajustements | 10 |
| `EvaluationPrePost` | apprenant, formation, type (pre/post), reponses_json, score | 6, 11 |
| `EnqueteSatisfaction` | apprenant, formation, type (chaud/froid), reponses_json, nps, date | 12, 13, 31 |
| `AbandonLog` | apprenant, formation, date_detection, cause, remediation, signalement_opco | 14 |
| `FicheFormateur` | user, cv_url, diplomes_json, certifications, rc_pro_url, date_maj | 20, 21, 22 |
| `ActionFormationFormateur` | formateur, intitule, date, attestation_url | 22 |
| `ReunionPedagogique` | date, lieu, participants_json, ordre_jour, decisions, cr_url | 23 |
| `VeilleEntry` | type (reglementaire/sectorielle/pedagogique), date, source, resume, impact, domaine | 24, 25, 26 |
| `Partenariat` | nom, type, convention_url, date_signature | 27 |
| `EnqueteInsertion` | apprenant, formation, date_envoi, date_reponse, reponses_json, situation_pro | 28 |
| `BilanFinanceur` | financeur, formation, bilan_url, date_envoi, accuse_url | 29 |
| `PlanAmelioration` | annee, bilan_precedent, actions_json, objectifs_json | 30 |
| `RevueDirection` | date, participants, donnees_entree_json, decisions_json, actions_json | 30 |
| `Reclamation` | numero, date_reception, reclamant, objet, responsable, date_reponse, statut, delai | 32 |
| `SousTraitant` | nom, siret, contrat_url, rc_pro_url, qualifications, statut | 19 |
| `DocumentQualiopi` | type (DOC-01 a DOC-22), formation, apprenant, pdf_url, genere_le, version | Tous |

**Total : ~20 modeles**

---

## PARTIE 4 — DASHBOARD QUALIOPI (7 ONGLETS)

### Navigation

```
Qualiopi
├── Vue d'ensemble (scorecard 32 indicateurs : vert/orange/rouge)
├── C1 — Information du public
├── C2 — Analyse des besoins
├── C3 — Suivi et evaluation
├── C4 — Moyens pedagogiques
├── C5 — Qualification formateurs
├── C6 — Veille et environnement pro
└── C7 — Appreciations et reclamations
```

### Vue d'ensemble (page d'accueil Qualiopi)

- Scorecard visuelle : 32 indicateurs avec pastille couleur
  - Vert : conforme (preuve presente, KPI atteint)
  - Orange : partiel (preuve incomplete ou KPI proche du seuil)
  - Rouge : non conforme (preuve manquante ou KPI non atteint)
- KPIs globaux :
  - Taux de conformite global (% d'indicateurs verts)
  - Nombre de reclamations en cours
  - Prochaine echeance (reunion pedagogique, enquete a froid, etc.)
- Alertes actives (triees par urgence)
- Bouton "Generer le dossier auditeur" (ZIP complet)

### Chaque onglet critere contient

- Tableau des indicateurs du critere avec statut
- Formulaires de saisie des donnees manuelles
- Boutons de generation des PDFs concernes
- KPIs specifiques au critere
- Historique des actions (audit trail)
