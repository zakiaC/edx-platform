# Analyse et amelioration site internet

Date: 2026-03-21
Repo analyse: `/Users/zakiachabane/edx-platform`

## 1. Perimetre retenu

Le depot courant n'est pas un repo de site marketing pur.
Le "site internet" y est embarque dans un `edx-platform` personnalise, avec une couche Mission Formations repartie entre:

- le theme LMS `themes/mission-theme/`
- le plugin Django `lms/djangoapps/mission_central_admin/`
- des routes LMS/Open edX standards (`lms/urls.py`, `openedx/core/djangoapps/user_authn/urls.py`, `lms/djangoapps/learner_dashboard/urls.py`)

Par consequent, l'inventaire ci-dessous couvre:

- les pages publiques Mission
- les pages de connexion et parcours utilisateur principaux
- les pages staff/admin custom Mission
- les pages d'erreur et pages legales/themees presentes dans le repo

Sont exclus du comptage "pages site internet":

- les endpoints API JSON
- les endpoints PDF
- les ecrans Studio natifs non lies au site public
- les tres nombreuses pages Open edX natives non specifiques a Mission Formations

## 2. Diagnostic synthese

### Ce qui est solide

- La couche Mission est assez bien isolee dans `themes/mission-theme/` et `lms/djangoapps/mission_central_admin/`.
- Les routes custom sont injectees proprement au runtime via `AppConfig.ready()` au lieu de patcher massivement `lms/urls.py`.
- Le repo contient deja les briques importantes d'un site/lms coherent: accueil, catalogue, contact, aide, dashboard, back-office, pages d'erreur.
- Les tests du projet confirment explicitement plusieurs pages et templates critiques.

### Points de fragilite et axes d'amelioration

1. Le "site internet" n'est pas isole dans un sous-projet clair.
   Aujourd'hui, les pages sont dispersees entre theme, plugin, routes LMS et patches Tutor. Pour maintenir le site, il faut connaitre plusieurs couches du produit.

2. Il existe une collision fonctionnelle sur `/contact/`.
   Le core Open edX declare deja une page `contact`, et le plugin Mission declare aussi `/contact/`. Le plugin gagne parce que ses URLs sont prepend au runtime. Ca fonctionne, mais c'est fragile et peu lisible pour la maintenance.

3. La homepage contient un lien `/handicap` qui ne correspond a aucune route trouvee dans ce repo.
   Cela ressemble a un lien casse potentiel.

4. Le widget chat est hardcode sur un domaine de staging.
   Le footer global pointe vers `https://chat.staging.missionformations.com`, ce qui est risqe si ce code sert autre chose que le staging.

5. Le catalogue depend d'images externes Unsplash.
   C'est rapide pour prototyper, mais moins bon pour la maitrise de la marque, la performance, la confidentialite et la disponibilite long terme.

6. Le theme utilise beaucoup de styles inline dans les templates.
   Le rendu peut etre rapide a ajuster, mais la maintenance devient plus couteuse que si les styles etaient centralises dans le SCSS du theme.

7. Les pages legales et institutionnelles sont hybrides.
   Une partie du parcours reste dans le LMS (`/catalogue/`, `/aide/`, `/contact/`) tandis que `about`, `privacy`, `tos`, "Qui sommes-nous", "CGU / CGV" et "Mentions legales" renvoient vers `missionformations.com`. L'experience est donc un peu morcelee.

8. Certaines pages existent comme templates, mais leur exposition reelle depend de la configuration marketing Open edX.
   C'est le cas de `about`, `privacy` et `tos`: les templates sont la, mais leur activation passe par la map marketing.

## 3. Liste des pages

### 3.1 Pages publiques confirmees

| URL | Type | Template / source principale | Observation |
| --- | --- | --- | --- |
| `/` | Publique | `themes/mission-theme/lms/templates/index.html` | Homepage Mission, route racine LMS |
| `/login` | Publique | `themes/mission-theme/lms/templates/student_account/login_and_register.html` | Ecran combine connexion/inscription |
| `/register` | Publique | `themes/mission-theme/lms/templates/student_account/login_and_register.html` | Meme page, mode inscription |
| `/password_assistance` | Publique | `themes/mission-theme/lms/templates/student_account/login_and_register.html` | Meme page, mode reset mot de passe |
| `/catalogue/` | Publique | `themes/mission-theme/lms/templates/catalogue/index.html` | Catalogue dynamique de formations |
| `/courses` | Redirection publique | `lms/djangoapps/mission_central_admin/views.py` | Redirige vers `/catalogue/` |
| `/contact/` | Publique | `lms/djangoapps/mission_central_admin/templates/mission_central_admin/contact.html` | Formulaire de contact email |
| `/aide/` | Publique | `themes/mission-theme/lms/templates/aide/index.html` | Centre d'aide Mission |
| `/courses/<course_id>/about` | Publique | `themes/mission-theme/lms/templates/courseware/course_about.html` | Page detail / enrollment d'un cours |
| `/courses/<course_id>/` | Publique | `themes/mission-theme/lms/templates/courseware/course_about.html` | Alias du detail cours |

