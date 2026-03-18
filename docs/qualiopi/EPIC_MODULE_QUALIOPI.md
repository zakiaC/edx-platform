# Epic — Module Qualiopi Mission Formations

> Objectif : generer automatiquement TOUS les documents exiges par Qualiopi
> depuis le dashboard admin et formateur, pour chaque formation et chaque stagiaire.
> Inclut la documentation pour l'auditeur, l'admin et le formateur.

---

## 1. Contexte

### Qualiopi — ce qui est exige

Qualiopi impose 7 criteres (32 indicateurs). Les documents generables concernent :

| Indicateur | Document | Qui le genere | Pour qui |
|------------|----------|---------------|----------|
| **1** | Conditions generales de vente (CGV) | Admin | Client B2B |
| **2** | Catalogue de formations | Admin | Public / Auditeur |
| **4** | Programme detaille de formation | Admin / Formateur | Stagiaire / Auditeur |
| **6** | Convention de formation | Admin | Client B2B |
| **7** | Convocation du stagiaire | Admin | Stagiaire |
| **11** | Feuille d'emargement (presence) | Formateur | Auditeur |
| **12** | Evaluation des acquis (pre/post) | Formateur | Stagiaire / Auditeur |
| **17** | Suivi de progression | Formateur | Stagiaire / Auditeur |
| **19** | Enquete de satisfaction | Admin | Auditeur |
| **32** | Attestation de fin de formation | Admin | Stagiaire / Auditeur |

---

## 2. Documents a generer (10 types)

### 2.1 Attestation de fin de formation (indicateur 32)
- **Pour** : chaque stagiaire ayant termine une formation
- **Contenu** : organisme, stagiaire, formation, dates, duree, resultats, signature
- **Reference legale** : Code du travail L.6353-1, R.6353-1
- **Genere par** : admin ou formateur
- **Deja code** : oui (pdf_reports.py — a enrichir)

### 2.2 Programme detaille de formation (indicateur 4)
- **Pour** : chaque formation
- **Contenu** : objectifs pedagogiques, prerequis, public vise, contenu detaille par module, modalites d'evaluation, moyens pedagogiques, duree, tarif
- **Genere par** : admin
- **Donnees source** : CourseOverview + structure OLX (chapters, sequentials)

### 2.3 Convention de formation (indicateur 6)
- **Pour** : chaque inscription entreprise (B2B)
- **Contenu** : parties (organisme + client), formation concernee, dates, duree, lieu, effectif, prix, conditions de reglement, conditions d'annulation
- **Genere par** : admin
- **Donnees source** : Academy (B2B) + CourseOverview

### 2.4 Convocation du stagiaire (indicateur 7)
- **Pour** : chaque stagiaire inscrit
- **Contenu** : nom stagiaire, formation, dates, lieu (URL plateforme), informations pratiques, contact
- **Genere par** : admin ou formateur
- **Donnees source** : CourseEnrollment + CourseOverview

### 2.5 Feuille d'emargement (indicateur 11)
- **Pour** : chaque session de formation
- **Contenu** : date, formation, formateur, tableau nom/prenom/signature/heure arrivee/heure depart
- **Genere par** : formateur
- **Adaptation e-learning** : remplacee par les logs de connexion OpenEdX (temps passe par module)
- **Donnees source** : StudentModule (completion tracking)

### 2.6 Evaluation des acquis — pre-formation (indicateur 12)
- **Pour** : chaque stagiaire avant le debut de la formation
- **Contenu** : questionnaire de positionnement, niveau initial, objectifs personnels
- **Genere par** : formateur
- **Donnees source** : quiz diagnostique OLX (premier quiz du cours)

### 2.7 Evaluation des acquis — post-formation (indicateur 12)
- **Pour** : chaque stagiaire a la fin de la formation
- **Contenu** : resultats finaux, competences acquises, comparaison pre/post
- **Genere par** : formateur
- **Donnees source** : quiz final OLX + note globale

### 2.8 Rapport de suivi de progression (indicateur 17)
- **Pour** : un cours (tous les stagiaires) ou un stagiaire (tous ses cours)
- **Contenu** : tableau des apprenants, progression par module, notes, taux de completion
- **Genere par** : admin ou formateur
- **Deja code** : oui (pdf_reports.py — a enrichir)

### 2.9 Enquete de satisfaction (indicateur 19)
- **Pour** : chaque stagiaire ayant termine
- **Contenu** : questionnaire de satisfaction (5 criteres : contenu, pedagogie, formateur, plateforme, global), note /5, commentaire libre, synthese
- **Genere par** : admin
- **Donnees source** : a creer (modele SatisfactionSurvey)

### 2.10 Bilan de formation (synthese auditeur)
- **Pour** : une formation complete (bilan global)
- **Contenu** : toutes les stats consolidees, taux de completion, satisfaction moyenne, nombre de certifies, recommandations
- **Genere par** : admin
- **Usage** : presentation a l'auditeur Qualiopi

---

## 3. Tickets Jira

