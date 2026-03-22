# Process post-tutor — Réappliquer les customisations

> CE PROCESS EST OBLIGATOIRE apres chaque :
> - `tutor config save`
> - `tutor local launch`
> - `tutor local start -d` (si containers redemarres)
> - `pip install tutor-xxx` (nouveau plugin)
> - Tout redemarrage des containers Docker

---

## POURQUOI CE PROCESS EXISTE

`tutor config save` et `tutor local launch` regenerent les settings
et redemarrent les containers. Cela ecrase :

1. Les settings LMS custom qui ne sont PAS dans un plugin Tutor
2. Les settings Chatwoot en base de donnees (branding WeWill)
3. Le logo copie dans le container Chatwoot (docker cp = non persistant)

---

## CHECKLIST POST-TUTOR (a executer dans l'ordre)

### Etape 1 — Verifier les plugins

```bash
ssh staging-openedx "tutor plugins list"
```

Plugins obligatoires (TOUS doivent etre ✅ enabled) :

| Plugin | Attendu |
|--------|---------|
| mfe | ✅ enabled |
| forum | ✅ enabled |
| mission_central_admin | ✅ enabled |
| mission_theme_lock | ✅ enabled |
| mission_certificates_policy | ✅ enabled |
| mission_csp_report_only | ✅ enabled |
| mission_theme_assets | ✅ enabled |
| mission_wewill | ✅ enabled |
| mission_braze_enrollment | ✅ enabled |

Si un plugin manque → `pip install tutor-xxx` ou copier le fichier .py dans `~/.local/share/tutor-plugins/`

### Etape 2 — Verifier les settings LMS

```bash
ssh staging-openedx "docker exec tutor_local-lms-1 python -c \"
from django.conf import settings
checks = {
    'LEARNING_MICROFRONTEND_URL': settings.LEARNING_MICROFRONTEND_URL,
    'ENABLE_MFE_CONFIG_API': settings.ENABLE_MFE_CONFIG_API,
    'DEFAULT_SITE_THEME': settings.DEFAULT_SITE_THEME,
    'CERTIFICATES_HTML_VIEW': settings.FEATURES.get('CERTIFICATES_HTML_VIEW'),
    'ENABLE_DISCUSSION_SERVICE': settings.FEATURES.get('ENABLE_DISCUSSION_SERVICE'),
    'MFE_CONFIG present': bool(settings.MFE_CONFIG),
}
for k, v in checks.items():
    status = 'OK' if v else 'ERREUR'
    print(f'{status}: {k} = {v}')
\" 2>/dev/null"
```

Si un setting est ERREUR → le plugin correspondant est manquant ou desactive.

### Etape 3 — Verifier les containers

```bash
ssh staging-openedx "docker ps --format '{{.Names}} {{.Status}}' | sort"
```

Containers obligatoires :

| Container | Sans lui |
|-----------|---------|
| tutor_local-lms-1 | Site inaccessible |
| tutor_local-cms-1 | Studio inaccessible |
| tutor_local-mfe-1 | Cours inaccessibles (MFE Learning) |
| tutor_local-mysql-1 | Tout casse |
| tutor_local-mongodb-1 | Contenu cours inaccessible |
| tutor_local-redis-1 | Cache et sessions morts |
| tutor_local-caddy-1 | SSL et routing morts |
| chatwoot-rails | Chat indisponible |

### Etape 4 — Reappliquer le branding WeWill

```bash
ssh staging-openedx "/root/chatwoot/apply-branding.sh"
```

Verifie ensuite :
```bash
ssh staging-openedx "docker exec chatwoot-rails bundle exec rails runner \"
puts 'INSTALLATION_NAME: ' + InstallationConfig.find_by(name: 'INSTALLATION_NAME')&.value.to_s
puts 'BRAND_NAME: ' + InstallationConfig.find_by(name: 'BRAND_NAME')&.value.to_s
\" 2>/dev/null"
```

Attendu : INSTALLATION_NAME: WeWill, BRAND_NAME: WeWill

### Etape 5 — Redeployer le theme (si tutor config save a ete fait)

```bash
./deploy.sh staging
```

Le deploy.sh fait :
- Sync code → container
- Compile Sass
- Collectstatic
- Clear cache Mako
- Restart LMS
- Smoke tests

### Etape 6 — Executer les smoke tests

Ouvrir `docs/ops/TEST_STAGING_CHECKLIST.md` et verifier les 33 tests.

Au minimum, verifier :
1. Homepage → 200
2. Login → 200
3. Cours VTC → accessible
4. Chat → "Powered by WeWill"
5. Studio → accessible

---

## AUTOMATISATION (a implementer)

Pour eviter d'oublier ce process, creer un script `post-tutor.sh` :

```bash
#!/bin/bash
# post-tutor.sh — A executer apres chaque tutor config save / launch
set -e
echo "=== POST-TUTOR — Reapplication des customisations ==="

echo "--- 1/4 Verification plugins ---"
tutor plugins list

echo "--- 2/4 Verification settings ---"
docker exec tutor_local-lms-1 python -c "
from django.conf import settings
assert settings.LEARNING_MICROFRONTEND_URL, 'LEARNING_MICROFRONTEND_URL manquant'
assert settings.ENABLE_MFE_CONFIG_API, 'ENABLE_MFE_CONFIG_API manquant'
assert settings.DEFAULT_SITE_THEME == 'mission-theme', 'Theme non mission-theme'
print('Settings OK')
" 2>/dev/null

echo "--- 3/4 Branding WeWill ---"
/root/chatwoot/apply-branding.sh

echo "--- 4/4 Smoke test rapide ---"
HTTP=$(curl -s -o /dev/null -w '%{http_code}' https://academie.staging.missionformations.com/)
[ "$HTTP" = "200" ] && echo "Homepage: OK" || echo "ERREUR Homepage: $HTTP"

echo "=== POST-TUTOR TERMINE ==="
```

---

## RESUME

| Commande Tutor | Ce qu'elle ecrase | Post-action obligatoire |
|----------------|-------------------|------------------------|
| `tutor config save` | Settings LMS/CMS | Verifier settings (etape 2) |
| `tutor local launch` | Settings + containers + init | TOUT le process (etapes 1-6) |
| `tutor local start -d` | Redemarre containers | Branding WeWill (etape 4) |
| `tutor local restart lms` | Redemarre LMS uniquement | Verifier settings (etape 2) |
| `pip install tutor-xxx` | Peut ecraser des paquets | Verifier plugins (etape 1) |
