# Compte-rendu de reunion — 12 avril 2026

## Participants
- Zakia (PM)
- Allyah (Specialiste OpenEdX)
- Ishaq (Specialiste DevOps)
- Claude (DevOps Mission, responsable deploiement)

## Duree : ~8 heures

---

## Objectif initial
Customiser le header et footer du Studio (CMS) :
1. Agrandir le logo dans le header
2. Remplacer le logo footer par celui de Mission
3. Remplacer le texte "edX and Open edX logos are registered trademarks" par "Donnez du sens a votre parcours!"

---

## Chronologie des evenements

### Phase 1 — Constat initial
- Audit du theme : le CMS n'a que 4 fichiers customises (footer, user_dropdown, sock_links)
- Le LMS a 70+ fichiers customises, le CMS est quasi brut OpenEdX
- Decision : commencer par le header et le footer

### Phase 2 — Premieres tentatives (echecs)
- Creation de header.html et footer.html custom dans le theme CMS
- Copie du logo dans cms/static/images/studio-logo.png
- Probleme : docker cp vers le mauvais chemin (/openedx/edx-platform/themes/ au lieu de /openedx/themes/)
- Probleme : les dossiers n'existaient pas dans le container CMS
- Probleme : le deploy.sh ne gerait que le LMS, pas le CMS

### Phase 3 — Tentative de rebuild image (regression majeure)
- Claude a lance `tutor images build openedx`
- REGRESSION : le LMS a crashe — ModuleNotFoundError: No module named 'eox_tenant'
- Cause : eox-tenant n'etait pas dans OPENEDX_EXTRA_PIP_REQUIREMENTS
- Correction : ajout de eox-tenant dans OPENEDX_EXTRA_PIP_REQUIREMENTS
- Nouveau rebuild necessaire (~30 min)
- Le theme LMS a disparu apres le rebuild (image neuve sans theme)
- Restauration via deploy.sh staging depuis la machine locale

### Phase 4 — Decouverte du vrai probleme
- Allyah identifie que TOUTES les pages Studio sont rendues par le MFE course-authoring
- Le MFE est une app React hebergee sur apps.academie.staging.missionformations.com
- Les templates Mako (header.html, footer.html) ne sont JAMAIS rendus
- Toutes nos modifications etaient invisibles car le MFE bypass les templates
- Confirmation : quand on ouvre une page Studio, l'URL redirige vers le MFE

### Phase 5 — Investigation MFE_CONFIG
- Le MFE lit sa config via l'API /api/mfe_config/v1
- Ishaq verifie : les settings sont dans /openedx/edx-platform/lms/envs/tutor/production.py
- Ce fichier est GENERE par Tutor via les plugins, pas editable directement
- Notre fichier tutor-patches/lms-production.py n'etait PAS charge par Tutor
- Les variables INDIGO_FOOTER_SLOGAN, SHOW_POWERED_BY_OPENEDX = PAS DEFINI

### Phase 6 — Solution : plugin Tutor
- Creation du plugin mission_mfe_branding.py
- Le plugin injecte via le patch "openedx-lms-common-settings"
- Installation : copie dans /root/.local/share/tutor-plugins/ + tutor plugins enable
- tutor config save + tutor local restart lms
- Verification : SLOGAN = "Donnez du sens a votre parcours!", POWERED = False
- L'API /api/mfe_config/v1 retourne les bonnes valeurs

### Phase 7 — Mais toujours pas visible
- Allyah decouvre que le footer MFE par defaut ne supporte PAS les variables INDIGO_*
- Le plugin tutor-indigo est necessaire pour avoir un footer qui lit ces variables
- tutor-indigo n'etait pas installe

### Phase 8 — Installation tutor-indigo (en cours)
- pip install tutor-indigo sur le VPS
- tutor plugins enable indigo
- tutor images build --no-cache mfe (build de toutes les apps MFE React)
- Le build a plante (probable manque de RAM — 8 apps React en parallele sur 16 Go)
- Zakia a du arreter le processus SSH

