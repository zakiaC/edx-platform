import unittest
from pathlib import Path


class MissionHomepageDesignTests(unittest.TestCase):
    """Valide l'implementation homepage Mission via le pipeline theming Open edX."""

    TEMPLATE_PATH = Path("themes/mission-theme/lms/templates/index.html")
    LEGACY_CSS_PATH = Path("themes/mission-theme/lms/static/css/mf-homepage.css")
    SASS_EXTRAS_PATH = Path("themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss")

    def setUp(self):
        self.template = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.extras_sass = self.SASS_EXTRAS_PATH.read_text(encoding="utf-8")

    def test_homepage_contains_expected_navigation_and_footer(self):
        """Le design expose la nav Mission et le footer avec liens fonctionnels."""
        self.assertIn('class="mf-nav"', self.template)
        self.assertIn('Mission Formations', self.template)
        self.assertIn('href="#mf-catalog"', self.template)
        self.assertIn('href="/login"', self.template)
        self.assertIn('class="mf-footer"', self.template)
        self.assertIn('href="/contact"', self.template)
        self.assertIn('href="/handicap"', self.template)

    def test_homepage_uses_preview_catalog_cards_when_no_live_courses(self):
        """La grille catalogue affiche les 3 cartes de l'aperçu validé."""
        self.assertIn('formateurNabil · Serie1-VTC2', self.template)
        self.assertIn('Deuxième test formation', self.template)
        self.assertIn('Formation management & leadership', self.template)
        self.assertNotIn('Aucune formation disponible pour le moment.', self.template)

    def test_homepage_does_not_link_fragile_page_css(self):
        """Le template ne doit plus dependre d'un fichier CSS isolé hors pipeline theming."""
        self.assertNotIn("mf-homepage.css", self.template)

    def test_homepage_styles_are_in_theme_extras_sass(self):
        """Les styles de homepage sont centralises dans le partial theme extras (pipeline)."""
        self.assertTrue(self.SASS_EXTRAS_PATH.exists(), "themes/mission-theme/lms/static/sass/partials/lms/theme/_extras.scss manquant")
        self.assertIn("body.view-index", self.extras_sass)
        self.assertIn(".mf-nav", self.extras_sass)
        self.assertIn(".mf-hero", self.extras_sass)
        self.assertIn(".mf-catalog", self.extras_sass)
        self.assertIn(".mf-footer", self.extras_sass)

    def test_legacy_homepage_css_file_is_removed(self):
        """Evite les regressions vers un asset CSS page-level non packagé."""
        self.assertFalse(self.LEGACY_CSS_PATH.exists(), "themes/mission-theme/lms/static/css/mf-homepage.css doit etre supprime")


if __name__ == "__main__":
    unittest.main(verbosity=2)
