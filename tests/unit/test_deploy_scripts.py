# -*- coding: utf-8 -*-
"""
Tests unitaires — Scripts de deploiement et infra.

Verifie:
- deploy.sh est executable et syntaxiquement valide
- Scripts custom-infra presents et valides
- .gitignore couvre les fichiers sensibles
"""
import os
import re
import subprocess

import pytest

from tests.conftest import ROOT_DIR, CUSTOM_INFRA_DIR, IN_DOCKER

# Ces tests ne tournent qu'en local (deploy.sh, .gitignore, etc. n'existent
# pas dans le container Docker)
pytestmark = pytest.mark.skipif(IN_DOCKER, reason="Tests locaux uniquement — fichiers absents dans le container Docker")

# ── 1. DEPLOY.SH ───────────────────────────────────────────────────────────

class TestDeployScript:
    """Le script de deploiement principal."""

    @pytest.mark.unit
    def test_deploy_sh_exists(self):
        deploy = ROOT_DIR / "deploy.sh"
        assert deploy.exists(), "deploy.sh manquant a la racine"

    @pytest.mark.unit
    def test_deploy_sh_executable(self):
        deploy = ROOT_DIR / "deploy.sh"
        if not deploy.exists():
            pytest.skip("deploy.sh absent")
        assert os.access(deploy, os.X_OK), "deploy.sh n'est pas executable (chmod +x)"

    @pytest.mark.unit
    def test_deploy_sh_valid_bash(self):
        deploy = ROOT_DIR / "deploy.sh"
        if not deploy.exists():
            pytest.skip("deploy.sh absent")
        result = subprocess.run(
            ["bash", "-n", str(deploy)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, (
            f"deploy.sh: erreur de syntaxe bash: {result.stderr}"
        )

    @pytest.mark.unit
    def test_deploy_sh_has_shebang(self):
        deploy = ROOT_DIR / "deploy.sh"
        if not deploy.exists():
            pytest.skip("deploy.sh absent")
        first_line = deploy.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("#!"), "deploy.sh: shebang manquant"


# ── 2. SCRIPTS CUSTOM-INFRA ────────────────────────────────────────────────

class TestCustomInfraScripts:
    """Scripts dans custom-infra/."""

    EXPECTED_SCRIPTS = [
        "scripts/deploy-theme.sh",
        "scripts/smoke-test.sh",
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("script_path", EXPECTED_SCRIPTS)
    def test_script_exists(self, script_path):
        filepath = CUSTOM_INFRA_DIR / script_path
        if not filepath.exists():
            pytest.skip(f"{script_path} absent")
        assert filepath.stat().st_size > 0, f"{script_path} est vide"

    @pytest.mark.unit
    @pytest.mark.parametrize("script_path", EXPECTED_SCRIPTS)
    def test_script_valid_bash(self, script_path):
        filepath = CUSTOM_INFRA_DIR / script_path
        if not filepath.exists():
            pytest.skip(f"{script_path} absent")
        result = subprocess.run(
            ["bash", "-n", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, (
            f"{script_path}: erreur bash: {result.stderr}"
        )


# ── 3. GITIGNORE ───────────────────────────────────────────────────────────

class TestGitignore:
    """Le .gitignore protege les fichiers sensibles."""

    MUST_IGNORE = [
        "*.secrets.env",
        ".codex-renders/",
        ".codex-venv/",
        ".DS_Store",
        "docker.sock",
        "*.xlsx",
    ]

    @pytest.mark.unit
    def test_gitignore_exists(self):
        gitignore = ROOT_DIR / ".gitignore"
        assert gitignore.exists(), ".gitignore manquant"

    @pytest.mark.unit
    @pytest.mark.parametrize("pattern", MUST_IGNORE)
    def test_pattern_in_gitignore(self, pattern):
        gitignore = ROOT_DIR / ".gitignore"
        if not gitignore.exists():
            pytest.skip(".gitignore absent")
        content = gitignore.read_text(encoding="utf-8")
        assert pattern in content, (
            f".gitignore: pattern '{pattern}' manquant — risque de commit accidentel"
        )

    @pytest.mark.unit
    def test_no_secrets_env_tracked(self):
        """Aucun fichier .secrets.env ne doit etre tracke par git."""
        result = subprocess.run(
            ["git", "ls-files", "--", "*.secrets.env", ".secrets.env"],
            capture_output=True, text=True, cwd=str(ROOT_DIR), timeout=10,
        )
        tracked = result.stdout.strip()
        assert not tracked, (
            f"Fichier(s) secrets tracke(s) par git: {tracked}"
        )
