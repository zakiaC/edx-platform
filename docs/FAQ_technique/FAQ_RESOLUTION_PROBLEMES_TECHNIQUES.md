# FAQ - Resolution de probleme technique (Mission Formations)

## Comptes demo actifs

- Formateur: `lyli.semiai@gmail.com` / `apprenant1`
- Apprenant: `semiaiabdallah@gmail.com` / `Formateur1`
- Superadmin: `chabanezakia@gmail.com` / `Superadmin`

## FAQ

### 1) Je vois `Forbidden` sur `local.openedx.io`

- Symptome:
  - Message `Forbidden` ou acces refuse.
- Cause probable:
  - La stack Tutor `local` n'est pas completement demarree (souvent seul MySQL tourne).
  - Ou la stack `dev` est active pendant que tu testes `local.openedx.io`.
- Resolution:
  - Verifier l'etat: `tutor local status`
  - Demarrer les services web: `tutor local start -d caddy lms cms`
- Prevention:
  - Toujours verifier quelle stack est active avant test (`local` vs `dev`).

### 2) Le mot de passe "ne fonctionne pas"

- Symptome:
  - Login refuse alors que le mot de passe semble correct.
- Cause probable:
  - Le mot de passe a ete change dans le mauvais conteneur (`tutor_dev-lms-1` au lieu de `tutor_local-lms-1`).
- Resolution:
  - Confirmer la stack cible.
  - Changer le mot de passe dans le conteneur LMS de la stack en cours.
- Prevention:
  - Si URL testee = `http://local.openedx.io`, alors cible BDD = `tutor_local-lms-1`.

### 3) Suppression massive des users impossible (`IntegrityError 1451`)

- Symptome:
  - Erreur SQL:
    - `Cannot delete or update a parent row: a foreign key constraint fails`
- Cause probable:
  - Des tables Open edX (ex: `course_creators`) referencent `auth_user`.
- Resolution:
  - Faire un nettoyage logique:
    - desactiver les comptes non utilises (`is_active=False`)
    - retirer privileges (`is_staff=False`, `is_superuser=False`)
    - archiver les emails si besoin
  - Conserver les comptes systeme requis.
- Prevention:
  - Eviter `delete()` global sur les users sans audit des dependances.

### 4) Page `Page non trouvee` lors du reset mot de passe

- Symptome:
  - 404 sur `/account/password/reset/` ou `/password_change`.
- Cause probable:
  - Certaines routes legacy ne sont pas toujours exposees selon la config active.
- Resolution:
  - Utiliser le flux de login/reset standard depuis `/login`.
  - Si necessaire, ajouter des redirections de compatibilite dans `lms/urls.py`.
- Prevention:
  - Standardiser les URLs de reset utilisees par le front.

### 5) Le daemon Docker est "inaccessible"

- Symptome:
  - `Cannot connect to the Docker daemon...`
- Cause probable:
  - Docker Desktop non demarre, ou permission socket non accordee.
- Resolution:
  - Relancer Docker Desktop.
  - Reexecuter les commandes Tutor apres verification `docker ps`.
- Prevention:
  - Verifier Docker avant operations BDD ou restart Tutor.

### 6) Confusion entre roles (apprenant/formateur/admin)

- Symptome:
  - Mauvais dashboard apres login.
- Cause probable:
  - Mauvais flags de role (`is_staff`, `is_superuser`) ou compte non actif.
- Resolution:
  - Verifier pour chaque compte:
    - `is_active`
    - `is_staff`
    - `is_superuser`
  - Reappliquer la matrice role attendue.
- Prevention:
  - Maintenir un "jeu de comptes demo" documente et stable.

## Check-list rapide avant demo

- La stack `local` est active.
- `caddy`, `lms`, `cms` sont `Up`.
- Les 3 comptes demo sont actifs avec les bons roles.
- Le reset mot de passe se fait depuis `/login`.
- Les routes dashboard repondent:
  - `/dashboard`
  - `/admin/mission-dashboard/`
