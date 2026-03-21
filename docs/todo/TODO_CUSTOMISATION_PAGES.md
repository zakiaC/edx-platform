# TODO — Customisation des pages OpenEdX + assets du Desktop

> 21 mars 2026
> Inventaire complet des fichiers a implementer depuis le Desktop et des pages a customiser

---

## 1. FICHIERS PRETS A IMPLEMENTER (Desktop/Mission-Formation)

### 1.1 Certificats — 20 templates HTML/CSS

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/certificats/`

| # | Domaine | Style | Statut |
|---|---------|-------|--------|
| 1 | VTC Transport | Dark premium, motif route, bleu→vert gradient | A implementer |
| 2 | Gestion d'entreprise | Blanc classique, coins dores | A implementer |
| 3 | Securite routiere | Dark rouge, bandes chevron | A implementer |
| 4 | Relation client | Blanc chaud, tons peche | A implementer |
| 5 | Langues | Dark bleu, globe | A implementer |
| 6 | Digital / Numerique | Cyber dark, grille | A implementer |
| 7 | Comptabilite | Blanc vert, formel | A implementer |
| 8 | Droit du travail | Navy serieux | A implementer |
| 9 | Premiers secours (SST) | Blanc, croix rouge | A implementer |
| 10 | Management / Leadership | Royal pourpre | A implementer |
| 11 | Immobilier | Blanc creme marbre | A implementer |
| 12 | Sante / Bien-etre | Dark teal | A implementer |
| 13 | Marketing | Blanc, formes geometriques | A implementer |
| 14 | Logistique | Dark industriel | A implementer |
| 15 | Environnement / RSE | Blanc nature, feuillage | A implementer |
| 16 | Intelligence Artificielle | Noir futuriste, scanlines | A implementer |
| 17 | Ressources Humaines | Dark bordeaux | A implementer |
| 18 | Communication | Blanc, vagues et cercles | A implementer |
| 19 | Finance / Investissement | Noir luxe, double bordure or | A implementer |
| 20 | Tourisme / Hotellerie | Navy elegant, vagues marines | A implementer |

**Fichiers** :
- `certificats-20-templates.html` — 20 templates HTML/CSS complets (68 Ko)
- `Tableau propre des 20 templates.md` — Reference des domaines et styles

**Action** : Convertir ces templates HTML en templates Mako OpenEdX (`certificates/valid.html`)
et les associer aux organisations dans Studio.

---

### 1.2 Pages d'erreur custom

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/SECTION 10 — PAGES D'ERREUR/`

| Fichier | Statut dans le theme |
|---------|---------------------|
| `403.html` | Deja implemente dans mission-theme |
| `404.html` | Deja implemente |
| `500.html` | Deja implemente (server-error.html) |
| `course-not-found.html` | Deja implemente |
| `maintenance.html` | Deja implemente |

**Action** : Verifier que les versions dans le theme sont a jour avec ces fichiers source.

---

### 1.3 Emails custom

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/section 9 email/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `preview-emails-mission.html` | Preview de tous les templates email | Reference |
| `certificate_notification.html` | Notification certificat obtenu | A verifier vs theme actuel |
| `instructor_email.html` | Email formateur | A verifier vs theme actuel |
| `Section enrollment formation/` | Email d'inscription | A verifier |
| `section alerte deadline/` | Email d'alerte deadline | A implementer |

---

### 1.4 Forum / Discussions custom

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `preview-forum-mission(2).html` | Design custom du forum de discussion | A implementer |

**Action** : Adapter le design pour le MFE Discussions ou le template Mako natif.

---

### 1.5 Studio (CMS) custom

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `preview-mission-hub-studio.html` | Design custom complet de Studio | A evaluer |
| `mission-studio.css` | CSS custom pour Studio | A implementer |

---

### 1.6 Wiki custom

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/section wiki/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `preview-wiki-mission.html` | Design custom du wiki OpenEdX | A evaluer |

---

