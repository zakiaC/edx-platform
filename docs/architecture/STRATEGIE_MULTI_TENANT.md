# Strategie Multi-Tenant — Mission Formations

> Version 1.0 — 23 mars 2026
> Vision holistique : LMS + Dashboard + Odoo + Qualiopi + Signature + Site + Chat
> Objectif : chaque academie = un espace dedie avec son branding, ses formations, ses apprenants

---

## 1. VISION CIBLE

```
                        missionformations.com (site vitrine)
                                    │
                                    │ "Je veux m'inscrire"
                                    ▼
                    academie.missionformations.com (portail)
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        vtc.academie.mf.com  ia.academie.mf.com  rh.academie.mf.com
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Logo VTC     │    │ Logo IA      │    │ Logo RH      │
        │ Couleurs VTC │    │ Couleurs IA  │    │ Couleurs RH  │
        │ Formations:  │    │ Formations:  │    │ Formations:  │
        │ - Certif VTC │    │ - IA Entrep  │    │ - Droit trav │
        │ - Anglais VTC│    │ - Workflow IA│    │ - Gestion RH │
        │ - Securite   │    │              │    │              │
        │ Formateurs:  │    │ Formateurs:  │    │ Formateurs:  │
        │ - Ahmed      │    │ - Sophie     │    │ - Marie      │
        └──────────────┘    └──────────────┘    └──────────────┘
                │                   │                   │
                └───────────────────┴───────────────────┘
                                    │
                        Meme LMS OpenEdX (une seule instance)
                        Meme base de donnees
                        Meme Odoo, meme Qualiopi, meme Chat
```

---

## 2. CE QUI EXISTE DEJA

### 2.1 Modele Academy (mission_central_admin)

```python
class Academy(models.Model):
    name = CharField(max_length=200)
    slug = SlugField(unique=True)          # ex: "vtc", "ia", "management"
    org_id = CharField(max_length=50)       # ex: "MF-VTC", "MF-IA"
    site_id = IntegerField(null=True)       # Django Site ID
    subdomain = CharField(max_length=100)   # ex: "vtc.academie"
    academy_type = CharField(choices=[INTERNAL, B2B])
    client_name = CharField(null=True)      # Nom entreprise B2B
    client_contact = EmailField(null=True)  # Contact RH
    contract_start = DateField(null=True)
    contract_end = DateField(null=True)
    max_seats = IntegerField(default=0)     # Places max B2B
    logo_url = URLField(null=True)
    primary_color = CharField(null=True)    # ex: "#0965D0"
    secondary_color = CharField(null=True)  # ex: "#01E8AE"
    is_active = BooleanField(default=True)
```

### 2.2 Academy Manager (dashboard admin)

Le dashboard admin a deja un onglet "Academy Manager" (`/academy-manager/`) qui permet de :
- Creer une academie
- Voir la liste des academies
- Voir le detail d'une academie (cours, apprenants, stats)

### 2.3 eox-tenant (installe mais pas configure)

Le plugin `eox-tenant` d'Edunext est dans le repo. Il permet :
- Multi-site Django (un Site par sous-domaine)
- Branding dynamique (logo, couleurs par site)
- Filtrage des cours par organisation
- Routing des sous-domaines

### 2.4 Organisations OpenEdX

Les 10 formations utilisent deja des organisations separees :

| Org | Domaine | Nb formations |
|-----|---------|--------------|
| MF-VTC | Transport VTC | 3 |
| MF-IA | Intelligence Artificielle | 2 |
| MF-MGMT | Management | 1 |
| MF-DIGITAL | Digital / Bureautique | 1 |
| MF-RH | Ressources Humaines | 1 |
| MF-FINANCE | Finance / Comptabilite | 1 |
| MF-VENTE | Vente / Negociation | 1 |
| MissionFormations | General | 1 |

---

## 3. ARCHITECTURE MULTI-TENANT RECOMMANDEE

### 3.1 Option retenue : sous-domaines + eox-tenant

Chaque academie = un sous-domaine qui pointe vers la meme instance OpenEdX.

