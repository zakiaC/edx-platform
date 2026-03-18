# Diagnostic de stabilite — Pret pour la production ?

> Audit du 18 mars 2026 — avis objectif sur les 3 sites (LMS, Studio, WeWill)

---

## Verdict global

| Site | Statut | Pret prod ? |
|------|--------|-------------|
| **LMS** (academie.staging.missionformations.com) | Fonctionnel | **NON** — failles a corriger |
| **Studio** (studio.staging.missionformations.com) | Fonctionnel | **PARTIEL** — customisation minimale |
| **WeWill** (chat.staging.missionformations.com) | Fonctionnel | **PARTIEL** — branding Chatwoot visible |

**Recommandation : NE PAS mettre en prod en l'etat.** Il y a des risques de stabilite, des failles de securite et des fonctionnalites incompletes qui donneraient une mauvaise premiere impression.

---

## 1. FAILLES CRITIQUES (bloquantes pour la prod)

### 1.1 Securite — Secrets exposes dans l'historique Git
- **Risque** : CRITIQUE
- **Detail** : Les cles JWT, Meilisearch, OAuth2 ont ete commitees en clair avant d'etre externalisees. Elles sont toujours dans l'historique git.
- **Impact** : Toute personne avec acces au repo peut lire les secrets de production
- **Fix** : Generer de NOUVEAUX secrets pour la prod (pas les memes que staging)
- **Effort** : 1h

### 1.2 Stabilite — Disque a 85%
- **Risque** : HAUT
- **Detail** : Le VPS a 16 Go libres sur 75 Go. Avec les logs Docker, les uploads et la croissance de la BDD, le disque peut se remplir en quelques semaines.
- **Impact** : Quand le disque est plein, MySQL crash → 500 sur tout le site
- **Fix** : Nettoyer (`docker system prune`), agrandir le disque, ou mettre en place une rotation des logs
- **Effort** : 1h

### 1.3 Stabilite — RAM a 79%
- **Risque** : MOYEN-HAUT
- **Detail** : 6.1 Go utilises sur 7.7 Go. Avec 18 containers Docker (OpenEdX + WeWill), il n'y a pas de marge. Un pic de charge peut declencher l'OOM killer.
- **Impact** : MySQL ou MongoDB tue par le kernel → 500
- **Fix** : Augmenter la RAM du VPS (16 Go recommande) ou optimiser les containers
- **Effort** : Upgrade VPS (10 min) ou optimisation (2h)

### 1.4 Base de donnees — Migrations fake-applied
- **Risque** : MOYEN
- **Detail** : Lors du deploiement, on a fait `migrate --fake` sur plusieurs apps pour contourner des tables manquantes. Certaines tables peuvent ne pas correspondre au schema attendu.
- **Impact** : Erreurs aleatoires sur des fonctionnalites specifiques
- **Fix** : Audit complet des migrations, recreer les tables manquantes proprement
- **Effort** : 3h

### 1.5 Base de donnees — Site Django ID 2 avec domaine temporaire
- **Risque** : MOYEN
- **Detail** : Le site ID 2 a ete recree avec "lms.staging.missionformations.com" au lieu de "academie.staging.missionformations.com". SITE_ID=2 dans les settings.
- **Impact** : Les emails et certaines fonctionnalites utilisent le mauvais domaine
- **Fix** : Mettre a jour le domaine du site ID 2 ou changer SITE_ID
- **Effort** : 15min

---

## 2. FAILLES MOYENNES (a corriger avant ou juste apres la prod)

### 2.1 Pas de backup automatique
- **Risque** : MOYEN
- **Detail** : Aucun backup automatique configure. Si le serveur crash, les donnees sont perdues.
- **Contenus concernes** : MySQL (users, enrollments, grades), MongoDB (cours), PostgreSQL (WeWill conversations)
- **Fix** : Cron job quotidien avec retention 7 jours + upload S3/Backblaze
- **Effort** : 2h

### 2.2 Pas de monitoring
- **Risque** : MOYEN
- **Detail** : Aucune alerte si un container tombe, si le disque se remplit, ou si le site est down
- **Fix** : Healthcheck + notification (email ou Slack) si container down
- **Effort** : 2h

### 2.3 Middleware InactiveUserLogoutMiddleware — risque de regression
- **Risque** : MOYEN
- **Detail** : Le middleware custom a deja cause un crash 500 global (heartbeat). Le fix est en place mais il n'a pas de tests unitaires dedies.
- **Fix** : Ecrire des tests pour le middleware (chemin exempt, user absent, user inactif, user actif)
- **Effort** : 1h

