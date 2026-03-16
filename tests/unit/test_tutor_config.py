# -*- coding: utf-8 -*-
"""
Tests unitaires — Fichiers de configuration Tutor (tutor-patches/).

Verifie:
- Syntaxe Python valide (pas de SyntaxError)
- Pas de secrets en dur (valeurs sensibles)
- Pas de settings dupliques
- Coherence entre lms et cms
"""
import ast
import re

import pytest

from tests.conftest import TUTOR_PATCHES_DIR, IN_DOCKER

# tutor-patches/ n'existe que sur le disque local, pas dans le container Docker
pytestmark = pytest.mark.skipif(
    IN_DOCKER and not TUTOR_PATCHES_DIR.exists(),
    reason="tutor-patches/ absent dans le container Docker — tests locaux uniquement"
)

# ── Fichiers a tester ───────────────────────────────────────────────────────

CONFIG_FILES = [
    "lms-production.py",
    "cms-production.py",
]

ASSET_FILES = [
    "lms-assets.py",
    "cms-assets.py",
]

ALL_PY_FILES = CONFIG_FILES + ASSET_FILES


# ── 1. SYNTAXE PYTHON ──────────────────────────────────────────────────────

class TestPythonSyntax:
    """Chaque fichier .py dans tutor-patches/ doit etre parseable par Python."""

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", ALL_PY_FILES)
    def test_syntax_valid(self, filename):
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        source = filepath.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=filename)
        except SyntaxError as exc:
            pytest.fail(
                f"SyntaxError dans {filename} ligne {exc.lineno}: {exc.msg}"
            )

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", ALL_PY_FILES)
    def test_no_concatenated_statements(self, filename):
        """Detecte deux instructions Python collees sur la meme ligne
        (ex: append(...)PIPELINE = ...). Bug introduit par Codex."""
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        lines = filepath.read_text(encoding="utf-8").splitlines()
        pattern = re.compile(r'\)[A-Z_][\w]*\s*[\[=]')
        for i, line in enumerate(lines, 1):
            assert not pattern.search(line), (
                f"{filename}:{i} — instructions collees detectees: {line.strip()}"
            )


# ── 2. PAS DE SECRETS EN DUR ───────────────────────────────────────────────

# Patterns de valeurs sensibles (longueur min + entropie)
SECRET_PATTERNS = [
    # Cles API longues (hex, 40+ chars)
    (re.compile(r'["\'][0-9a-f]{40,}["\']'), "cle API hexadecimale en dur"),
    # JWT secret (alphanum, 20+ chars entre guillemets, apres SECRET_KEY)
    (re.compile(r'SECRET_KEY["\'\]]\s*=\s*["\'][A-Za-z0-9]{16,}["\']'), "JWT secret en dur"),
    # OAuth secret
    (re.compile(r'OAUTH2_SECRET\s*=\s*["\'][A-Za-z0-9]{10,}["\']'), "OAuth secret en dur"),
    # RSA private key component (d, p, q, dp, dq, qi with long base64url)
    (re.compile(r'"d":\s*"[A-Za-z0-9_-]{50,}"'), "cle RSA privee en dur"),
]


class TestNoHardcodedSecrets:
    """Aucun secret ne doit etre en dur dans les fichiers de config."""

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", CONFIG_FILES)
    def test_no_secrets(self, filename):
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        content = filepath.read_text(encoding="utf-8")
        for pattern, description in SECRET_PATTERNS:
            match = pattern.search(content)
            assert match is None, (
                f"{filename} contient un {description}. "
                f"Utiliser os.environ.get() a la place. "
                f"Extrait: {match.group()[:60]}..."
            )

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", CONFIG_FILES)
    def test_secrets_use_environ(self, filename):
        """Les settings sensibles doivent utiliser os.environ.get()."""
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        content = filepath.read_text(encoding="utf-8")
        sensitive_keys = [
            "MEILISEARCH_API_KEY",
            "MEILISEARCH_MASTER_KEY",
            "JWT_SECRET_KEY",
        ]
        for key in sensitive_keys:
            if key not in content:
                continue
            assert f'os.environ.get("{key}"' in content or f"os.environ.get('{key}'" in content, (
                f"{filename}: {key} doit etre charge via os.environ.get()"
            )


