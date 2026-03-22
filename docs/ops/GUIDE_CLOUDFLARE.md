# Guide Cloudflare — Mission Formations

> A faire avant la mise en prod
> Duree : 15-20 minutes
> Cout : 0€ (plan Free)
> Pre-requis : acces au manager OVH + email pour creer le compte Cloudflare

---

## Pourquoi Cloudflare

| Ce que ca fait | Detail |
|----------------|--------|
| CDN | Les CSS, JS, images sont caches dans 300+ datacenters → site plus rapide |
| Protection DDoS | Bloque les attaques automatiquement |
| WAF | Filtre les requetes malveillantes (injections SQL, XSS, bots) |
| SSL | Double couche SSL (Cloudflare + Caddy) |
| IP cachee | L'IP du VPS n'est plus visible publiquement |
| Analytics | Statistiques de trafic gratuites |

---

## Etape 1 — Creer le compte Cloudflare

1. Aller sur https://dash.cloudflare.com/sign-up
2. Email : utiliser l'email pro (ex: admin@missionformations.com)
3. Mot de passe : fort (12+ caracteres)
4. Valider l'email de confirmation

---

## Etape 2 — Ajouter le domaine

1. Dashboard Cloudflare → "Add a site"
2. Entrer : `missionformations.com`
3. Selectionner le plan **Free**
4. Cliquer "Continue"
5. Cloudflare scanne automatiquement les DNS existants

---

## Etape 3 — Verifier les enregistrements DNS

Cloudflare affiche les DNS detectes. Verifier que tous ces enregistrements sont presents :

### DNS Staging

| Type | Nom | Valeur | Proxy |
|------|-----|--------|-------|
| A | academie.staging | 89.167.50.194 | ☁️ Proxied (orange) |
| A | studio.staging | 89.167.50.194 | ☁️ Proxied |
| A | apps.academie.staging | 89.167.50.194 | ☁️ Proxied |
| A | chat.staging | 89.167.50.194 | ☁️ Proxied |
| A | meilisearch.academie.staging | 89.167.50.194 | ☁️ Proxied |

### DNS Production (a ajouter quand la prod sera prete)

| Type | Nom | Valeur | Proxy |
|------|-----|--------|-------|
| A | academie | [IP PROD] | ☁️ Proxied |
| A | studio | [IP PROD] | ☁️ Proxied |
| A | apps.academie | [IP PROD] | ☁️ Proxied |
| A | chat | [IP PROD] | ☁️ Proxied |

### DNS Site internet (si heberge separement)

| Type | Nom | Valeur | Proxy |
|------|-----|--------|-------|
| A | @ | [IP site] | ☁️ Proxied |
| A | www | [IP site] | ☁️ Proxied |

### DNS Email (ne PAS mettre en Proxied)

| Type | Nom | Valeur | Proxy |
|------|-----|--------|-------|
| MX | @ | (serveur mail) | ☁️ DNS only (gris) |
| TXT | @ | (SPF, DKIM) | ☁️ DNS only (gris) |

**IMPORTANT** : les enregistrements MX (email) doivent etre en "DNS only" (nuage gris), PAS en "Proxied". Sinon les emails ne fonctionnent plus.

---

## Etape 4 — Changer les nameservers chez OVH

Cloudflare donne 2 nameservers (ex: `ada.ns.cloudflare.com` et `bob.ns.cloudflare.com`).

1. Aller sur https://www.ovh.com/manager/
2. Menu → Noms de domaine → missionformations.com
3. Onglet "Serveurs DNS"
4. Cliquer "Modifier les serveurs DNS"
5. Remplacer les nameservers OVH par ceux de Cloudflare :
   - Serveur DNS 1 : `ada.ns.cloudflare.com` (exemple, Cloudflare donne les vrais)
   - Serveur DNS 2 : `bob.ns.cloudflare.com`
6. Sauvegarder
7. Retourner sur Cloudflare → cliquer "Done, check nameservers"

**Propagation** : quelques minutes a 24h. Cloudflare envoie un email quand c'est actif.

---

## Etape 5 — Configurer SSL

1. Dashboard Cloudflare → SSL/TLS
2. Mode : **Full (strict)**
   - Full (strict) = Cloudflare chiffre vers le serveur ET verifie le certificat
   - Le serveur (Caddy) a deja un certificat valide → Full (strict) est correct
3. Onglet "Edge Certificates" → activer "Always Use HTTPS"
4. Activer "Automatic HTTPS Rewrites"

---

## Etape 6 — Configurer le cache

1. Dashboard Cloudflare → Caching → Configuration
2. "Caching Level" : **Standard**
3. "Browser Cache TTL" : **4 hours** (les CSS/JS changent rarement)
4. Onglet "Cache Rules" → creer une regle :
   - Si URL contient `/static/` → Cache Everything, Edge TTL 1 jour
   - Cela cache tous les assets statiques (CSS, JS, images, polices)

---

## Etape 7 — Configurer la securite

1. Dashboard Cloudflare → Security → Settings
2. "Security Level" : **Medium**
3. "Bot Fight Mode" : **On**
4. "Browser Integrity Check" : **On**

### Page Rules (optionnel)

| Regle | URL | Action |
|-------|-----|--------|
| Proteger l'admin | `*missionformations.com/admin/*` | Security Level: High |
| Proteger Studio | `studio.*missionformations.com/*` | Security Level: High |
| Cache les assets | `*missionformations.com/static/*` | Cache Level: Cache Everything |

---

## Etape 8 — Verifier que tout fonctionne

Apres la propagation DNS :

| Test | Comment |
|------|---------|
| Site accessible | Ouvrir https://academie.staging.missionformations.com/ |
| SSL valide | Cliquer sur le cadenas → certificat emis par Cloudflare |
| Studio accessible | Ouvrir https://studio.staging.missionformations.com/ |
| Chat accessible | Widget chat en bas a droite |
| Emails fonctionnent | Envoyer un email de test |

### Verifier que Cloudflare est actif

```bash
curl -I https://academie.staging.missionformations.com/ 2>/dev/null | grep -i 'cf-ray\|server'
```

Si Cloudflare est actif, tu verras :
```
server: cloudflare
cf-ray: xxxx-CDG
```

---

## En cas de probleme

### Le site ne charge plus apres le changement de nameservers

1. Attendre 24h (propagation DNS)
2. Verifier les nameservers : `dig missionformations.com NS`
3. Si ca ne marche toujours pas → repasser sur les nameservers OVH

### Les emails ne fonctionnent plus

1. Verifier que les enregistrements MX sont en "DNS only" (gris) et PAS "Proxied" (orange)
2. Dans Cloudflare → DNS → trouver les MX → cliquer le nuage pour le passer en gris

### Studio donne une erreur SSL

1. Verifier que le mode SSL est "Full (strict)" et pas "Flexible"
2. "Flexible" cause des boucles de redirection

### Le chat ne fonctionne plus

1. Verifier que `chat.staging.missionformations.com` est dans les DNS Cloudflare
2. Verifier que le Caddy route toujours vers chatwoot-rails

---

## Checklist rapide

- [ ] Compte Cloudflare cree
- [ ] Domaine ajoute (plan Free)
- [ ] DNS verifies (staging + email)
- [ ] Nameservers changes chez OVH
- [ ] Propagation terminee (email Cloudflare recu)
- [ ] SSL : Full (strict)
- [ ] Cache : Standard + regle /static/
- [ ] Securite : Medium + Bot Fight
- [ ] Test : site, studio, chat, emails OK