### 2.4 WeWill — branding Chatwoot visible
- **Risque** : FAIBLE-MOYEN
- **Detail** : Le texte "Propulse par Chatwoot" est visible dans l'iframe du widget. Le CSS ne peut pas le masquer (iframe cross-origin).
- **Impact** : Image de marque non coherente
- **Fix** : Fork WeWill (Epic CHAT, ~20h)
- **Effort** : 20h (projet separe)

### 2.5 8 cours sur 10 sont vides
- **Risque** : MOYEN
- **Detail** : Seuls les 2 cours VTC ont du contenu. Les 8 autres (IA, Management, RH, etc.) sont des coquilles vides dans Studio.
- **Impact** : Les apprenants qui s'inscrivent ne trouvent aucun contenu
- **Fix** : Creer le contenu ou masquer les cours vides
- **Effort** : 8h par cours (estimation)

---

## 3. POINTS FAIBLES (ameliorations recommandees)

### LMS

| Point | Detail | Impact |
|-------|--------|--------|
| Dashboard apprenant | Recommandations, events, activite, badges hardcodes | UX incomplete |
| Dashboard admin | 6 onglets sur 14 sont des placeholders | Admin frustre |
| Certificats | Aucun template de certificat configure | Les apprenants ne peuvent pas obtenir de certificat |
| Page progression | Pas d'override dans le theme (design natif OpenEdX) | Incoherence visuelle |
| Academy Manager | Teste mais les academies ne s'affichent pas toujours | Bug Mako a verifier |
| Recommandations | Hardcodees, pas d'algorithme | Pas pertinent pour l'apprenant |

### Studio

| Point | Detail | Impact |
|-------|--------|--------|
| Header | Design natif OpenEdX, pas brande | Incoherence avec le LMS |
| Page d'accueil | Logo et textes OpenEdX par defaut | Premiere impression non professionnelle |
| Traductions | Certains textes en anglais | UX formateur francophone |
| Dropdown creation cours | Organisations MF pas toujours visibles | Formateur ne peut pas creer un cours |

### WeWill (chat)

| Point | Detail | Impact |
|-------|--------|--------|
| Branding | "Chatwoot" visible | Confusion marque |
| Pas de bot | Pas de reponses automatiques configurees | Equipe doit repondre manuellement |
| Pas de SMTP | Emails de notification non configures | Les agents ne sont pas prevenus |

---

## 4. POINTS FORTS (ce qui est pret)

| Element | Statut | Detail |
|---------|--------|--------|
| Theme complet | SOLIDE | Header, footer, login, register, dashboard, erreurs — tout brande MF |
| Architecture code | SOLIDE | 0 fichier natif modifie, tout dans le theme et le plugin |
| Tests | SOLIDE | 178 tests automatises, diagnostic SSH, deploy health |
| Deploy script | SOLIDE | deploy.sh avec sync container, cache Mako, collectstatic |
| Plugin Tutor | SOLIDE | 8 plugins portables et configurables |
| Pages publiques | SOLIDE | Homepage, catalogue, inscription, aide, contact — tout fonctionne |
| Chat self-hosted | FONCTIONNEL | Widget sur toutes les pages, admin accessible |
| Academy Manager | FONCTIONNEL | 12 academies, CRUD, rattachement cours |
| Rapports PDF | FONCTIONNEL | Attestation + suivi, Qualiopi-compatible |

---

## 5. MON AVIS POUR LA MISE EN PROD

### Ce qu'il faut faire AVANT la prod (bloquant)

1. **Nouveaux secrets** pour la prod (1h)
2. **Augmenter la RAM** a 16 Go (10 min + cout VPS)
3. **Nettoyer le disque** (30 min)
4. **Corriger le Site ID 2** (15 min)
5. **Configurer les certificats** (au moins 2-3 templates pour les cours actifs) (3h)
6. **Masquer les cours vides** ou creer du contenu minimal (2h)
7. **Configurer les backups** (2h)
8. **Tester le parcours complet** : inscription → cours → quiz → certificat (2h)

**Effort minimum avant prod : ~12h**

### Ce qu'on peut faire apres la prod (non bloquant)

- Dashboard admin onglets placeholder (connecter progressivement)
- Dashboard apprenant hardcode (ameliorer progressivement)
- Customisation Studio (fonctionnel en natif)
- Module Qualiopi (necessaire pour les audits, pas pour les apprenants)
- Fork WeWill (le branding Chatwoot n'est pas bloquant)
- Guides utilisateurs (le centre d'aide couvre l'essentiel)

### Timeline recommandee

| Semaine | Objectif |
|---------|----------|
| S1 | Corriger les failles critiques (secrets, RAM, disque, Site ID) |
| S2 | Certificats + contenu minimal des cours + backups |
| S3 | Test complet avec 5 stagiaires reels |
| S4 | **GO LIVE** production |
| S5-S8 | Ameliorations post-prod (dashboard, Qualiopi, Studio, guides) |
