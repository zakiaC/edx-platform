# Cahier de charge — Customisation Studio Mission Formations

## Contexte

Le Studio (CMS) utilise le MFE course-authoring (application React).
Toutes les pages Studio sont rendues par le MFE, pas par des templates Mako.
La customisation passe par :
- Le brand package (couleurs, logo, typo)
- Le plugin tutor-indigo (footer custom)
- Le MFE_CONFIG (logo URL, favicon, slogan, liens footer)

---

## Sprint Studio 1 — Branding global MFE

### Objectif
Remplacer toute l'identite visuelle OpenEdX par Mission Formations sur toutes les pages MFE (Studio + pages cours LMS).

### Pages concernees

| Page | URL | Rendu |
|------|-----|-------|
| Accueil Studio | /home/ | MFE |
| Outline de cours | /course/course-v1:... | MFE |
| Pages & Resources | /course/.../pages-and-resources | MFE |
| Updates | /course/.../updates | MFE |
| Files & Uploads | /course/.../assets | MFE |
| Video Uploads | /course/.../videos | MFE |
| Schedule & Details | /course/.../settings/details | MFE |
| Grading | /course/.../settings/grading | MFE |
| Course Team | /course/.../course_team | MFE |
| Advanced Settings | /course/.../settings/advanced | MFE |
| Import | /course/.../import | MFE |
| Export | /course/.../export | MFE |
| Certificats | /course/.../certificates | MFE |
| Page cours LMS (learning) | /learning/course/... | MFE |
| Account | /account/ | MFE |
| Profile | /profile/ | MFE |
| Discussions | /discussions/ | MFE |

### Tache 1 — Header MFE

**Etat actuel :** logo OpenEdX, couleur de fond par defaut, navigation OpenEdX
**Etat cible :**
- Logo Mission Formations (SVG + PNG, ~40px hauteur)
- Lien logo → https://missionformations.com
- Couleur de fond header : a definir par Chloe
- Couleur des liens de navigation : a definir par Chloe

**Livrable design :**
- Maquette header desktop (1440px)
- Maquette header mobile (375px)
- Logo SVG fond transparent
- Logo PNG fond transparent (min 200px largeur)

### Tache 2 — Footer MFE

**Etat actuel :** texte "edX and Open edX, and the edX and Open edX logos are registered trademarks of edX Inc", logo OpenEdX
**Etat cible :**
- Slogan : "Donnez du sens a votre parcours!"
- Liens : Qui sommes-nous, Catalogue, Centre d'aide, Contact, CGU/CGV, Mentions legales
- Aucune mention OpenEdX / edX
- Logo Mission Formations

**Livrable design :**
- Maquette footer desktop (1440px)
- Maquette footer mobile (375px)

### Tache 3 — Couleurs globales

