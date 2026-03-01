import re
import unittest
from pathlib import Path


class StudioHelpLabelsTests(unittest.TestCase):
    """TDD guardrail: Studio help must expose business-friendly labels."""

    TEMPLATE = (
        Path(__file__).resolve().parents[2]
        / "themes/mission-theme/cms/templates/widgets/sock_links.html"
    )

    def _read_template(self) -> str:
        return self.TEMPLATE.read_text(encoding="utf-8")

    def test_studio_help_uses_expected_labels(self):
        content = self._read_template()
        self.assertIn("'text': _('Documentation')", content)
        self.assertIn("'text': _('Course demo')", content)

    def test_studio_help_removes_legacy_labels(self):
        content = self._read_template()
        self.assertNotIn("'text': _('edX Documentation')", content)
        self.assertNotIn("'text': _('Open edX Portal')", content)
        self.assertNotIn("'text': _('Enroll in edX101')", content)
        self.assertNotIn("'text': _('Enroll in StudioX')", content)

    def test_studio_help_exposes_two_primary_actions(self):
        content = self._read_template()
        labels = re.findall(r"'text': _\('([^']+)'\)", content)
        self.assertEqual(
            labels,
            ["Documentation", "Course demo"],
            "Les actions Studio Help doivent rester strictement: Documentation + Course demo.",
        )

    def test_theme_override_file_exists(self):
        self.assertTrue(
            self.TEMPLATE.exists(),
            "Le thème Mission doit fournir son override sock_links.html.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
