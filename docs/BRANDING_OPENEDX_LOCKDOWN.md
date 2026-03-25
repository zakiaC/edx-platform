# Verrouillage branding — Suppression du logo OpenEdX

> Version 1.0 — 25 mars 2026
> Document interne equipe technique

---

## Objectif

Supprimer toute trace visible du logo et de la marque OpenEdX sur l'ensemble de la plateforme (LMS, CMS/Studio, MFEs). L'utilisateur final ne doit jamais savoir que la plateforme est construite sur OpenEdX.

---

## Architecture du verrouillage (triple verrou)

### Verrou 1 — Settings (plugin Tutor)

**Fichier** : `tutor_plugins/mission_theme_lock.py`

Settings injectes dans le LMS :
```python
LOGO_POWERED_BY_OPEN_EDX_URL = False
LOGO_POWERED_BY_OPEN_EDX_URL_DARK = False
ENABLE_FOOTER_MOBILE_APP_LINKS = False
FOOTER_OPENEDX_URL = None
FOOTER_OPENEDX_LOGO_IMAGE = None

MFE_CONFIG = {
    'LOGO_POWERED_BY_OPEN_EDX_URL': False,
    'SHOW_POWERED_BY_OPENEDX': False,
    'FOOTER_POWERED_BY_OPENEDX': False,
}
```

Settings injectes dans le CMS :
```python
LOGO_POWERED_BY_OPEN_EDX_URL = False
LOGO_POWERED_BY_OPEN_EDX_URL_DARK = False
FOOTER_OPENEDX_URL = None
FOOTER_OPENEDX_LOGO_IMAGE = None
```

**Pourquoi** : les MFEs (Learning, Account, etc.) lisent MFE_CONFIG pour afficher ou non le logo. Les templates Mako utilisent les settings FOOTER_OPENEDX_*.

### Verrou 2 — Code Python (branding API)

**Fichier** : `lms/djangoapps/branding/views.py`

Deux modifications :

1. **Fonction `_render_footer_html()`** (ligne ~142) :
```python
# Mission Formations: toujours masquer le logo OpenEdX
show_openedx_logo = False
context = {
    'hide_openedx_link': True,
    ...
}
```

2. **API endpoint `/api/branding/v1/footer`** (ligne ~266) :
```python
# Mission Formations: toujours masquer le logo OpenEdX
show_openedx_logo = False
```

**Pourquoi** : meme si un parametre `?show-openedx-logo=1` est passe dans l'URL ou si les settings sont reinitialises par une mise a jour, le code force la valeur a False.

### Verrou 3 — Fichiers statiques (images)

**Fichiers** :
- `lms/static/images/openedx-logo-tag.png`
- `lms/static/images/openedx-logo-tag-dark.png`
- `lms/static/images/openedx-logo-tag-light.png`

**Action** : remplaces par des PNG transparents 1x1 pixel.

**Pourquoi** : meme si un template ou MFE charge ces images, elles sont invisibles (transparentes).

---

## Templates concernes

### Footer LMS natif (`lms/templates/footer.html`)

Le template natif contient :
```mako
% if not hide_openedx_link:
    <div class="footer-about-openedx">
        <a href="${footer['openedx_link']['url']}">
            <img src="${footer['openedx_link']['image']}" ... />
        </a>
    </div>
% endif
```

Ce bloc est masque par `hide_openedx_link = True` (verrou 2).

### Footer LMS theme Mission (`themes/mission-theme/lms/templates/footer.html`)

Ce template surcharge le natif et ne contient **aucune reference** a OpenEdX. Il est 100% brande Mission Formations.

### Footer CMS/Studio (`themes/mission-theme/cms/templates/widgets/footer.html`)

Ce template surcharge le natif et ne contient **aucune reference** a OpenEdX. Footer brande "Academie Mission Formations".

---

## Cas de risque et protection

| Scenario | Protection |
|----------|-----------|
| Mise a jour OpenEdX (tutor upgrade) | Verrou 1 (settings plugin) + Verrou 2 (code Python) empechent la reapparition |
| Plugin Tutor desactive | Verrou 2 (code) + Verrou 3 (images transparentes) couvrent |
| Settings ecrases par `tutor config save` | Les settings sont dans le plugin, ils sont reinjectes automatiquement |
| Nouveau MFE installe | MFE_CONFIG dans le plugin masque le logo dans tous les MFEs |
| Template theme supprime ou ecrase | Verrou 2 dans le code Python force `hide_openedx_link = True` |
| Parametre `?show-openedx-logo=1` dans l'URL | Verrou 2 : le parametre est ignore, force a False |
| Image chargee directement par URL | Verrou 3 : l'image est un pixel transparent |

---

## Verification apres deploy

Apres chaque deploy ou mise a jour, verifier les pages suivantes :

1. **Homepage** : https://academie.staging.missionformations.com/
2. **Page de cours** : https://academie.staging.missionformations.com/courses/course-v1:MissionFormations+MF-VTC-2025+2025/course/
3. **Dashboard** : https://academie.staging.missionformations.com/dashboard
4. **Studio** : https://apps.academie.staging.missionformations.com/authoring/home
5. **Login** : https://academie.staging.missionformations.com/login
6. **API footer** : https://academie.staging.missionformations.com/api/branding/v1/footer

Sur chaque page, scroller en bas et verifier qu'**aucun logo ou mention OpenEdX** n'est visible.

### Test automatise (a ajouter aux smoke tests)

```python
def test_no_openedx_branding():
    """Verifier qu'aucun logo OpenEdX n'est visible sur le site."""
    pages = ['/', '/login', '/dashboard', '/courses/']
    for page in pages:
        response = requests.get(f'{BASE_URL}{page}')
        assert 'openedx-logo' not in response.text.lower()
        assert 'powered by open edx' not in response.text.lower()
        assert 'openedx.org' not in response.text.lower()
```

---

## Fichiers modifies (resume)

| Fichier | Modification |
|---------|-------------|
| `tutor_plugins/mission_theme_lock.py` | Settings LOGO_POWERED_BY + MFE_CONFIG + FOOTER_OPENEDX |
| `lms/djangoapps/branding/views.py` | Force show_openedx_logo=False, hide_openedx_link=True |
| `lms/static/images/openedx-logo-tag.png` | Remplace par PNG transparent 1x1 |
| `lms/static/images/openedx-logo-tag-dark.png` | Remplace par PNG transparent 1x1 |
| `lms/static/images/openedx-logo-tag-light.png` | Remplace par PNG transparent 1x1 |
| `themes/mission-theme/lms/templates/footer.html` | Aucune ref OpenEdX (deja clean) |
| `themes/mission-theme/cms/templates/widgets/footer.html` | Aucune ref OpenEdX (deja clean) |

---

## Commits

| Hash | Message |
|------|---------|
| `0778784b8b` | fix(branding): supprimer le logo OpenEdX de toutes les pages LMS, CMS et MFEs |
| `d96a6d8302` | fix(branding): verrouiller suppression logo OpenEdX — aucune trace visible |

---

*Document genere le 25 mars 2026 — Mission Formations — Equipe technique*