```
DNS :
  *.academie.missionformations.com → IP du VPS (wildcard)

Caddy :
  *.academie.missionformations.com → reverse_proxy LMS :8000

eox-tenant :
  vtc.academie.mf.com → Site ID 3, org=MF-VTC, theme=mission-vtc
  ia.academie.mf.com  → Site ID 4, org=MF-IA, theme=mission-ia
  rh.academie.mf.com  → Site ID 5, org=MF-RH, theme=mission-rh

LMS :
  Detecte le sous-domaine → charge la config tenant → filtre les cours par org
```

### 3.2 Ce que chaque tenant a de different

| Element | Global (partage) | Par tenant (specifique) |
|---------|-----------------|----------------------|
| Instance LMS | ✅ Une seule | — |
| Base MySQL | ✅ Une seule | — |
| Base MongoDB | ✅ Une seule | — |
| Studio | ✅ Un seul | — |
| Users / comptes | ✅ Partages (un user peut etre dans plusieurs academies) | — |
| URL | — | ✅ vtc.academie.mf.com |
| Logo | — | ✅ Logo de l'academie |
| Couleurs | — | ✅ Couleurs de l'academie |
| Cours visibles | — | ✅ Filtres par org (MF-VTC ne voit que les cours VTC) |
| Certificats | — | ✅ Design different par org (deja fait — 20 templates) |
| Dashboard apprenant | — | ✅ Ne montre que les cours de l'academie |
| Formateurs | — | ✅ Formateurs rattaches a l'academie |
| Page d'accueil | — | ✅ Homepage specifique a l'academie |

---

## 4. IMPACT SUR CHAQUE BRIQUE

### 4.1 Dashboard Admin (Academy Manager)

**Etat actuel** : le dashboard a un onglet Academy Manager avec CRUD basique.

**Ce qu'il faut ajouter** :

| Fonctionnalite | Detail |
|----------------|--------|
| Creation d'academie → creation automatique du tenant | Creer le Django Site + la config eox-tenant + le DNS |
| Dashboard par academie | Vue filtree : KPIs, apprenants, formateurs, CA de CETTE academie |
| Gestion des cours par academie | Rattacher / detacher des cours (AcademyCourse) |
| Gestion des formateurs par academie | Rattacher / detacher des formateurs |
| Branding par academie | Upload logo, choix couleurs, preview |
| Stats par academie | Taux completion, satisfaction, CA — filtres par org |

### 4.2 Dashboard Apprenant

**Etat actuel** : le dashboard montre TOUS les cours de l'apprenant.

**Ce qui change avec le multi-tenant** :

| Si l'apprenant accede via | Il voit |
|--------------------------|---------|
| `academie.mf.com` (portail general) | Tous ses cours |
| `vtc.academie.mf.com` | Uniquement ses cours VTC |
| `ia.academie.mf.com` | Uniquement ses cours IA |

Le filtrage se fait via `eox-tenant` qui injecte l'org du tenant dans le contexte.

### 4.3 Odoo (ERP)

**Ce qu'il faut** :

| Element Odoo | Multi-tenant |
|-------------|-------------|
| Produits | Chaque formation a un champ `academie` (tag ou categorie) |
| Pipeline CRM | Un pipeline par academie OU un pipeline global avec tag academie |
| Facturation | La facture mentionne l'academie (ex: "Formation VTC — Academie VTC") |
| Devis/Convention | Le template de convention est brande avec le logo de l'academie |
| Webhook → OpenEdX | Le payload inclut `academy_id` pour rattacher l'enrollment a l'academie |
| Reporting | CA par academie, par formation, par financeur |

**Implementation** :

```
Odoo : champ custom "academie" sur le produit
  │
  │ Commande confirmee
  ▼
Webhook → App Qualiopi
  │
  │ Payload : {academy_id: "vtc", course_id: "MF-VTC-CERT", user_email: "..."}
  ▼
App Qualiopi → OpenEdX
  │
  │ Creer enrollment + AcademyEnrollment
  ▼
L'apprenant voit le cours sur vtc.academie.mf.com
```

### 4.4 Qualiopi (App Hub API)

**Ce qui change** :