### 1.7 Favicons et branding

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/generation claude/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `favicons-mission-roles.html` | Favicons par role (apprenant, formateur, admin) | A implementer |

---

### 1.8 Homepage alternative

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/page openedx index/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `apercu-homepage-mission.html` | Design alternatif de la homepage | A comparer avec l'actuel |
| `mf-homepage.css` | CSS de la homepage alternative | A comparer |
| `Capture d'ecran 2026-02-23.png` | Screenshot de reference | Reference visuelle |

---

### 1.9 Headers

**Source** : `Desktop/Mission-Formation/travail du jour 20:02/fichier customiser a implementer/`

| Fichier | Description | Statut |
|---------|------------|--------|
| `header.html` | Header design v1 | A comparer avec l'actuel |
| `header 2.html` | Header design v2 | A comparer |
| `main.html` | Template principal | A comparer |
| `mission-overrides.css` | CSS overrides globaux | A verifier si integre |

---

## 2. DOCUMENTATION ET GUIDES (Desktop/Mission-Formation)

### 2.1 Guides apprenants

**Source** : `Desktop/Mission-Formation/Documentation Mission/Documentation academie mission/`

| Fichier | Description | Deja dans /aide/ ? |
|---------|------------|-------------------|
| `guide-apprenant.html` | Guide complet apprenant | A verifier |
| `guide-demarrer.html` | Guide demarrage | A verifier |
| `guide-naviguer.html` | Guide navigation cours | A verifier |
| `guide-exercices.html` | Guide exercices | A verifier |
| `guide-progression.html` | Guide progression | A verifier |
| `guide-certificat.html` | Guide certificats | A verifier |
| `guide-contenus.html` | Guide contenus | A verifier |
| `guide-discussions.html` | Guide discussions/forum | A verifier |
| `guide-faq.html` | FAQ | A verifier |

**Action** : Verifier quels guides sont deja integres dans la page /aide/ du theme.

### 2.2 Documentation technique

**Source** : `Desktop/Mission-Formation/Documentation Mission/Documentation technique/`

| Fichier | Description |
|---------|------------|
| `GUIDE_STAGING_MISSION_FORMATIONS.md` | Guide staging |

### 2.3 Documentation Mission Hub (formateurs)

**Source** : `Desktop/Mission-Formation/Documentation Mission/Documentation Mission Hub/`

Contenu complet de documentation Studio/formateur :
- Formateurs : inscrire apprenants, telecharger notes, envoyer emails, equipe cours
- Composants : exercices, SCORM, Zoom meeting
- studio-vs-lms-mission.html

### 2.4 Ecosysteme Mission

**Source** : `Desktop/Mission-Formation/Documentation Mission/Ecosysteme Mission/`

A explorer pour le contenu.

---

## 3. ASSETS COMMERCIAUX (Desktop/Mission-Formation)

### 3.1 Strategie commerciale

**Source** : `Desktop/Mission-Formation/strategie commerciale/`

A explorer — peut contenir des elements pour le kit commercial.

### 3.2 Strategie financiere

**Source** : `Desktop/Mission-Formation/strategie financiere/`

- Document holding

### 3.3 Pole communication

**Source** : `Desktop/Mission-Formation/Pole communication/`

| Dossier | Contenu |
|---------|---------|
| `Feuille emergement/` | Templates feuille d'emargement |
| `Livre VTC/` | Contenu du livre VTC |
| `Livret accueil handicap/` | Livret d'accueil handicap (Qualiopi Ind. 4) |
| `bandeau equipe/` | Visuels equipe |
| `remplissage automatique feuille de presence/` | Script auto feuille de presence |

### 3.4 Site internet

**Source** : `Desktop/Mission-Formation/site-internet-MF/`

| Dossier | Contenu |
|---------|---------|
| `Email/` | Templates email du site |
| `Logo/` | Logos Mission Formations |
| `RUBRIQUE SITE/` | Structure des rubriques |
| `deploy_missionformations/` | Scripts de deploiement du site |
| `documentation/` | Doc du site |

