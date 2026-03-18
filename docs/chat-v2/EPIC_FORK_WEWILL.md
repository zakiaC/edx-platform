# Epic — Fork WeWill (Chatwoot) : Chat 100% independant

> Objectif : forker Chatwoot, rebrander entierement en WeWill,
> builder notre propre image Docker, supprimer toute dependance au tiers.
> Priorite : Moyenne (apres mise en prod du LMS)

---

## Contexte

### Ce qui a ete fait (Chat v1 — actuel)

| Element | Statut | Detail |
|---------|--------|--------|
| Chatwoot self-hosted | Fait | 4 containers Docker sur le VPS OVH |
| Widget sur le LMS | Fait | footer.html, toutes les pages |
| SSL automatique | Fait | Caddy + Let's Encrypt |
| Plugin Tutor | Fait | mission_wewill.py (reverse proxy Caddy) |
| Compte admin | Fait | admin@missionformations.com |
| Inbox Website | Fait | Token: SqDrn962MP4DfDkr6qdWFJ9f |
| Documentation equipe | Fait | docs/ops/WEWILL_GUIDE_EQUIPE.md |
| Documentation client | Fait | docs/ops/WEWILL_GUIDE_CLIENT.md |
| Documentation technique | Fait | docs/ops/WEWILL.md |

### Ce qui reste a faire (Chat v2 — ce document)

| Element | Statut | Bloquant |
|---------|--------|----------|
| Branding "Propulse par Chatwoot" | A faire | Visible par les clients |
| Fork du repo GitHub | A faire | Prerequis pour tout le reste |
| Rebranding complet WeWill | A faire | Interface admin + widget |
| Image Docker custom | A faire | Independance Docker Hub |
| Registry prive | A faire | Hebergement de l'image |
| Messages d'erreur en francais | A faire | UX (ex: mot de passe) |
| Customisation interface | A faire | Couleurs MF, logo, textes |

---

## Tickets Jira

### CHAT-1 : Fork du repo Chatwoot
- **Type** : Tache technique
- **Priorite** : Haute
- **Estimation** : 1h
- **Description** :
  - Forker `github.com/chatwoot/chatwoot` vers `github.com/zakiaC/wewill-chat`
  - Creer la branche `main` depuis le tag stable le plus recent
  - Ajouter le remote upstream pour les futures mises a jour
- **Critere d'acceptation** : Le repo forke est accessible et buildable
- **Commandes** :
  ```bash
  gh repo fork chatwoot/chatwoot --clone --remote-name upstream
  git remote rename origin wewill
  ```

---

### CHAT-2 : Rebranding complet Chatwoot → WeWill
- **Type** : Tache technique
- **Priorite** : Haute
- **Estimation** : 4h
- **Description** :
  - Remplacer toutes les occurrences de "Chatwoot" par "WeWill" dans :
    - Interface admin (sidebar, header, titres de pages)
    - Widget chat (texte "Propulse par Chatwoot")
    - Emails transactionnels (templates)
    - Page de login / onboarding
    - Favicon et logo
  - Fichiers concernes :
    - `app/javascript/widget/` (widget JS)
    - `app/views/` (templates Rails)
    - `app/assets/` (images, logos)
    - `config/locales/` (traductions)
    - `public/` (favicon, manifest)
- **Critere d'acceptation** : Zero occurrence de "Chatwoot" visible par l'utilisateur final
- **Dependance** : CHAT-1

---

### CHAT-3 : Charte graphique Mission Formations
- **Type** : Tache design
- **Priorite** : Moyenne
- **Estimation** : 3h
- **Description** :
  - Appliquer les couleurs Mission Formations :
    - Primaire : #0965D0
    - Secondaire : #01E8AE
    - Dark : #0a1628
  - Polices : Ubuntu (titres) + Raleway (corps)
  - Logo "M" gradient bleu-vert dans le widget
  - Fond sombre pour le header du widget
  - Bouton bulle avec le gradient MF
- **Fichiers** :
  - `app/javascript/widget/assets/scss/` (styles widget)
  - `app/javascript/dashboard/assets/scss/` (styles admin)
  - `app/assets/images/` (logos)
- **Critere d'acceptation** : Widget et admin alignes visuellement avec le LMS
- **Dependance** : CHAT-1

---

### CHAT-4 : Traduction francaise complete
- **Type** : Tache
- **Priorite** : Moyenne
- **Estimation** : 2h
- **Description** :
  - Completer / corriger les traductions francaises dans `config/locales/fr.yml`
  - Messages d'erreur user-friendly en francais :
    - "Password must contain special character" → "Le mot de passe doit contenir au moins un caractere special (!@#$...)"
    - Tous les messages de validation du formulaire
  - Interface admin : verifier que tous les menus sont traduits
  - Widget : verifier les textes par defaut (bienvenue, hors ligne, CSAT)