| Element | Impact multi-tenant |
|---------|-------------------|
| Scorecard 32 indicateurs | Global + par academie (filtrable) |
| PDFs generes | Le logo/couleurs de l'academie dans le header |
| Registres | Filtrables par academie |
| Enquetes satisfaction | Resultats par academie |
| Taux completion/abandon | Par academie |
| Bilan formation (ZIP) | Brande avec l'academie |
| Convention B2B | L'academie B2B de l'entreprise |

**L'app Qualiopi recoit `academy_id` dans chaque webhook et filtre en consequence.**

### 4.5 Signature electronique (Odoo Signature)

**Ce qui change** :

| Document | Multi-tenant |
|----------|-------------|
| Convention de formation | Logo + couleurs de l'academie dans le template |
| Contrat individuel | Idem |
| Devis | Idem |

**Implementation** : dans Odoo, un template de rapport par academie (ou un template generique avec variables dynamiques logo/couleurs).

### 4.6 Site internet (missionformations.com)

**Ce qui change** :

| Page | Multi-tenant |
|------|-------------|
| Page catalogue | Liste des academies avec lien vers chaque sous-domaine |
| Page academie | `/academie/vtc/` → description, formations, formateurs, tarifs |
| Page formation | Lien "S'inscrire" → redirige vers `vtc.academie.mf.com/courses/.../about` |
| SEO | Une page par academie = meilleur referencement |

### 4.7 Chat WeWill

**Ce qui change** :

| Element | Multi-tenant |
|---------|-------------|
| Widget chat | Meme widget sur tous les sous-domaines (meme inbox WeWill) |
| Identification | Le sous-domaine est envoye comme metadata → l'agent sait de quelle academie vient le message |
| Lead Odoo | Le lead cree est tague avec l'academie |

### 4.8 Certificats

**Deja fait.** Les 20 templates de certificats sont mappes par organisation (MF-VTC → design VTC, MF-IA → design IA, etc.). Le multi-tenant ne change rien — le bon certificat est deja selectionne automatiquement.

### 4.9 Forum (Discussions)

**Ce qui change** :

| Element | Multi-tenant |
|---------|-------------|
| Forum du cours | Deja filtre par cours — pas d'impact |
| Forum general (si prevu) | Un forum par academie |

### 4.10 Emails transactionnels

**Ce qui change** :

| Email | Multi-tenant |
|-------|-------------|
| Email de bienvenue | Logo + couleurs de l'academie |
| Convocation | Idem |
| Attestation | Idem (deja fait via les certificats) |
| Relances | Idem |

---

## 5. IMPLEMENTATION TECHNIQUE

### 5.1 DNS Wildcard

```bash
# Chez OVH (ou Cloudflare si configure) :
*.academie.staging.missionformations.com  A  89.167.50.194

# Un seul enregistrement DNS pour TOUS les sous-domaines
```

### 5.2 Caddy Wildcard SSL

```
*.academie.staging.missionformations.com {
    tls {
        dns ovh {
            # Config API OVH pour challenge DNS (wildcard SSL)
        }
    }
    reverse_proxy lms:8000
}
```

**Note** : le wildcard SSL necessite un challenge DNS (pas HTTP). Il faut configurer l'API OVH dans Caddy.

### 5.3 eox-tenant Configuration

```python
# Pour chaque academie, creer dans la DB :

# 1. Django Site
Site.objects.create(domain='vtc.academie.staging.missionformations.com', name='Academie VTC')

# 2. eox-tenant TenantConfig
TenantConfig.objects.create(
    external_key='vtc.academie.staging.missionformations.com',
    lms_configs={
        'SITE_NAME': 'vtc.academie.staging.missionformations.com',
        'PLATFORM_NAME': 'Academie VTC — Mission Formations',
        'platform_name': 'Academie VTC',
        'course_org_filter': ['MF-VTC'],  # Filtre les cours par org
        'ENABLE_COURSE_DISCOVERY': True,
        'logo_image_url': '/static/images/logo-vtc.png',
        'css_overrides_file': '/static/css/tenant-vtc.css',
    },
    studio_configs={},
    theming={
        'primary_color': '#0965D0',
        'secondary_color': '#01E8AE',
    }
)
```

