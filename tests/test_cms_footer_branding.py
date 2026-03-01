import os
import unittest


def find_repo_root():
    path = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(path, "cms")) and os.path.isdir(os.path.join(path, "themes")):
            return path
        path = os.path.dirname(path)
    return os.getcwd()


REPO_ROOT = find_repo_root()
CMS_CORE_FOOTER = os.path.join(REPO_ROOT, "cms", "templates", "widgets", "footer.html")


class CmsFooterBrandingTests(unittest.TestCase):
    """Valide le branding Studio: label Hub et suppression du logo Open edX."""

    def test_cms_footer_uses_hub_label(self):
        with open(CMS_CORE_FOOTER, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        self.assertIn('id="lms-link"', content)
        self.assertIn('${_("Hub")}', content)
        self.assertNotIn('${_("LMS")}', content)

    def test_cms_footer_has_no_openedx_logo_block(self):
        with open(CMS_CORE_FOOTER, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        self.assertNotIn("footer-about-openedx", content)
        self.assertNotIn("open-edx-logo-tag.png", content)
        self.assertNotIn("Powered by Open edX", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
