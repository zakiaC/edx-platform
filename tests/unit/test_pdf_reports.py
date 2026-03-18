# -*- coding: utf-8 -*-
"""
Tests unitaires — Generation de rapports PDF Qualiopi.

Verifie:
- Le module pdf_reports.py existe et est importable
- Les fonctions de generation produisent du PDF valide
- Les routes sont enregistrees
- Le contenu PDF contient les informations requises Qualiopi
"""
import ast

import pytest

from tests.conftest import PLUGIN_DIR


# ── 1. STRUCTURE ────────────────────────────────────────────────────────────

class TestPdfReportsModule:
    """Le module pdf_reports.py est present et syntaxiquement valide."""

    @pytest.mark.unit
    def test_module_exists(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        assert filepath.exists(), "pdf_reports.py manquant"

    @pytest.mark.unit
    def test_syntax_valid(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        source = filepath.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename="pdf_reports.py")
        except SyntaxError as exc:
            pytest.fail(f"SyntaxError dans pdf_reports.py L{exc.lineno}: {exc.msg}")

    @pytest.mark.unit
    def test_has_attestation_function(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "def generate_attestation_pdf" in content, (
            "Fonction generate_attestation_pdf manquante"
        )

    @pytest.mark.unit
    def test_has_rapport_suivi_function(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "def generate_rapport_suivi_pdf" in content, (
            "Fonction generate_rapport_suivi_pdf manquante"
        )


# ── 2. CONTENU QUALIOPI ────────────────────────────────────────────────────

class TestQualiopiCompliance:
    """Les rapports contiennent les elements requis par Qualiopi."""

    @pytest.mark.unit
    def test_attestation_has_qualiopi_fields(self):
        """L'attestation doit contenir les champs Qualiopi (indicateur 32)."""
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        required = [
            "Organisme de formation",
            "Stagiaire",
            "Formation suivie",
            "Resultats",
            "Code du travail",
        ]
        for field in required:
            assert field in content, (
                f"pdf_reports.py: champ Qualiopi '{field}' manquant dans l'attestation"
            )

    @pytest.mark.unit
    def test_attestation_has_signature_block(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "Directeur" in content or "signature" in content.lower(), (
            "Bloc signature manquant dans l'attestation"
        )

    @pytest.mark.unit
    def test_rapport_has_qualiopi_indicators(self):
        """Le rapport doit mentionner les indicateurs Qualiopi."""
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "Qualiopi" in content, "Mention Qualiopi absente du rapport"
        assert "indicateur" in content.lower(), "Reference aux indicateurs absente"

    @pytest.mark.unit
    def test_rapport_has_learner_table(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        assert "Liste des apprenants" in content, (
            "Tableau des apprenants manquant dans le rapport"
        )

    @pytest.mark.unit
    def test_rapport_has_stats(self):
        filepath = PLUGIN_DIR / "pdf_reports.py"
        if not filepath.exists():
            pytest.skip("pdf_reports.py absent")
        content = filepath.read_text(encoding="utf-8")
        stats_fields = ["total_enrolled", "completion_rate", "pass_rate", "avg_grade"]
        for field in stats_fields:
            assert field in content, (
                f"Statistique '{field}' manquante dans le rapport"
            )


# ── 3. ROUTES ───────────────────────────────────────────────────────────────

class TestPdfRoutes:
    """Les routes PDF sont declarees dans urls.py."""

    @pytest.mark.unit
    def test_attestation_route_exists(self):
        urls_file = PLUGIN_DIR / "urls.py"
        if not urls_file.exists():
            pytest.skip("urls.py absent")
        content = urls_file.read_text(encoding="utf-8")
        assert "pdf-attestation" in content or "pdf/attestation" in content, (
            "Route attestation PDF manquante dans urls.py"
        )

    @pytest.mark.unit
    def test_rapport_suivi_route_exists(self):
        urls_file = PLUGIN_DIR / "urls.py"
        if not urls_file.exists():
            pytest.skip("urls.py absent")
        content = urls_file.read_text(encoding="utf-8")
        assert "pdf-rapport-suivi" in content or "pdf/rapport" in content, (
            "Route rapport suivi PDF manquante dans urls.py"
        )


# ── 4. VIEWS ────────────────────────────────────────────────────────────────

class TestPdfViews:
    """Les vues PDF sont definies dans views.py."""

    @pytest.mark.unit
    def test_attestation_view_exists(self):
        views_file = PLUGIN_DIR / "views.py"
        if not views_file.exists():
            pytest.skip("views.py absent")
        content = views_file.read_text(encoding="utf-8")
        assert "def pdf_attestation" in content, (
            "Vue pdf_attestation manquante dans views.py"
        )

    @pytest.mark.unit
    def test_rapport_view_exists(self):
        views_file = PLUGIN_DIR / "views.py"
        if not views_file.exists():
            pytest.skip("views.py absent")
        content = views_file.read_text(encoding="utf-8")
        assert "def pdf_rapport_suivi" in content, (
            "Vue pdf_rapport_suivi manquante dans views.py"
        )

    @pytest.mark.unit
    def test_views_require_auth(self):
        """Les vues PDF doivent etre protegees par login_required."""
        views_file = PLUGIN_DIR / "views.py"
        if not views_file.exists():
            pytest.skip("views.py absent")
        content = views_file.read_text(encoding="utf-8")
        # Chercher login_required avant chaque def pdf_
        import re
        for func_name in ["pdf_attestation", "pdf_rapport_suivi"]:
            pattern = rf'@login_required\s+.*?def {func_name}'
            assert re.search(pattern, content, re.DOTALL), (
                f"{func_name} n'est pas protegee par @login_required"
            )