**Etat actuel :** bleu OpenEdX (#0075B4), gris par defaut
**Etat cible :** palette Mission Formations

**Elements a definir :**
- Couleur primaire (boutons, liens actifs, accents)
- Couleur secondaire (boutons secondaires, hover)
- Couleur fond header
- Couleur fond footer
- Couleur fond page
- Couleur texte principal
- Couleur texte secondaire
- Couleur succes (vert)
- Couleur erreur (rouge)
- Couleur warning (orange)

**Livrable design :**
- Charte couleurs avec codes hex
- Fichier _variables.scss du brand package

### Tache 4 — Favicon

**Etat actuel :** favicon OpenEdX
**Etat cible :** favicon Mission Formations

**Livrable design :**
- favicon.ico (32x32 et 16x16)
- apple-touch-icon.png (180x180)

---

## Sprint Studio 2 — Pages Mako restantes

Ces pages ne passent pas par le MFE. Elles sont rarement vues mais doivent etre coherentes.

### Tache 5 — Page 404 Studio

**Fichier :** themes/mission-theme/cms/templates/404.html
**Etat actuel :** page OpenEdX par defaut
**Etat cible :** page 404 brandee Mission Formations

### Tache 6 — Page 500 Studio

**Fichier :** themes/mission-theme/cms/templates/500.html
**Etat actuel :** page OpenEdX par defaut
**Etat cible :** page 500 brandee Mission Formations

---

## Sprint Studio 3 — Multi-tenant (marque blanche)

### Objectif
Chaque academie (VTC, Scolaire, IA, etc.) a son propre branding dans le MFE.

### Tache 7 — Branding par academie

**Mecanisme :** eox-tenant TenantConfig avec MFE_CONFIG par academie

**Pour chaque academie, Chloe doit fournir :**
- Logo academie (SVG + PNG)
- Favicon academie
- Couleur primaire
- Couleur secondaire
- Nom de l'academie (affiche dans le header)

**Academies prevues :**
| Academie | Sous-domaine | Org |
|----------|-------------|-----|
| VTC | vtc.academie.staging.missionformations.com | VTC |
| Scolaire (AJEP) | scolaire.academie.staging.missionformations.com | AJEP |
| IA | ia.academie.staging.missionformations.com | IA |
| Management | management.academie.staging.missionformations.com | MANAGEMENT |
| Digital | digital.academie.staging.missionformations.com | DIGITAL |
| RH | rh.academie.staging.missionformations.com | RH |
| Finance | finance.academie.staging.missionformations.com | FINANCE |
| Vente | vente.academie.staging.missionformations.com | VENTE |
| Communication | communication.academie.staging.missionformations.com | COMMUNICATION |
| Cybersecurite | cybersecurite.academie.staging.missionformations.com | CYBERSECURITE |

### Tache 8 — Branding marque blanche client

**Pour chaque client marque blanche :**
- Sous-domaine client : client.academie.missionformations.com
- Logo client
- Favicon client
- Palette couleurs client
- Configuration TenantConfig dans Django admin

**Process de creation d'un nouveau client :**
1. Creer l'organisation dans Django admin
2. Creer le Site + SiteTheme
3. Creer la Route eox-tenant
4. Creer le TenantConfig avec MFE_CONFIG personnalise
5. Ajouter le sous-domaine dans Caddy (plugin mission_multi_tenant.py)
6. Tester : homepage, login, dashboard, cours

---

## Livrables design — Resume pour Chloe

### Sprint 1 (immediat)
- [ ] Logo Mission Formations SVG + PNG (fond transparent)
- [ ] Favicon .ico (32x32, 16x16) + apple-touch-icon.png (180x180)
- [ ] Maquette header desktop + mobile
- [ ] Maquette footer desktop + mobile
- [ ] Charte couleurs complete (codes hex)

### Sprint 2
- [ ] Maquette page 404
- [ ] Maquette page 500

### Sprint 3
- [ ] Kit branding par academie (10 academies)
- [ ] Template de kit branding client marque blanche

---

## Sprint Studio 4 — Application mobile brandee Mission Formations

### Objectif
Publier une application mobile iOS + Android brandee Mission Formations sur les stores.
L'app se connecte a l'instance OpenEdX et charge le branding du client via MFE_CONFIG.

### Repos sources
- Android : https://github.com/openedx/openedx-app-android
- iOS : https://github.com/openedx/openedx-app-ios

### Taches

#### Tache 9 — Fork et branding Android
- Forker openedx-app-android
- Remplacer logo, splash screen, icone app
- Couleurs Mission Formations
- Nom de l'app : "Academie Mission Formations" (ou nom a definir)
- Configurer l'URL par defaut : academie.missionformations.com
- Builder l'APK / AAB

#### Tache 10 — Fork et branding iOS
- Forker openedx-app-ios
- Remplacer logo, splash screen, icone app
- Couleurs Mission Formations
- Nom de l'app : "Academie Mission Formations"
- Configurer l'URL par defaut
- Builder l'IPA

#### Tache 11 — Publication stores
- Compte developpeur Apple (99$/an) — requis
- Compte developpeur Google Play (25$ une fois) — requis
- Fiche store : description, screenshots, icone, categorisation
- Soumission review Apple (delai 1-3 jours)
- Publication Google Play (delai 1-2 jours)

#### Tache 12 — Multi-tenant mobile
- L'app detecte le sous-domaine du client
- Charge le branding (logo, couleurs) via l'API MFE_CONFIG
- Chaque client marque blanche voit son branding dans l'app

### Livrables design pour Chloe (Sprint 4)
- [ ] Icone app (1024x1024 PNG)
- [ ] Splash screen (logo centre sur fond couleur)
- [ ] Screenshots store (6 ecrans min, iPhone + Android)
- [ ] Description store (texte marketing)
- [ ] Feature graphic Google Play (1024x500)

### Pre-requis
- Sprint 1 termine (branding MFE fonctionnel)
- Compte Apple Developer
- Compte Google Play Developer
- API mobile OpenEdX activee sur le serveur

---

## Implementation technique

### Fichiers a modifier (Sprint 1)

| Fichier | Modification |
|---------|-------------|
| tutor_plugins/mission_mfe_branding.py | MFE_CONFIG : logo, slogan, footer links |
| Brand package (a creer) | _variables.scss : couleurs, typo |
| Brand package (a creer) | _overrides.scss : header bg, footer bg |
| Brand package (a creer) | logo.svg, logo.png, favicon.ico |

### Process de deploiement

Voir PROCESS_DEPLOIEMENT.md a la racine du repo.
- Modification MFE_CONFIG → Type 2 (plugin Tutor + config save + restart)
- Modification brand package → Type 3 (build image MFE)