### 3.2 Pages publiques presentes dans le repo, mais a confirmer par configuration

| URL probable | Type | Template | Observation |
| --- | --- | --- | --- |
| `/about` | Publique | `themes/mission-theme/lms/templates/static_templates/about.html` | Redirection vers `missionformations.com/a-propos/...` |
| `/privacy` | Publique | `themes/mission-theme/lms/templates/static_templates/privacy.html` | Redirection vers `missionformations.com/mentions-legales/` |
| `/tos` | Publique | `themes/mission-theme/lms/templates/static_templates/tos.html` | Redirection vers `missionformations.com/mission-formation-cgu-cgv/` |

### 3.3 Pages d'erreur et de maintenance

| URL | Type | Template | Observation |
| --- | --- | --- | --- |
| `/mission-errors/403` | Preview technique | `themes/mission-theme/lms/templates/static_templates/403.html` | Preview page 403 |
| `/mission-errors/404` | Preview technique | `themes/mission-theme/lms/templates/static_templates/404.html` | Preview page 404 |
| `/mission-errors/500` | Preview technique | `themes/mission-theme/lms/templates/static_templates/server-error.html` | Preview page 500 |
| `/maintenance` | Technique | `themes/mission-theme/lms/templates/static_templates/maintenance.html` | Page 503 |
| `/course-not-found` | Technique | `themes/mission-theme/lms/templates/static_templates/course-not-found.html` | Preview cours introuvable |
| `handler403` | Technique | `themes/mission-theme/lms/templates/static_templates/403.html` | Handler global override |
| `handler404` | Technique | `themes/mission-theme/lms/templates/static_templates/404.html` ou `course-not-found.html` | Choix selon contexte |
| `handler500` | Technique | `themes/mission-theme/lms/templates/static_templates/server-error.html` | Handler global override |

### 3.4 Pages utilisateur connecte

| URL | Type | Template / source | Observation |
| --- | --- | --- | --- |
| `/dashboard` | Authentifie | `themes/mission-theme/lms/templates/dashboard.html` | Dashboard principal utilisateur |
| `/dashboard/programs/` | Authentifie | `lms/templates/learner_dashboard/programs.html` | Liste des programmes |
| `/dashboard/programs/<program_uuid>/` | Authentifie | `lms/templates/learner_dashboard/program_details.html` | Detail programme |
| `/messagerie/interne/` | Staff | `themes/mission-theme/lms/templates/mission_internal_messaging.html` | Messagerie interne |
| `/notifications/interne/` | Staff | `themes/mission-theme/lms/templates/mission_internal_notifications.html` | Notifications internes |

### 3.5 Pages admin / back-office Mission

| URL | Type | Template | Observation |
| --- | --- | --- | --- |
| `/admin/mission-dashboard/` | Admin | `themes/mission-theme/lms/templates/admin_central_dashboard.html` | Dashboard central Mission |
| `/admin/mission-dashboard/formateur/` | Admin | `themes/mission-theme/lms/templates/admin_formateur_detail.html` | Detail formateur |
| `/admin/mission-dashboard/tests/` | Admin | `themes/mission-theme/lms/templates/admin_test_dashboard.html` | Dashboard de tests |
| `/admin/mission-dashboard/users/delete/` | Admin | `themes/mission-theme/lms/templates/admin_delete_user.html` | Suppression securisee user |
| `/academy-manager/` | Admin | `themes/mission-theme/lms/templates/academy_manager/dashboard.html` | Liste academies |
| `/academy-manager/create/` | Admin | `themes/mission-theme/lms/templates/academy_manager/create.html` | Creation academie |
| `/academy-manager/<slug>/` | Admin | `themes/mission-theme/lms/templates/academy_manager/detail.html` | Detail academie |

### 3.6 Endpoints presents mais non comptes comme "pages"

- `/api/admin/formateurs-sessions/`
- `/api/admin/formateurs-sessions/export.csv`
- `/api/admin/pdf/attestation/`
- `/api/admin/pdf/rapport-suivi/`
- `/academy-manager/<slug>/attach-course/`
- `/academy-manager/<slug>/invite/`

## 4. Risques concrets reperes dans le repo

### R1. Lien probablement casse: `/handicap`

La homepage contient:

- `themes/mission-theme/lms/templates/index.html`

mais aucune route `/handicap` n'a ete retrouvee dans le repo.

Impact:

