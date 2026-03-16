# Checklist pré-déploiement — Mission Formations

> À valider **avant chaque mise en production** sur le VPS OVH.
> Dernière mise à jour : 2026-03-16

---

## 1. Secrets & sécurité

- [ ] **Injecter les variables d'environnement** dans les containers Docker
  - Copier `tutor-patches/.secrets.env` sur le serveur
  - Charger les vars dans Docker via `docker-compose.override.yml` ou `tutor config save`
  - Variables requises :
    ```
    MEILISEARCH_API_KEY
    MEILISEARCH_MASTER_KEY
    JWT_SECRET_KEY
    JWT_RSA_KID, JWT_RSA_E, JWT_RSA_D, JWT_RSA_N
    JWT_RSA_P, JWT_RSA_Q, JWT_RSA_DQ, JWT_RSA_DP, JWT_RSA_QI
    SOCIAL_AUTH_EDX_OAUTH2_SECRET
    ```
- [ ] **Vérifier que `.secrets.env` n'est PAS dans git** : `git status` ne doit pas le lister
- [ ] **Rotation des secrets** : les clés JWT et Meilisearch ont été exposées dans l'historique git — planifier une rotation après déploiement

---

## 2. Corrections critiques

- [x] ~~Syntaxe Python `cms-production.py` ligne 321~~ — corrigé (instructions collées sur une ligne)
- [x] ~~Secrets en dur dans `lms-production.py` et `cms-production.py`~~ — remplacés par `os.environ.get()`
- [x] ~~Nettoyer les duplications dans les tutor-patches~~ — corrigé (blocs theme_lock dupliqués supprimés dans lms et cms)

---

## 3. Thème Mission Formations

- [ ] **Vérifier les classes CSS du dashboard** : `themes/mission-theme/lms/templates/dashboard.html`
  - Lignes 172, 200, 223, 316 : classes `"reco an d2"`, `"g5 an d3"` — vérifier si le CSS correspond
- [ ] **Valider les modifications index.html** (actuellement non commité) :
  - "Formateur Nabil" au lieu de "formateurNabil"
  - "Formation stratégie commerciale HEC" au lieu de "Test formation en ligne"
  - "Formation HEC" au lieu de "Deuxième test formation"
  - → Commiter si c'est intentionnel, sinon `git restore`
- [ ] **Compiler les assets du thème** :
  ```bash
  tutor local do openedx-assets build --env=lms
  tutor local do openedx-assets collect --env=lms
  ```

---

## 4. Cours OLX (MF-VTC-2025)

- [ ] **Importer le cours** sur la plateforme :
  ```bash
  tutor local do import-demo-course  # ou import manuel via Studio
  ```
- [ ] **Vérifier le rendu** de quelques pages HTML dans Studio (s1, s2, s8)
- [ ] **Tester les quiz** (s1_1_u3, s2_1_u3, s2_2_u3, etc.)

---

## 5. Nettoyage repo

- [ ] **Supprimer ou déplacer** le fichier Excel à la racine :
  ```
  "template accompagnement UP - business plan enrichi.xlsx"
  ```
- [ ] **Ajouter au .gitignore** les fichiers business/docs volumineux (`.xlsx`, `.docx`)
- [ ] **Commiter le CLAUDE.md** si souhaité

---

## 6. Déploiement

- [ ] **Backup avant déploiement** :
  ```bash
  tutor local do backup
  # ou manuellement :
  docker exec tutor_local_mongodb_1 mongodump --out /backup/$(date +%F)
  docker exec tutor_local_mysql_1 mysqldump -u root openedx > /backup/openedx_$(date +%F).sql
  ```
- [ ] **Pull le code sur le serveur** :
  ```bash
  cd /chemin/vers/edx-platform && git pull origin staging
  ```
- [ ] **Rebuild l'image Docker** :
  ```bash
  tutor images build openedx --build-arg EDX_PLATFORM_REPOSITORY=...
  ```
- [ ] **Redémarrer** :
  ```bash
  tutor local stop && tutor local start -d
  ```
- [ ] **Vérifier le site** : https://academie.staging.missionformations.com
- [ ] **Vérifier Studio** : https://studio.staging.missionformations.com

---

## 7. Post-déploiement

- [ ] **Rotation des secrets** (JWT, Meilisearch) car exposés dans l'historique git
- [ ] **Tester le login/register** sur le thème Mission
- [ ] **Vérifier les MFE** (account, discussions, learning, authoring)
- [ ] **Monitorer les logs** pendant 30 min :
  ```bash
  tutor local logs --follow lms
  tutor local logs --follow cms
  ```