### 3.5 Design natif OpenEdX a customiser

**Source** : `Desktop/Mission-Formation/design natif openedex a customiser/`

| Dossier | Contenu | Statut |
|---------|---------|--------|
| `Ajouter nouveau composant/` | Screenshots du design a customiser | Reference |
| `Onglet recherche/` | Screenshots | Reference |
| `Onglet schedulle and detail/` | Screenshots | Reference |
| `Parametres/` | Screenshots | Reference |
| `interface LTI:Zoom/` | Screenshots integration Zoom | Reference |

### 3.6 Annales VTC

**Source** : `Desktop/Mission-Formation/annales/`

| Dossier | Contenu |
|---------|---------|
| `CMA/` | Annales CMA |
| `Organisme vtc qualiopi/` | Annales organismes VTC |
| `by_matiere/` | Annales par matiere |
| `scipt scrapping google form/` | Script de scraping |
| `statistique vtc examen/` | Statistiques examen |

---

## 4. PAGES OPENEDX A CUSTOMISER (non encore faites)

### 4.1 Priorite CRITIQUE (pour la demo mardi)

| # | Page | URL | Action |
|---|------|-----|--------|
| 1 | **Courseware** | `/courses/{id}/courseware/` | Verifier le rendu du header/footer MF dans le cours |
| 2 | **Certificat web** | `/certificates/{id}` | Implementer un des 20 templates (VTC pour la demo) |

### 4.2 Priorite HAUTE (avant mise en prod)

| # | Page | URL | Action |
|---|------|-----|--------|
| 3 | Progression cours | `/courses/{id}/progress` | Customiser avec couleurs MF |
| 4 | Forum/Discussions | `/courses/{id}/discussion/` | Utiliser le design du fichier `preview-forum-mission.html` |
| 5 | Studio header/accueil | Studio | Utiliser `mission-studio.css` + `preview-mission-hub-studio.html` |

### 4.3 Priorite MOYENNE (V2)

| # | Page | URL | Action |
|---|------|-----|--------|
| 6 | Profil utilisateur | `/u/{username}` | MFE Profile — config couleurs |
| 7 | Parametres compte | `/account/settings` | MFE Account — config couleurs |
| 8 | Wiki | `/courses/{id}/wiki/` | Utiliser `preview-wiki-mission.html` |
| 9 | Honor code | `/honor` | Page statique simple |
| 10 | Gradebook | Instructor tools | MFE Gradebook — config couleurs |

---

## 5. RECAPITULATIF DES ASSETS SUR LE DESKTOP

| Categorie | Nb fichiers | Pret a implementer | Deja implemente | A creer |
|-----------|------------|--------------------|-----------------|---------|
| Certificats (20 templates) | 2 | Oui (HTML/CSS complets) | Non | Conversion Mako |
| Pages d'erreur | 5 | Oui | Oui (deja dans theme) | Verifier MAJ |
| Emails | 5+ | Oui | Partiellement | Verifier MAJ |
| Forum | 1 | Oui | Non | A implementer |
| Studio CSS | 2 | Oui | Partiellement | A implementer |
| Wiki | 1 | Oui | Non | A evaluer |
| Favicons | 1 | Oui | Non | A implementer |
| Homepage alt | 3 | Oui | Deja une homepage | A comparer |
| Headers | 3 | Oui | Deja un header | A comparer |
| Guides apprenant | 9 | Oui | Partiellement (page /aide/) | A verifier |
| Livret handicap | 1 dossier | Oui | Non | A integrer (Qualiopi Ind. 4) |
| Feuille emargement | 1 dossier | Oui | Non | A integrer (Qualiopi Ind. 9) |
| Logos | 1 dossier | Oui | Oui (logo.png dans theme) | OK |
| Annales VTC | 5 dossiers | Oui | Non | Contenu pedagogique |

**Total : ~40+ fichiers prets a implementer sur le Desktop**
