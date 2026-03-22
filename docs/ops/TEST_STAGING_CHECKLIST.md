# Checklist de test staging — Mission Formations

> Date du test : ____________________
> Testeur : ____________________
> Apres deploy du : ____________________

---

## Etape 1 — Pages publiques (sans connexion)

- [ ] 1.1 Homepage → https://academie.staging.missionformations.com/
  - Attendu : hero, catalogue, footer Mission Formations
  - Resultat : ____________________

- [ ] 1.2 Login → https://academie.staging.missionformations.com/login
  - Attendu : formulaire connexion avec design MF (panneau bleu a gauche)
  - Resultat : ____________________

- [ ] 1.3 Register → https://academie.staging.missionformations.com/register
  - Attendu : formulaire inscription
  - Resultat : ____________________

- [ ] 1.4 Catalogue → https://academie.staging.missionformations.com/catalogue/
  - Attendu : liste des 10 formations avec cartes
  - Resultat : ____________________

- [ ] 1.5 Cours about → https://academie.staging.missionformations.com/courses/course-v1:MissionFormations+MF-VTC-2025+2025/about
  - Attendu : page "A propos" de la formation VTC
  - Resultat : ____________________

- [ ] 1.6 Contact → https://academie.staging.missionformations.com/contact/
  - Attendu : formulaire de contact
  - Resultat : ____________________

- [ ] 1.7 Aide → https://academie.staging.missionformations.com/aide/
  - Attendu : centre d'aide (guides, FAQ)
  - Resultat : ____________________

**Bilan etape 1 : ___/7 OK**

---

## Etape 2 — Connexion

- [ ] 2.1 Connexion superadmin (superadmin_zakia)
  - Attendu : redirection vers /admin/mission-dashboard/
  - Resultat : ____________________

- [ ] 2.2 Deconnexion
  - Attendu : retour a la homepage
  - Resultat : ____________________

- [ ] 2.3 Connexion apprenant (lyli.semiai@gmail.com / semiai_allyah)
  - Attendu : redirection vers /dashboard
  - Resultat : ____________________

**Bilan etape 2 : ___/3 OK**

---

## Etape 3 — Dashboard apprenant (connecte avec semiai_allyah)

- [ ] 3.1 Le dashboard s'affiche
  - Attendu : hero avec progression, formations listees
  - Resultat : ____________________

- [ ] 3.2 La formation VTC apparait
  - Attendu : carte avec titre "Certificat de Formation Professionnelle VTC"
  - Resultat : ____________________

- [ ] 3.3 Bouton "Acceder au cours" fonctionne
  - Attendu : redirection vers le cours (MFE Learning)
  - Resultat : ____________________

**Bilan etape 3 : ___/3 OK**

---

## Etape 4 — Acces au cours VTC (LE PLUS CRITIQUE)

- [ ] 4.1 Cours accessible depuis le dashboard
  - Attendu : redirection vers apps.academie.staging.missionformations.com/learning/course/...
  - Resultat : ____________________

- [ ] 4.2 La page du cours s'affiche
  - Attendu : contenu du cours (chapitres, modules) — PAS "cours introuvable"
  - Resultat : ____________________

- [ ] 4.3 Cliquer sur un chapitre
  - Attendu : le contenu du chapitre s'affiche
  - Resultat : ____________________

- [ ] 4.4 Cliquer sur un quiz
  - Attendu : le quiz s'affiche et peut etre soumis
  - Resultat : ____________________

> **Si erreur SSL** : attendre 2 minutes et reessayer (Caddy genere le certificat)
> **Si "cours introuvable"** : STOP — regression detectee

**Bilan etape 4 : ___/4 OK**

---

## Etape 5 — Dashboard admin (connecte avec superadmin_zakia)

- [ ] 5.1 Dashboard admin → https://academie.staging.missionformations.com/admin/mission-dashboard/
  - Attendu : dashboard admin avec sidebar + KPIs
  - Resultat : ____________________

- [ ] 5.2 Section "Studio" dans la sidebar
  - Attendu : lien "Ouvrir Studio" visible
  - Resultat : ____________________

- [ ] 5.3 Cliquer "Ouvrir Studio"
  - Attendu : ouvre Studio dans un nouvel onglet (studio.staging.missionformations.com)
  - Resultat : ____________________

- [ ] 5.4 Onglet "Formateurs"
  - Attendu : liste des formateurs
  - Resultat : ____________________

- [ ] 5.5 Onglet "Apprenants"
  - Attendu : liste des apprenants
  - Resultat : ____________________

- [ ] 5.6 Onglet "Formations"
  - Attendu : liste des cours
  - Resultat : ____________________

**Bilan etape 5 : ___/6 OK**

---

## Etape 6 — Chat WeWill

- [ ] 6.1 Widget chat visible en bas a droite
  - Attendu : bulle de chat presente
  - Resultat : ____________________

- [ ] 6.2 Cliquer sur le widget
  - Attendu : fenetre de chat s'ouvre
  - Resultat : ____________________

- [ ] 6.3 Branding "Powered by WeWill"
  - Attendu : PAS "Powered by Chatwoot"
  - Resultat : ____________________

- [ ] 6.4 Lien pointe vers missionformations.com
  - Attendu : PAS chatwoot.com
  - Resultat : ____________________

**Bilan etape 6 : ___/4 OK**

---

## Etape 7 — Studio

- [ ] 7.1 Studio → https://studio.staging.missionformations.com/
  - Attendu : page d'accueil Studio
  - Resultat : ____________________

- [ ] 7.2 Se connecter (meme compte admin)
  - Attendu : liste des cours dans Studio
  - Resultat : ____________________

- [ ] 7.3 Ouvrir le cours VTC
  - Attendu : editeur de cours avec les 8 chapitres
  - Resultat : ____________________

**Bilan etape 7 : ___/3 OK**

---

## Etape 8 — Certificats (preview)

- [ ] 8.1 Catalogue certificats → https://academie.staging.missionformations.com/static/certificates-catalogue.html
  - Attendu : catalogue des 20 templates de certificats
  - Resultat : ____________________

- [ ] 8.2 Cliquer sur chaque onglet (VTC, Gestion, Securite...)
  - Attendu : le design du certificat change
  - Resultat : ____________________

**Bilan etape 8 : ___/2 OK**

---

## Etape 9 — Pages d'erreur

- [ ] 9.1 Page 404 → https://academie.staging.missionformations.com/page-qui-nexiste-pas
  - Attendu : page 404 customisee Mission Formations
  - Resultat : ____________________

**Bilan etape 9 : ___/1 OK**

---

## BILAN GLOBAL

| Etape | Score | Statut |
|-------|-------|--------|
| 1. Pages publiques | ___/7 | |
| 2. Connexion | ___/3 | |
| 3. Dashboard apprenant | ___/3 | |
| 4. Cours VTC | ___/4 | |
| 5. Dashboard admin | ___/6 | |
| 6. Chat WeWill | ___/4 | |
| 7. Studio | ___/3 | |
| 8. Certificats | ___/2 | |
| 9. Pages erreur | ___/1 | |
| **TOTAL** | **___/33** | |

---

## REGRESSIONS DETECTEES

| # | Test echoue | Erreur constatee | Action |
|---|-------------|-----------------|--------|
| | | | |
| | | | |
| | | | |

---

## DECISION

- [ ] **TOUT OK** — le staging est stable, on peut continuer a developper
- [ ] **REGRESSIONS** — rollback necessaire avant de continuer
- [ ] **PROBLEMES MINEURS** — noter et corriger dans le prochain sprint

**Signe par** : ____________________
**Date** : ____________________