---

## Problemes identifies

### Technique
1. **Studio = MFE** : les templates Mako ne sont pas utilises, toute customisation passe par MFE_CONFIG + plugins Tutor
2. **tutor-patches pas charge** : le fichier lms-production.py custom n'est pas inclus dans les settings Tutor generes
3. **deploy.sh incomplet** : ne gerait que le LMS, pas le CMS — corrige ce jour
4. **Chemin container** : /openedx/themes/ (pas /openedx/edx-platform/themes/) — corrige ce jour
5. **eox-tenant fragile** : se perd a chaque rebuild d'image si pas dans OPENEDX_EXTRA_PIP_REQUIREMENTS — corrige ce jour
6. **RAM insuffisante** : le build MFE (8 apps React) depasse les 16 Go de RAM du VPS

### Process
1. **Pas de process de deploiement documente** — corrige ce jour (PROCESS_DEPLOIEMENT.md)
2. **Pas de cahier de charge Studio** — corrige ce jour (CAHIER_DE_CHARGE_STUDIO.md)
3. **Confusion machine locale vs VPS** : plusieurs commandes executees au mauvais endroit
4. **Trop de tentatives sans diagnostic prealable** : on a modifie avant de comprendre

---

## Decisions prises

1. **Garder le MFE** (pas le desactiver) — vision long terme multi-clients
2. **Plugin Tutor** pour toute config MFE — pas de fichier patch manuel
3. **tutor-indigo** necessaire pour le footer custom
4. **Application mobile brandee** : repos crees (mission-app-android, mission-app-ios)
5. **Cahier de charge en 4 sprints** : branding MFE, pages Mako, multi-tenant, app mobile

---

## Corrections effectuees

| Correction | Fichier | Commit |
|-----------|---------|--------|
| deploy.sh avec etapes CMS | deploy.sh | feat(deploy) |
| Chemin CMS corrige /openedx/themes/ | deploy.sh | fix(deploy) |
| Plugin branding MFE | tutor_plugins/mission_mfe_branding.py | feat(mfe) |
| eox-tenant dans OPENEDX_EXTRA_PIP_REQUIREMENTS | tutor config VPS | — |
| Process deploiement | PROCESS_DEPLOIEMENT.md | docs |
| Cahier de charge Studio | CAHIER_DE_CHARGE_STUDIO.md | docs |
| Guide plugins Tutor | diagnostics/2026-04-12_plugins-tutor-guide.md | docs |
| Audit complet | diagnostics/2026-04-12_audit-studio-deploy.md | docs |

---

## A faire demain (13 avril)

### Priorite 1 — Build MFE
- Ajouter du swap sur le VPS (4 Go) pour eviter le crash RAM
- Relancer tutor images build --no-cache mfe
- tutor local stop && tutor local start -d
- Verifier : slogan visible, texte edX disparu, logo Mission visible

### Priorite 2 — Validation visuelle
- Tester toutes les pages Studio
- Screenshots avant/apres
- Valider avec Zakia

### Priorite 3 — Design avec Chloe
- Brief design : logo SVG/PNG, favicon, maquettes header/footer, charte couleurs
- Voir CAHIER_DE_CHARGE_STUDIO.md Sprint 1 livrables

### Priorite 4 — App mobile
- Configurer mission-app-ios et mission-app-android
- Tester sur simulateur Xcode

---

## Lecons apprises

1. **Toujours diagnostiquer avant d'agir** : comprendre l'architecture (MFE vs Mako) avant de modifier
2. **Ne jamais rebuilder une image Docker sans verifier les dependances**
3. **Les plugins Tutor sont la seule facon fiable d'injecter des settings**
4. **Le docker cp est un raccourci fragile** qui se perd a chaque rebuild
5. **Documenter chaque process** pour eviter de repeter les memes erreurs
6. **Le VPS a 16 Go de RAM** : insuffisant pour builder 8 apps React en parallele sans swap
