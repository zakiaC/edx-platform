import unittest
from pathlib import Path
import re


class ThemeDeployRunbookTests(unittest.TestCase):
    """Valide les artefacts OPS de deploiement theme et smoke test Open edX."""

    DEPLOY_SCRIPT = Path("custom-infra/scripts/deploy-theme.sh")
    SMOKE_SCRIPT = Path("custom-infra/scripts/smoke-test.sh")
    RUNBOOK_DOC = Path("custom-infra/docs/openedx-theme-css-rca-runbook.md")

    def test_rt_ops_001_required_files_exist(self):
        """RT-OPS-001: les 3 livrables OPS (deploy, smoke, runbook) existent dans le repo."""
        self.assertTrue(self.DEPLOY_SCRIPT.exists(), f"{self.DEPLOY_SCRIPT} manquant")
        self.assertTrue(self.SMOKE_SCRIPT.exists(), f"{self.SMOKE_SCRIPT} manquant")
        self.assertTrue(self.RUNBOOK_DOC.exists(), f"{self.RUNBOOK_DOC} manquant")

    def test_rt_ops_002_deploy_script_has_build_collect_restart_flow(self):
        """RT-OPS-002: le script de deploy doit enchaîner build + collect + restart."""
        content = self.DEPLOY_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("openedx-assets build", content)
        self.assertIn("openedx-assets collect", content)
        self.assertIn("restart lms cms", content)
        self.assertRegex(content, r"grep\s+-c\s+['\"]mf-nav['\"]")

    def test_rt_ops_003_smoke_script_checks_html_and_css(self):
        """RT-OPS-003: le smoke test couvre endpoints, markers HTML et classes CSS du bundle."""
        content = self.SMOKE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("formateurNabil", content)
        self.assertIn("Serie1-VTC2", content)
        self.assertIn("Deuxième test formation", content)
        self.assertIn("mf-homepage\\.css", content)
        self.assertIn("mf-nav", content)
        self.assertIn("mf-hero", content)
        self.assertIn("mf-section", content)
        self.assertIn("mf-footer", content)

    def test_rt_ops_004_runbook_contains_rca_and_validation_commands(self):
        """RT-OPS-004: le runbook documente RCA, verification technique et correctif permanent."""
        content = self.RUNBOOK_DOC.read_text(encoding="utf-8")
        self.assertIn("Root Cause Analysis", content)
        self.assertIn("Cause racine", content)
        self.assertIn("openedx-assets build", content)
        self.assertIn("openedx-assets collect", content)
        self.assertRegex(content, r"grep\s+-[rR].*_extras")
        self.assertIn("lms-main-v2.scss", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