# ── 3. PAS DE DUPLICATIONS ─────────────────────────────────────────────────

class TestNoDuplicateSettings:
    """Les settings critiques ne doivent etre definis qu'une seule fois."""

    UNIQUE_SETTINGS = [
        "DEFAULT_SITE_THEME",
        "PIPELINE['JS_COMPRESSOR']",
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", CONFIG_FILES)
    def test_no_duplicate_settings(self, filename):
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        content = filepath.read_text(encoding="utf-8")
        for setting in self.UNIQUE_SETTINGS:
            # Compte les lignes d'assignation (ignore les commentaires)
            assignment_pattern = re.compile(
                rf'^\s*{re.escape(setting)}\s*=', re.MULTILINE
            )
            matches = assignment_pattern.findall(content)
            assert len(matches) <= 1, (
                f"{filename}: '{setting}' est defini {len(matches)} fois "
                f"(attendu: 1 max). Supprimer le doublon."
            )


# ── 4. COHERENCE LMS / CMS ─────────────────────────────────────────────────

class TestLmsCmsCoherence:
    """Les settings partages entre LMS et CMS doivent etre identiques."""

    SHARED_SETTINGS = [
        "DEFAULT_SITE_THEME",
        "MEILISEARCH_ENABLED",
        "MEILISEARCH_URL",
        "MEILISEARCH_INDEX_PREFIX",
    ]

    @pytest.mark.unit
    def test_shared_settings_match(self):
        lms_path = TUTOR_PATCHES_DIR / "lms-production.py"
        cms_path = TUTOR_PATCHES_DIR / "cms-production.py"
        if not lms_path.exists() or not cms_path.exists():
            pytest.skip("Fichiers config manquants")

        lms_content = lms_path.read_text(encoding="utf-8")
        cms_content = cms_path.read_text(encoding="utf-8")

        for setting in self.SHARED_SETTINGS:
            pattern = re.compile(
                rf'^\s*{re.escape(setting)}\s*=\s*(.+)$', re.MULTILINE
            )
            lms_match = pattern.search(lms_content)
            cms_match = pattern.search(cms_content)
            if lms_match and cms_match:
                assert lms_match.group(1).strip() == cms_match.group(1).strip(), (
                    f"Incoherence LMS/CMS pour '{setting}': "
                    f"LMS={lms_match.group(1).strip()} vs CMS={cms_match.group(1).strip()}"
                )

    @pytest.mark.unit
    def test_theme_dir_in_both(self):
        """Le repertoire de themes doit etre configure dans LMS ET CMS."""
        for filename in CONFIG_FILES:
            filepath = TUTOR_PATCHES_DIR / filename
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            assert "COMPREHENSIVE_THEME_DIRS" in content, (
                f"{filename}: COMPREHENSIVE_THEME_DIRS manquant"
            )


# ── 5. STRUCTURE DES FICHIERS ──────────────────────────────────────────────

class TestConfigFileStructure:
    """Verification de la structure attendue des fichiers."""

    @pytest.mark.unit
    def test_required_files_exist(self):
        for filename in CONFIG_FILES:
            filepath = TUTOR_PATCHES_DIR / filename
            assert filepath.exists(), f"Fichier requis manquant: {filename}"

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", CONFIG_FILES)
    def test_imports_present(self, filename):
        filepath = TUTOR_PATCHES_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        content = filepath.read_text(encoding="utf-8")
        assert "import os" in content, f"{filename}: import os manquant"
        assert "import json" in content, f"{filename}: import json manquant"

    @pytest.mark.unit
    def test_lms_inherits_production(self):
        filepath = TUTOR_PATCHES_DIR / "lms-production.py"
        if not filepath.exists():
            pytest.skip("lms-production.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "from lms.envs.production import" in content

    @pytest.mark.unit
    def test_cms_inherits_production(self):
        filepath = TUTOR_PATCHES_DIR / "cms-production.py"
        if not filepath.exists():
            pytest.skip("cms-production.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "from cms.envs.production import" in content