### QUA-1 : Modele de donnees Qualiopi
- **Type** : Tache technique
- **Priorite** : Haute
- **Estimation** : 3h
- **Description** :
  Creer les modeles Django :
  ```python
  class FormationProgram:
      """Programme detaille d'une formation."""
      course_key, objectives, prerequisites, target_audience,
      teaching_methods, evaluation_methods, duration_hours, price_ht

  class FormationConvention:
      """Convention de formation B2B."""
      academy, course_key, client_name, client_contact,
      start_date, end_date, num_seats, price_total, signed_at

  class SatisfactionSurvey:
      """Enquete de satisfaction post-formation."""
      user, course_key, rating_content, rating_pedagogy,
      rating_trainer, rating_platform, rating_global, comment, submitted_at

  class EmargementLog:
      """Log de presence e-learning (remplace la feuille papier)."""
      user, course_key, date, time_spent_minutes, modules_accessed
  ```
- **Migration** : 0003_qualiopi_models.py
- **Dependance** : aucune

---

### QUA-2 : Generateur PDF — Attestation de fin de formation
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 2h (enrichir l'existant)
- **Description** :
  - Enrichir `generate_attestation_pdf` existant
  - Ajouter : duree effective (depuis les logs), objectifs atteints, competences validees
  - Ajouter un QR code de verification (lien vers le certificat web OpenEdX)
  - Bouton "Telecharger attestation" dans le dashboard admin onglet Apprenants
  - Bouton "Generer les attestations" (bulk) pour tous les certifies d'un cours
- **Acces** : admin + formateur

---

### QUA-3 : Generateur PDF — Programme de formation
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 4h
- **Description** :
  - Generer le programme detaille depuis la structure OLX du cours
  - Extraire automatiquement : chapitres, sous-sections, types de contenus
  - Ajouter les champs manuels (objectifs, prerequis, public) depuis FormationProgram
  - Interface admin pour remplir les champs manquants
  - Bouton "Telecharger le programme" dans le dashboard formateur
- **Acces** : admin + formateur

---

### QUA-4 : Generateur PDF — Convention de formation B2B
- **Type** : Feature
- **Priorite** : Moyenne
- **Estimation** : 3h
- **Description** :
  - Generer la convention depuis les donnees Academy (B2B) + CourseOverview
  - Champs : parties, formation, dates, duree, effectif, prix, conditions
  - Bouton "Generer convention" dans Academy Manager onglet detail
  - Envoi par email au contact RH du client
- **Acces** : admin uniquement
- **Dependance** : QUA-1

---

### QUA-5 : Generateur PDF — Convocation stagiaire
- **Type** : Feature
- **Priorite** : Moyenne
- **Estimation** : 2h
- **Description** :
  - Generer une convocation individuelle ou en masse
  - Contenu : nom, formation, dates, URL de la plateforme, contact
  - Bouton "Convoquer" dans le dashboard formateur onglet Apprenants
  - Envoi par email avec le PDF en piece jointe
- **Acces** : admin + formateur
- **Dependance** : QUA-1

---

### QUA-6 : Feuille d'emargement e-learning
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 4h
- **Description** :
  - Remplacer la feuille papier par un rapport de connexion
  - Extraire les logs OpenEdX : temps passe, modules accedes, dates de connexion
  - Generer un PDF avec tableau : date, heure debut, heure fin, duree, modules
  - Equivalent legal de la feuille d'emargement pour le e-learning
  - Bouton "Emargement" dans le dashboard formateur par cours
- **Acces** : formateur
- **Donnees** : StudentModule, courseware.models (completion tracking)
- **Dependance** : QUA-1

---

### QUA-7 : Evaluation pre/post formation
- **Type** : Feature
- **Priorite** : Moyenne
- **Estimation** : 3h
- **Description** :
  - Generer un rapport comparatif pre-formation vs post-formation
  - Pre : score du quiz diagnostique (premier quiz OLX du cours)
  - Post : score du quiz final + note globale
  - Tableau comparatif par stagiaire
  - Graphique d'evolution (barres pre vs post)
  - Bouton dans le dashboard formateur
- **Acces** : formateur
- **Dependance** : QUA-1

---

### QUA-8 : Rapport de suivi de progression (enrichi)
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 2h (enrichir l'existant)
- **Description** :
  - Enrichir `generate_rapport_suivi_pdf` existant
  - Ajouter : progression par module (pas juste binaire), temps passe, date dernier acces
  - Vue par stagiaire (tous ses cours) en plus de la vue par cours
  - Filtrer par academie / par client B2B
  - Export en masse (ZIP de tous les PDF)
- **Acces** : admin + formateur
- **Dependance** : QUA-1

---

### QUA-9 : Enquete de satisfaction
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 5h
- **Description** :
  - Formulaire en ligne (page dans le LMS) post-formation
  - 5 criteres notes /5 : contenu, pedagogie, formateur, plateforme, global
  - Commentaire libre
  - Envoi automatique par email quand le stagiaire termine
  - Synthese PDF par formation (moyennes, graphiques, verbatims)
  - Tableau de bord satisfaction dans le dashboard admin
- **Modele** : SatisfactionSurvey
- **Acces** : admin (synthese), stagiaire (formulaire)
- **Dependance** : QUA-1

---

### QUA-10 : Bilan de formation (synthese auditeur)
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 4h
- **Description** :
  - Document PDF complet pour l'auditeur Qualiopi
  - Contenu :
    - Page de garde (formation, organisme, periode)
    - Programme de formation
    - Liste des stagiaires avec resultats
    - Taux de completion et de reussite
    - Synthese des evaluations pre/post
    - Synthese de satisfaction
    - Feuilles d'emargement
    - Attestations
  - Un seul bouton "Generer le dossier Qualiopi" dans le dashboard admin
  - Produit un ZIP avec tous les PDF classes par stagiaire
- **Acces** : admin uniquement
- **Dependance** : QUA-2 a QUA-9 (tous)

---

### QUA-11 : Interface dashboard — Onglet Qualiopi
- **Type** : Feature
- **Priorite** : Haute
- **Estimation** : 4h
- **Description** :
  - Nouvel onglet "Qualiopi" dans le dashboard admin
  - Vue par formation : liste tous les documents disponibles avec statut
  - Boutons de telechargement individuels + "Tout generer"
  - Vue par stagiaire : tous les documents d'un stagiaire
  - Indicateurs visuels : vert (document pret), orange (a generer), rouge (manquant)
  - Tableau de bord conformite : % de documents complets par formation
- **Template** : admin_central_dashboard.html (nouveau page-qualiopi)
- **Acces** : admin + formateur (vue reduite)

---

### QUA-12 : Documentation auditeur
- **Type** : Documentation
- **Priorite** : Haute
- **Estimation** : 3h
- **Description** :
  Creer `docs/qualiopi/GUIDE_AUDITEUR.md` :
  - Presentation de l'organisme
  - Liste des indicateurs couverts (avec numero et reference)
  - Pour chaque indicateur : quel document, comment y acceder, qui le genere
  - Procedure de generation des documents
  - FAQ auditeur (questions types et reponses)
  - Capture d'ecran du dashboard Qualiopi

---

### QUA-13 : Documentation admin
- **Type** : Documentation
- **Priorite** : Haute
- **Estimation** : 2h
- **Description** :
  Creer `docs/qualiopi/GUIDE_ADMIN.md` :
  - Comment generer chaque type de document
  - Comment configurer le programme de formation
  - Comment generer les conventions B2B
  - Comment envoyer les convocations
  - Comment generer le dossier complet pour un audit
  - Comment exporter en masse

---

### QUA-14 : Documentation formateur
- **Type** : Documentation
- **Priorite** : Haute
- **Estimation** : 2h
- **Description** :
  Creer `docs/qualiopi/GUIDE_FORMATEUR.md` :
  - Comment acceder a ses formations
  - Comment generer les feuilles d'emargement
  - Comment consulter la progression des stagiaires
  - Comment generer les evaluations pre/post
  - Comment telecharger les attestations de ses stagiaires

---

## 4. Planning

| Semaine | Tickets | Effort |
|---------|---------|--------|
| 1 | QUA-1 (modeles) + QUA-2 (attestation) + QUA-8 (suivi enrichi) | 7h |
| 2 | QUA-3 (programme) + QUA-6 (emargement) + QUA-11 (dashboard) | 12h |
| 3 | QUA-4 (convention) + QUA-5 (convocation) + QUA-7 (eval pre/post) | 8h |
| 4 | QUA-9 (satisfaction) + QUA-10 (bilan auditeur) | 9h |
| 5 | QUA-12 + QUA-13 + QUA-14 (documentation) | 7h |
| **Total** | **14 tickets** | **~43h** |

---

## 5. Priorites

### Indispensable pour un audit (a faire en premier)
- QUA-1 : Modeles de donnees
- QUA-2 : Attestation de formation
- QUA-6 : Feuille d'emargement
- QUA-8 : Rapport de suivi
- QUA-10 : Bilan auditeur
- QUA-11 : Dashboard Qualiopi
- QUA-12 : Documentation auditeur

### Important mais pas bloquant
- QUA-3 : Programme de formation
- QUA-9 : Enquete de satisfaction
- QUA-13 : Documentation admin
- QUA-14 : Documentation formateur

### Peut attendre
- QUA-4 : Convention B2B
- QUA-5 : Convocation
- QUA-7 : Evaluation pre/post

---

## 6. Correspondance indicateurs Qualiopi

| Indicateur | Critere | Document | Ticket |
|------------|---------|----------|--------|
| 1 | Info public | CGV (existant sur le site) | — |
| 2 | Info public | Catalogue formations | QUA-3 |
| 4 | Conception | Programme de formation | QUA-3 |
| 6 | Conception | Convention de formation | QUA-4 |
| 7 | Conception | Convocation stagiaire | QUA-5 |
| 11 | Realisation | Feuille d'emargement | QUA-6 |
| 12 | Realisation | Evaluation pre/post | QUA-7 |
| 17 | Realisation | Suivi de progression | QUA-8 |
| 19 | Satisfaction | Enquete de satisfaction | QUA-9 |
| 32 | Certification | Attestation de formation | QUA-2 |
