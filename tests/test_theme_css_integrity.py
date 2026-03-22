"""
Test de non-régression : le CSS Mission doit contenir les classes .mf-*

Diagnostic (2026-03-22) :
  Le CSS compilé dans le thème (lms/static/css/lms-main-v1.css) contenait
  bien les règles .mf-hero, .mf-card, etc. Mais collectstatic ne recopiait
  pas ce fichier dans /openedx/staticfiles/ car le fichier existant avait
  le même hash Django. Résultat : le navigateur chargeait un CSS vide de
  tout style Mission.

  Cause racine : collectstatic --noinput sans --clear ne remplace pas un
  fichier déjà présent si le hash Django n'a pas changé, même si le contenu
  du source a changé.

  Correctifs appliqués :
  1. Inline CSS dans index.html (filet de sécurité — le design marche même
     sans compilation Sass)
  2. Copie forcée dans deploy.sh après collectstatic
  3. Ce test vérifie que le CSS source ET le CSS compilé contiennent
     les classes Mission critiques
"""

import os
import unittest


def find_repo_root():
    path = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(path, "themes")):
            return path
        path = os.path.dirname(path)
    return os.getcwd()


REPO_ROOT = find_repo_root()
THEME_DIR = os.path.join(REPO_ROOT, "themes", "mission-theme", "lms")

SASS_SOURCE = os.path.join(THEME_DIR, "static", "sass", "partials", "lms", "theme", "_extras.scss")
COMPILED_CSS = os.path.join(THEME_DIR, "static", "css", "lms-main-v1.css")
INDEX_TEMPLATE = os.path.join(THEME_DIR, "templates", "index.html")

# Classes CSS critiques qui doivent être présentes pour que le thème s'affiche
CRITICAL_CSS_CLASSES = [
    ".mf-hero",
    ".mf-hero__bg",
    ".mf-hero__title",
    ".mf-btn--grad",
    ".mf-features",
    ".mf-feat__icon",
    ".mf-card",
    ".mf-card__body",
    ".mf-catalog",
    ".mf-footer",
    ".mf-cta__box",
]


class ThemeCSSSourceTests(unittest.TestCase):
    """Vérifie que le source Sass contient les classes Mission critiques."""

    def test_sass_source_exists(self):
        self.assertTrue(os.path.isfile(SASS_SOURCE), f"Sass source introuvable: {SASS_SOURCE}")

    def test_sass_source_contains_critical_classes(self):
        with open(SASS_SOURCE, "r", encoding="utf-8") as f:
            content = f.read()
        for css_class in CRITICAL_CSS_CLASSES:
            with self.subTest(css_class=css_class):
                self.assertIn(css_class, content, f"Classe {css_class} absente du Sass source")


class ThemeCSSCompiledTests(unittest.TestCase):
    """Vérifie que le CSS compilé contient les classes Mission critiques."""

    def test_compiled_css_exists(self):
        self.assertTrue(os.path.isfile(COMPILED_CSS), f"CSS compilé introuvable: {COMPILED_CSS}")

    def test_compiled_css_contains_critical_classes(self):
        with open(COMPILED_CSS, "r", encoding="utf-8") as f:
            content = f.read()
        for css_class in CRITICAL_CSS_CLASSES:
            with self.subTest(css_class=css_class):
                self.assertIn(css_class, content, f"Classe {css_class} absente du CSS compilé — relancer la compilation Sass")

    def test_compiled_css_minimum_size(self):
        """Le CSS compilé doit faire au moins 900 Ko (le thème complet pèse ~930 Ko)."""
        size = os.path.getsize(COMPILED_CSS)
        self.assertGreater(size, 900_000, f"CSS compilé trop petit ({size} octets) — compilation Sass probablement incomplète")


class ThemeInlineCSSTests(unittest.TestCase):
    """Vérifie que le template index.html contient le CSS inline (filet de sécurité)."""

    def test_index_template_exists(self):
        self.assertTrue(os.path.isfile(INDEX_TEMPLATE), f"Template introuvable: {INDEX_TEMPLATE}")

    def test_index_contains_inline_mf_hero(self):
        with open(INDEX_TEMPLATE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".mf-hero", content, "Le CSS inline .mf-hero est absent du template index.html — risque de régression visuelle")

    def test_index_contains_inline_mf_card(self):
        with open(INDEX_TEMPLATE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".mf-card", content, "Le CSS inline .mf-card est absent du template index.html — risque de régression visuelle")


if __name__ == "__main__":
    unittest.main(verbosity=2)