- risque de 404 sur un lien de footer
- perte de credibilite sur un sujet sensible (accessibilite)

Action recommandee:

- soit creer une vraie page `/handicap/`
- soit remplacer ce lien par `/contact/` avec une section "referent handicap"
- soit faire pointer vers une page legale existante sur `missionformations.com`

### R2. Route `/contact/` dupliquee entre core et plugin

Le core expose deja `contact` via `lms/djangoapps/static_template_view/urls.py`.
Le plugin Mission expose aussi `/contact/` via `lms/djangoapps/mission_central_admin/urls.py`.
Le plugin gagne parce que `MissionCentralAdminConfig.ready()` prepend ses URLs dans `lms.urlpatterns`.

Impact:

- comprehension plus difficile
- effet de bord possible si la mecanique d'injection change

Action recommandee:

- documenter explicitement que la route officielle est celle du plugin
- supprimer le template de contact non utilise si possible
- ou renommer la route custom si l'on veut zero ambiguite

### R3. Chat branche sur le staging

Le footer LMS charge:

- `https://chat.staging.missionformations.com`

Impact:

- confusion entre environnements
- risque de fuite de trafic prod vers staging

Action recommandee:

- sortir l'URL du chat dans une variable de config
- injecter la valeur par environnement

### R4. Catalogue dependant d'assets externes

`catalogue_view()` utilise plusieurs URLs `images.unsplash.com`.

Impact:

- temps de chargement non maitrise
- dependance externe
- branding visuel moins controle

Action recommandee:

- heberger les visuels sur vos assets theming/CDN
- definir un jeu d'images de marque par domaine de formation

### R5. Beaucoup de styles inline

Le header et le footer Mission portent de gros blocs CSS inline directement dans les templates.

Impact:

- relecture plus difficile
- duplication potentielle
- dette de maintenance a moyen terme

Action recommandee:

- deplacer la majeure partie du CSS vers le SCSS du theme
- garder l'inline uniquement pour les overrides critiques

## 5. Priorites d'amelioration conseillees

### Priorite 1 - Fiabilite

1. Corriger ou supprimer le lien `/handicap`.
2. Externaliser les URLs d'environnement (chat, domaines, redirections) dans la config.
3. Ajouter un test d'integration simple qui verifie au minimum: `/`, `/catalogue/`, `/contact/`, `/aide/`, `/login`.

### Priorite 2 - Lisibilite du repo

1. Creer une cartographie officielle des pages Mission.
2. Documenter quelles pages viennent du theme, du plugin, du core LMS.
3. Identifier les templates "vivants" vs "fallback" vs "dead code probable".

### Priorite 3 - Experience utilisateur

1. Unifier le parcours entre LMS et `missionformations.com`.
2. Remplacer les assets externes par des assets internes.
3. Standardiser header/footer/legal pages pour eviter l'impression de site morcele.

### Priorite 4 - Maintenance front

1. Sortir les styles inline dans le pipeline SCSS du theme.
2. Regrouper les tokens visuels Mission (couleurs, espacements, typo).
3. Ajouter un inventaire de pages versionne et maintenu avec les tests.

## 6. Fichiers sources principaux utilises pour cette analyse

- `themes/mission-theme/lms/templates/index.html`
- `themes/mission-theme/lms/templates/catalogue/index.html`
- `themes/mission-theme/lms/templates/aide/index.html`
- `themes/mission-theme/lms/templates/dashboard.html`
- `themes/mission-theme/lms/templates/footer.html`
- `themes/mission-theme/lms/templates/header/header.html`
- `themes/mission-theme/lms/templates/courseware/course_about.html`
- `themes/mission-theme/lms/templates/static_templates/*.html`
- `lms/djangoapps/mission_central_admin/urls.py`
- `lms/djangoapps/mission_central_admin/views.py`
- `lms/djangoapps/mission_central_admin/error_views.py`
- `lms/djangoapps/mission_central_admin/apps.py`
- `lms/djangoapps/mission_central_admin/templates/mission_central_admin/contact.html`
- `lms/urls.py`
- `openedx/core/djangoapps/user_authn/urls.py`
- `openedx/core/djangoapps/user_authn/views/login_form.py`
- `lms/djangoapps/learner_dashboard/urls.py`
- `tests/unit/test_plugin_logic.py`
- `tests/unit/test_theme_templates.py`
- `docs/changelogs/CHANGELOG_2026-03-18.md`

## 7. Conclusion

Le repo contient bien une couche "site internet / portail public" exploitable, mais elle est imbriquee dans un `edx-platform` personnalise plutot que dans un projet web autonome.
Le plus important a court terme est de fiabiliser les liens publics, sortir les URLs d'environnement de l'HTML, et clarifier la cartographie des pages pour que chaque futur changement soit plus simple, plus rapide et moins risqe.