### 5.4 Academy Manager — Creation automatisee

Quand un admin cree une academie dans l'Academy Manager :

```
Admin clique "Creer une academie"
  │
  │ Formulaire : nom, slug, org, logo, couleurs
  ▼
Backend :
  1. Creer le Django Site (domain = slug.academie.mf.com)
  2. Creer le TenantConfig eox-tenant
  3. Creer l'Academy dans mission_central_admin
  4. Creer le produit Odoo (categorie = academie)
  5. Si B2B : creer le contact entreprise dans Odoo
  │
  ▼
L'academie est accessible immediatement sur slug.academie.mf.com
```

### 5.5 Middleware sous-domaine

Le plugin `mission_central_admin` a deja un middleware prevu (Sprint 3 du cahier des charges) :

```python
class AcademySubdomainMiddleware:
    """Detecte le sous-domaine et injecte l'academie dans le request."""

    def __call__(self, request):
        host = request.get_host()
        # vtc.academie.staging.missionformations.com → slug = "vtc"
        subdomain = host.split('.')[0]

        try:
            academy = Academy.objects.get(subdomain=subdomain, is_active=True)
            request.academy = academy
        except Academy.DoesNotExist:
            request.academy = None

        return self.get_response(request)
```

---

## 6. TYPES D'ACADEMIES

### 6.1 Academies internes (thematiques)

Creees par Mission Formations pour organiser le catalogue :

| Academie | Slug | Org | Formations |
|----------|------|-----|------------|
| Academie VTC | vtc | MF-VTC | Certif VTC, Anglais VTC, Securite |
| Academie IA | ia | MF-IA | IA Entreprise, Workflows IA |
| Academie Management | management | MF-MGMT | Leadership |
| Academie Digital | digital | MF-DIGITAL | Excel, Outils numeriques |
| Academie RH | rh | MF-RH | Droit du travail, Gestion RH |
| Academie Finance | finance | MF-FINANCE | Comptabilite, Gestion financiere |
| Academie Vente | vente | MF-VENTE | Negociation commerciale |

### 6.2 Academies B2B (entreprises clientes)

Creees pour chaque entreprise cliente :

| Academie | Slug | Type | Formations | Places |
|----------|------|------|------------|--------|
| Entreprise ABC | abc | B2B | VTC (selectionne par le client) | 20 |
| Entreprise XYZ | xyz | B2B | IA + Management | 50 |

L'entreprise B2B voit :
- Son propre sous-domaine : `abc.academie.mf.com`
- Uniquement les formations qu'elle a achetees
- Le dashboard RH avec la progression de ses collaborateurs
- Son logo et ses couleurs (co-branding)

---

## 7. PARCOURS UTILISATEUR PAR ROLE

### 7.1 Apprenant individuel

```
1. Decouvre une formation sur le site missionformations.com
2. Clique "S'inscrire" → redirige vers vtc.academie.mf.com/courses/.../about
3. S'inscrit (ou se connecte) sur vtc.academie.mf.com
4. Paye (Odoo/Stripe)
5. Recoit la convocation par email (logo academie VTC)
6. Se connecte a vtc.academie.mf.com/dashboard → voit ses cours VTC
7. Suit la formation
8. Recoit le certificat (design VTC)
```

### 7.2 Apprenant B2B (entreprise)

```
1. Son RH inscrit les collaborateurs via le portail B2B
2. L'apprenant recoit un email de bienvenue (logo entreprise ABC)
3. Se connecte a abc.academie.mf.com/dashboard → voit ses cours
4. Ne voit QUE les formations achetees par son entreprise
5. Le RH suit la progression sur abc.academie.mf.com/dashboard-rh
```

### 7.3 Admin Mission Formations

```
1. Se connecte a academie.mf.com/admin/mission-dashboard/
2. Voit le dashboard global (toutes les academies)
3. Peut filtrer par academie (dropdown)
4. Peut creer une nouvelle academie via Academy Manager
5. Peut voir les stats par academie (CA, apprenants, completion)
```

### 7.4 Formateur

```
1. Se connecte a vtc.academie.mf.com (son academie)
2. Voit le dashboard formateur avec SES cours
3. Acces a Studio pour editer ses cours
4. Voit les apprenants de ses cours uniquement
```