- **Critere d'acceptation** : Zero texte anglais visible dans l'interface
- **Dependance** : CHAT-1

---

### CHAT-5 : Build image Docker custom
- **Type** : Tache DevOps
- **Priorite** : Haute
- **Estimation** : 2h
- **Description** :
  - Creer un Dockerfile base sur le Dockerfile officiel Chatwoot
  - Builder l'image avec les modifications (CHAT-2, CHAT-3, CHAT-4)
  - Taguer l'image : `ghcr.io/zakiac/wewill-chat:latest`
  - Pusher sur GitHub Container Registry (GHCR)
  - Modifier `/root/chatwoot/docker-compose.yaml` sur le serveur :
    ```yaml
    image: ghcr.io/zakiac/wewill-chat:latest  # au lieu de chatwoot/chatwoot:latest
    ```
- **Critere d'acceptation** : L'image custom tourne sur le VPS sans dependance Docker Hub
- **Dependance** : CHAT-2, CHAT-3, CHAT-4

---

### CHAT-6 : CI/CD automatique (GitHub Actions)
- **Type** : Tache DevOps
- **Priorite** : Basse
- **Estimation** : 2h
- **Description** :
  - Creer `.github/workflows/build.yml` dans le repo forke
  - A chaque push sur `main` :
    1. Build l'image Docker
    2. Push sur GHCR
    3. (Optionnel) Deploy automatique sur le VPS via SSH
  - A chaque nouvelle release upstream Chatwoot :
    - Merge les changements upstream
    - Rebuild l'image
- **Critere d'acceptation** : Push sur main → image disponible sur GHCR en <10min
- **Dependance** : CHAT-5

---

### CHAT-7 : Migration de l'installation existante
- **Type** : Tache ops
- **Priorite** : Haute
- **Estimation** : 1h
- **Description** :
  - Arreter les containers actuels
  - Modifier docker-compose.yaml pour pointer vers la nouvelle image
  - Relancer les containers
  - Verifier que les donnees sont intactes (conversations, contacts, inbox)
  - Tester le widget sur le LMS
- **Critere d'acceptation** : Widget fonctionne avec la nouvelle image, zero perte de donnees
- **Dependance** : CHAT-5

---

### CHAT-8 : Procedure de mise a jour upstream
- **Type** : Documentation
- **Priorite** : Moyenne
- **Estimation** : 1h
- **Description** :
  - Documenter la procedure pour integrer les mises a jour Chatwoot :
    ```bash
    cd wewill-chat
    git fetch upstream
    git merge upstream/main
    # Resoudre les conflits sur les fichiers rebrandés
    docker build -t ghcr.io/zakiac/wewill-chat:latest .
    docker push ghcr.io/zakiac/wewill-chat:latest
    # Sur le serveur :
    cd /root/chatwoot && docker compose pull && docker compose up -d
    ```
  - Documenter les fichiers a risque de conflit (ceux modifies dans CHAT-2/3/4)
- **Critere d'acceptation** : Un developpeur peut faire la mise a jour en suivant le guide
- **Dependance** : CHAT-5

---

### CHAT-9 : Customisations fonctionnelles (optionnel)
- **Type** : Feature
- **Priorite** : Basse
- **Estimation** : 4-8h
- **Description** :
  - Ajouter des fonctionnalites custom :
    - Integration directe avec OpenEdX (creation automatique de contact LMS → WeWill)
    - Widget contextuel : afficher le nom du cours dans lequel l'apprenant se trouve
    - Bot de pre-qualification connecte aux FAQ du centre d'aide (/aide/)
    - Webhook → Odoo pour creer un lead a chaque nouvelle conversation
- **Dependance** : CHAT-5, Odoo integration (Sprint 4 cahier des charges)

---

## Planning estime

| Semaine | Tickets | Effort |
|---------|---------|--------|
| 1 | CHAT-1 + CHAT-2 + CHAT-4 | 7h |
| 2 | CHAT-3 + CHAT-5 + CHAT-7 | 6h |
| 3 | CHAT-6 + CHAT-8 | 3h |
| Futur | CHAT-9 | 4-8h |
| **Total** | **9 tickets** | **~20h** |

---

## Risques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Conflits lors des merges upstream | Moyen | Limiter les modifications aux fichiers de branding |
| Image Docker trop lourde | Faible | Utiliser le Dockerfile officiel comme base |
| Regression apres mise a jour | Moyen | Tests automatiques dans le CI/CD |
| Chatwoot change de licence | Faible | Le code est MIT — le fork reste libre |
