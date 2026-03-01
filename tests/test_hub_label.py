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
TARGET_FILES = [
    os.path.join(
        REPO_ROOT, "themes", "mission-theme", "lms", "templates", "admin", "base_site.html"
    ),
    os.path.join(
        REPO_ROOT, "themes", "mission-theme", "lms", "templates", "_mf_dashboard_admin.html"
    ),
    os.path.join(
        REPO_ROOT, "themes", "mission-theme", "lms", "templates", "admin_central_dashboard.html"
    ),
]


class HubLabelTests(unittest.TestCase):
    """Garantit l'usage du label 'Hub' à la place de 'LMS' dans l'UI Mission."""

    def test_hub_label_present_and_lms_label_absent(self):
        for path in TARGET_FILES:
            with self.subTest(path=path):
                self.assertTrue(os.path.isfile(path), f"Fichier introuvable: {path}")
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                self.assertIn("Hub", content, f"Le label 'Hub' est absent de {path}")
                self.assertNotIn(">LMS<", content, f"Le label '>LMS<' doit être remplacé dans {path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