### 7.5 Auditeur Qualiopi

```
1. Se connecte a l'app Qualiopi
2. Voit le scorecard global (32 indicateurs)
3. Peut filtrer par academie
4. Chaque preuve est rattachee a une academie
5. Le ZIP auditeur peut etre genere par academie
```

---

## 8. PLAN D'IMPLEMENTATION

### Phase 0 — Prerequis (Sprint 0)

| Tache | Effort | Dependance |
|-------|--------|------------|
| DNS wildcard *.academie.staging.mf.com | 15 min | Acces OVH DNS |
| Caddy wildcard SSL (challenge DNS OVH) | 2h | DNS wildcard |
| Installer et configurer eox-tenant | 3h | Caddy wildcard |

### Phase 1 — Premiere academie (Sprint 1)

| Tache | Effort | Dependance |
|-------|--------|------------|
| Creer l'academie VTC dans eox-tenant | 1h | Phase 0 |
| Tester vtc.academie.staging.mf.com | 30 min | Phase 1 |
| Verifier le filtrage des cours par org | 1h | Phase 1 |
| Verifier le branding (logo, couleurs) | 1h | Phase 1 |
| Adapter le dashboard apprenant pour le filtrage tenant | 3h | Phase 1 |

### Phase 2 — Toutes les academies internes (Sprint 2)

| Tache | Effort | Dependance |
|-------|--------|------------|
| Creer les 6 autres academies (IA, MGMT, Digital, RH, Finance, Vente) | 2h | Phase 1 |
| Automatiser la creation d'academie dans Academy Manager | 4h | Phase 1 |
| Adapter le dashboard admin pour le filtre par academie | 3h | Phase 1 |

### Phase 3 — B2B (Sprint 3-4)

| Tache | Effort | Dependance |
|-------|--------|------------|
| Workflow creation academie B2B depuis Odoo | 4h | Odoo configure |
| Dashboard RH entreprise (progression collaborateurs) | 6h | Phase 2 |
| Co-branding (logo + couleurs entreprise) | 3h | Phase 2 |
| Gestion des places (max_seats) | 2h | Phase 2 |

### Phase 4 — Integration complete (Sprint 4-5)

| Tache | Effort | Dependance |
|-------|--------|------------|
| Odoo : produits par academie | 2h | Odoo configure |
| Qualiopi : filtrage par academie | 4h | App Qualiopi |
| Emails brandes par academie | 3h | Phase 2 |
| Site internet : page par academie | 4h | Phase 2 |
| Signature electronique : template par academie | 2h | Odoo Signature |

**Effort total : ~45-50h reparties sur les sprints 1-5**

---

## 9. CE QUI NE CHANGE PAS

| Element | Pourquoi |
|---------|----------|
| Une seule instance OpenEdX | Performance, cout, maintenance |
| Une seule base MySQL/MongoDB | Partage des users, pas de duplication |
| Un seul Studio | Les formateurs editent dans le meme Studio |
| Un seul Odoo | Comptabilite unifiee |
| Une seule app Qualiopi | Scorecard global + filtrable |
| Un seul WeWill | Meme inbox support |
| Un seul S3 | Stockage centralise |

---

## 10. DECISIONS A PRENDRE

| Question | Options | Recommandation |
|----------|---------|---------------|
| **Sous-domaine ou path ?** | vtc.academie.mf.com vs academie.mf.com/vtc/ | **Sous-domaine** — plus propre, meilleur SEO, vrai isolation visuelle |
| **eox-tenant ou custom ?** | Plugin existant vs middleware custom | **eox-tenant** — deja installe, maintenu par Edunext, eprouve |
| **Quand commencer ?** | Maintenant / apres la prod | **Sprint 1** — c'est prevu dans le cahier des charges |
| **Academies internes d'abord ou B2B ?** | Internes / B2B | **Internes d'abord** — plus simple, valide le concept |
| **Un theme par academie ou CSS dynamique ?** | Theme Mako separe / CSS override | **CSS dynamique** (variables injectees par eox-tenant) — un seul theme a maintenir |
