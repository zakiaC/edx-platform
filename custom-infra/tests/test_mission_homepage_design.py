import unittest
from pathlib import Path


class MissionHomepageDesignTests(unittest.TestCase):
    """Valide l'implementation du design cible de la homepage Mission."""

    TEMPLATE_PATH = Path("themes/mission-theme/lms/templates/index.html")
    CSS_PATH = Path("themes/mission-theme/lms/static/css/mf-homepage.css")

    def setUp(self):
        self.template = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.css = self.CSS_PATH.read_text(encoding="utf-8")

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

    def test_homepage_css_contains_preview_sections(self):
        """La feuille de style contient les sections du design fourni (nav/hero/footer)."""
        self.assertIn('.mf-nav{display:flex;align-items:center;justify-content:space-between;', self.css)
        self.assertIn('.mf-hero{position:relative;overflow:hidden;min-height:560px;display:flex;align-items:center;padding:80px 0 70px}', self.css)
        self.assertIn('.mf-footer{background:var(--mf-sidebar);padding:36px 0 22px;color:rgba(255,255,255,.5)}', self.css)


if __name__ == "__main__":
    unittest.main(verbosity=2)
