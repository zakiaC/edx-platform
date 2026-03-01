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
LMS_HEADER = os.path.join(
    REPO_ROOT, "themes", "mission-theme", "lms", "templates", "header", "header.html"
)
CMS_FOOTER = os.path.join(
    REPO_ROOT, "themes", "mission-theme", "cms", "templates", "widgets", "footer.html"
)
CMS_USER_DROPDOWN = os.path.join(
    REPO_ROOT, "themes", "mission-theme", "cms", "templates", "widgets", "user_dropdown.html"
)


class DashboardAccessLinksTests(unittest.TestCase):
    """Valide la présence des points d'entrée Dashboard sur LMS et CMS."""

    def _read(self, path):
        self.assertTrue(os.path.isfile(path), f"Fichier introuvable: {path}")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def test_lms_header_has_dashboard_link(self):
        """L'en-tête LMS expose un accès direct 'Mon dashboard'."""
        content = self._read(LMS_HEADER)
        self.assertIn("Mon dashboard", content)
        self.assertIn("/dashboard", content)

    def test_cms_footer_points_to_lms_dashboard(self):
        """Le footer CMS contient un lien vers le dashboard LMS."""
        content = self._read(CMS_FOOTER)
        self.assertIn("/dashboard", content)
        self.assertIn("Mon dashboard", content)

    def test_cms_user_dropdown_has_dashboard_shortcut(self):
        """Le menu utilisateur CMS expose un raccourci dashboard LMS."""
        content = self._read(CMS_USER_DROPDOWN)
        self.assertIn("/dashboard", content)
        self.assertRegex(content, r"Dashboard|Mon dashboard")


if __name__ == "__main__":
    unittest.main(verbosity=2)
