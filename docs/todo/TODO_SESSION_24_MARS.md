# TODO — Session 24 mars 2026

> Bilan de la session : Demo Centre Social Croizat + Formation Strategie Commerciale

---

## FAIT AUJOURD'HUI

### Dashboard partenaire Croizat (site missionformations.com)
- [x] Analyse du besoin + cahier des charges 16 onglets
- [x] Diagnostic Product Manager + funnel de vente
- [x] Analyse financiere (devis/factures : 3 610€ Croizat + 1 050€ Tillon)
- [x] Analyse SROI (modele Excel v2 : ratio x3.95)
- [x] Dashboard 16 onglets implemente (2 400+ lignes PHP)
- [x] Couleurs Saint-Denis (#3773FF / #F56441) + Powered by Mission Formations
- [x] Galerie photos (18 photos HEIC/JPG converties)
- [x] Videos YouTube embeddees (Restitution Tillon + Croizat)
- [x] Suivi des seances enrichi (creneau, presences, outils, methodologie, freins, acquis)
- [x] Export par seance + export global (rapport imprimable)
- [x] Calculateur SROI interactif (3 scenarios + popups facteurs ajustement)
- [x] Selecteur financeur modulable (CAF, Mairie, Departement, France Travail, OPCO, Fondation)
- [x] Roue methodologie 19 etapes style KPM (fleches progression + labels phase)
- [x] Proposition commerciale 7 pages HTML
- [x] Automatisation Qualiopi (flux demo)
- [x] Propositions 2026 (2 ateliers : Prise de parole S2 + Retour emploi)
- [x] Formule & Tarifs (3 formules : 2 560€ / 3 610€ / sur devis)
- [x] Contact & RDV (Zakia Semiai + Abdallah Semiai)
- [x] Compte auth wahib.sabbagh@saintdenis.fr / Croizat2026
- [x] Redirection auto vers dashboard Croizat
- [x] Script bootstrap admin
- [x] Deploy FTP OVH (381 fichiers)

### Formation Strategie Commerciale (staging OpenEdX)
- [x] Plan du cours 5 modules / 40 videos
- [x] Descriptions + tags YouTube pour les 40 videos
- [x] 39 videos uploadees sur YouTube (non listees)
- [x] Cours OLX cree (170 fichiers)
- [x] Import dans Studio staging

### Documentation
- [x] Guide admin gestion des comptes (GUIDE_ADMIN_COMPTES.md)
- [x] Plan du cours avec liens YouTube (PLAN_COURS_STRATEGIE_COMMERCIALE.md)

---

## RESTE A FAIRE

### Immediat (avant la demo Croizat)
- [ ] Creer le compte admin sur missionformations.com (via phpMyAdmin : roles_mask=1)
- [ ] Creer le compte wahib.sabbagh@saintdenis.fr via l'admin (ou verifier qu'il existe)
- [ ] Tester la connexion partenaire sur missionformations.com/partenaire/login/
- [ ] Verifier que la redirection vers /espace/partenaire/croizat/ fonctionne
- [ ] Supprimer les fichiers temporaires (setup-account.php, test-local.php, bootstrap-web.php)
- [ ] Tuer le serveur PHP local (pkill php)

### Formation Strategie Commerciale
- [ ] Publier les 5 modules dans Studio (section par section)
- [ ] Uploader la video manquante 2.1 (Parcours d'achat — Les 4 etapes)
- [ ] Rattacher le cours a l'academie Finance (AcademyCourse)
- [ ] Creer les comptes apprenants demo sur le LMS
- [ ] Tester le parcours apprenant complet (inscription → cours → video → quiz)
- [ ] Ajouter des quiz a chaque fin de module

### Design dashboard Croizat
- [ ] Ameliorer le design global (trop IA selon retour utilisateur)
- [ ] Ajouter photo Abdallah Semiai dans l'onglet Contact
- [ ] Revoir la colorimetrie Mission Formations sur toutes les pages

### Session ROI social (1h ensemble)
- [ ] Calibrer les curseurs SROI pour le contexte Saint-Denis/Croizat
- [ ] Adapter les proxies (donnees CAF Ain → donnees IDF)
- [ ] Valider les formules avec Zakia

### Smoke checks site (4 en echec)
- [ ] Corriger auditeur_root (attendu 302, recu 200)
- [ ] Corriger mission_interne_tech (erreur DNS)
- [ ] Corriger mission_interne_commercial (erreur DNS)
- [ ] Corriger mission_interne_monitoring (attendu 200, recu 404)

---

## NOTES DE SESSION

- Le directeur du centre est Wahib Sabbagh (wahib.sabbagh@saintdenis.fr)
- La referente famille est Samia Hammouchi
- L'interlocutrice MF est Zakia Semiai (chef de projet)
- Le formateur est Abdallah Semiai (Association Oratore)
- Le centre social est finance par son budget propre (pas la CAF)
- Total facture Croizat : 3 610€ (devis 2 560€ + facture 1 050€)
- ROI social mesure : x3.95 (pour 1€ investi, 3.95€ de valeur sociale)
- 2 femmes ont repris un emploi, 1 a cree une epicerie solidaire
- Videos de restitution sur YouTube : Tillon (ji8e-v7l4J8) + Croizat (edVP93FdPUk)
