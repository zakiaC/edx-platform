# TODO — Multi-tenant (pages et filtrage a completer)

> Date : 23 mars 2026
> Statut : multi-tenant operationnel (DNS + Caddy + eox-tenant + filtrage catalogue)
> Reste a faire : adapter les pages custom pour le multi-tenant

---

## Fait

- [x] DNS wildcard *.academie.staging.missionformations.com
- [x] Caddy SSL pour les 9 sous-domaines
- [x] ALLOWED_HOSTS wildcard
- [x] eox-tenant installe et configure (TenantConfig + Route + TenantOrganization)
- [x] 9 academies creees (VTC, IA, Management, Digital, RH, Finance, Vente, Communication, Cybersecurite)
- [x] Filtrage catalogue /catalogue/ par org du tenant

## A faire — Pages a adapter pour le multi-tenant

### Priorite haute

- [ ] **Homepage (index.html)** : affiche 3 cours hardcodes → doit afficher les cours de l'academie du tenant
- [ ] **Dashboard apprenant (dashboard.html)** : affiche tous les cours → doit filtrer par org du tenant
- [ ] **Dashboard admin (admin_central_dashboard.html)** : KPIs globaux → ajouter filtre par academie
- [ ] **Header** : nom plateforme → doit afficher le nom de l'academie (PLATFORM_NAME du tenant)
- [ ] **Footer** : liens → adapter au contexte du tenant

### Priorite moyenne

- [ ] **Page about du cours** : verifier que le branding du tenant s'applique
- [ ] **Certificats** : verifier que le certificat utilise le design de l'org du tenant (deja mappe par org — a tester)
- [ ] **Emails** : l'expediteur et le logo doivent correspondre au tenant
- [ ] **Chat WeWill** : identifier le sous-domaine dans les metadata de la conversation
- [ ] **Page login/register** : branding du tenant (logo, couleurs, nom)

### Priorite basse (marque blanche)

- [ ] **Branding complet par tenant** : logo, couleurs, favicon injectes par eox-tenant (theming_configs)
- [ ] **Zero mention Mission Formations** pour les clients marque blanche
- [ ] **Domaine custom client** : formation.client.com (CNAME + config Caddy + tenant)
- [ ] **Emails expediteur custom** : formation@client.com au lieu de @missionformations.com

## A faire — Fonctionnel

- [ ] **Academy Manager** : creer un tenant automatiquement quand on cree une academie
- [ ] **Cross-selling Canal A** : bandeau "Decouvrez aussi" dans le dashboard apprenant
- [ ] **Cross-selling Canal B** : email de recommandation J+7 apres fin de formation
- [ ] **Cross-selling Canal C** : catalogue global avec filtre par academie
- [ ] **Facturation par tenant** : comptage apprenants par academie dans Odoo

## A faire — Integration emargement dans les dashboards LMS

- [ ] **Dashboard admin** : ajouter onglet "Emargement" (appel API Qualiopi /emargement/dashboard/ en AJAX)
- [ ] **Dashboard admin** : liste des signatures par session (appel API /emargement/signatures/)
- [ ] **Dashboard admin** : bouton "Generer QR code" pour le presentiel
- [ ] **Dashboard apprenant** : section "Mon assiduite" (appel API /emargement/logs/?user_id=...)
- [ ] **Dashboard apprenant** : historique des signatures presentiel
- [ ] **Fiche apprenant** : assiduite visible quand l'admin consulte un apprenant
