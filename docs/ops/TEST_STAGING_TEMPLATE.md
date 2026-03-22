# Checklist de test staging — Mission Formations

> Date du test : __/__/2026
> Testeur : ____
> Apres deploy du : __/__/2026

---

## Etape 1 — Pages publiques (sans connexion)

| # | Page | URL | ✅/❌ | Remarque |
|---|------|-----|-------|----------|
| 1.1 | Homepage | https://academie.staging.missionformations.com/ | | |
| 1.2 | Login | https://academie.staging.missionformations.com/login | | |
| 1.3 | Register | https://academie.staging.missionformations.com/register | | |
| 1.4 | Catalogue | https://academie.staging.missionformations.com/catalogue/ | | |
| 1.5 | Cours about VTC | https://academie.staging.missionformations.com/courses/course-v1:MissionFormations+MF-VTC-2025+2025/about | | |
| 1.6 | Contact | https://academie.staging.missionformations.com/contact/ | | |
| 1.7 | Aide | https://academie.staging.missionformations.com/aide/ | | |

---

## Etape 2 — Connexion

| # | Action | Attendu | ✅/❌ | Remarque |
|---|--------|---------|-------|----------|
| 2.1 | Connexion superadmin_zakia | Redirect → /admin/mission-dashboard/ | | |
| 2.2 | Deconnexion | Retour homepage | | |
| 2.3 | Connexion semiai_allyah | Redirect → /dashboard | | |

---

## Etape 3 — Dashboard apprenant (connecte semiai_allyah)

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 3.1 | Dashboard s'affiche | Hero + formations listees | | |
| 3.2 | Formation VTC visible | Carte "Certificat VTC" | | |
| 3.3 | Bouton "Acceder au cours" | Redirect vers le cours | | |

---

## Etape 4 — Cours VTC (CRITIQUE)

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 4.1 | Cours accessible depuis dashboard | Redirect vers MFE Learning | | |
| 4.2 | Page du cours s'affiche | Chapitres et modules visibles | | |
| 4.3 | Cliquer sur un chapitre | Contenu affiche | | |
| 4.4 | Cliquer sur un quiz | Quiz affiche et soumissible | | |

> Si SSL error → attendre 2 min. Si "cours introuvable" → STOP regression.

---

## Etape 5 — Dashboard admin (connecte superadmin_zakia)

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 5.1 | Dashboard admin | Sidebar + KPIs | | |
| 5.2 | Section Studio sidebar | Lien "Ouvrir Studio" visible | | |
| 5.3 | Clic "Ouvrir Studio" | Ouvre studio.staging.missionformations.com | | |
| 5.4 | Onglet Formateurs | Liste formateurs | | |
| 5.5 | Onglet Apprenants | Liste apprenants | | |
| 5.6 | Onglet Formations | Liste cours | | |

---

## Etape 6 — Chat WeWill

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 6.1 | Widget chat visible | Bulle en bas a droite | | |
| 6.2 | Clic sur le widget | Fenetre chat s'ouvre | | |
| 6.3 | Branding | "Powered by WeWill" (pas Chatwoot) | | |
| 6.4 | Lien branding | missionformations.com (pas chatwoot.com) | | |

---

## Etape 7 — Studio

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 7.1 | Accueil Studio | https://studio.staging.missionformations.com/ | | |
| 7.2 | Connexion admin | Liste des cours | | |
| 7.3 | Ouvrir cours VTC | Editeur avec 8 chapitres | | |

---

## Etape 8 — Certificats

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 8.1 | Catalogue preview | /static/certificates-catalogue.html | | |
| 8.2 | 20 onglets fonctionnels | Chaque design s'affiche | | |

---

## Etape 9 — Page erreur

| # | Verification | Attendu | ✅/❌ | Remarque |
|---|-------------|---------|-------|----------|
| 9.1 | Page 404 | /page-qui-nexiste-pas → 404 customise MF | | |

---

## BILAN

| Etape | Score | Statut |
|-------|-------|--------|
| 1. Pages publiques | /7 | |
| 2. Connexion | /3 | |
| 3. Dashboard apprenant | /3 | |
| 4. Cours VTC | /4 | |
| 5. Dashboard admin | /6 | |
| 6. Chat WeWill | /4 | |
| 7. Studio | /3 | |
| 8. Certificats | /2 | |
| 9. Page erreur | /1 | |
| **TOTAL** | **/33** | |

## Regressions detectees

| # | Test | Erreur | Priorite |
|---|------|--------|----------|
| | | | |

## Decision

- [ ] TOUT OK → staging stable
- [ ] REGRESSIONS → rollback avant de continuer
- [ ] MINEURS → noter et corriger au prochain sprint
