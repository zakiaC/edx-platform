# -*- coding: utf-8 -*-
"""
Tests unitaires — Theme Mission Formations (themes/mission-theme/).

Verifie:
- Presence de tous les fichiers requis
- Syntaxe Mako de base (blocs, heritage, fermeture)
- Assets statiques (CSS, JS, images)
- Pas de secrets ni URLs cassees dans les templates
"""
import re

import pytest

from tests.conftest import THEME_DIR

# ── Constantes ──────────────────────────────────────────────────────────────

LMS_TEMPLATES = THEME_DIR / "lms" / "templates"
CMS_TEMPLATES = THEME_DIR / "cms" / "templates"
LMS_STATIC = THEME_DIR / "lms" / "static"

# Templates critiques qui doivent exister
REQUIRED_TEMPLATES = [
    "index.html",
    "dashboard.html",
    "header/header.html",
    "footer.html",
    "403.html",
    "body-extra.html",
    "student_account/login_and_register.html",
    "_mf_dashboard_hero.html",
    "_mf_dashboard_sidebar.html",
    "_mf_dashboard_admin.html",
    "_mf_dashboard_formateur.html",
    "includes/_mf_brand_panel.html",
    "admin_delete_user.html",
    "admin_test_dashboard.html",
    "aide/index.html",
    "academy_manager/dashboard.html",
    "academy_manager/create.html",
    "academy_manager/detail.html",
]

REQUIRED_STATIC_TEMPLATES = [
    "static_templates/403.html",
    "static_templates/404.html",
    "static_templates/server-error.html",
]

REQUIRED_STATIC_FILES = [
    "css/lms-main-v1.css",
    "js/mf-dashboard.js",
    "images/logo.png",
    "images/favicon.ico",
]

# Couleurs Mission Formations
MF_COLORS = {
    "bleu": "#0965D0",
    "vert": "#01E8AE",
    "dark": "#0a1628",
}


# ── 1. FICHIERS REQUIS ─────────────────────────────────────────────────────

class TestRequiredFiles:
    """Tous les fichiers du theme doivent etre presents."""

    @pytest.mark.unit
    @pytest.mark.parametrize("template", REQUIRED_TEMPLATES)
    def test_lms_template_exists(self, template):
        filepath = LMS_TEMPLATES / template
        assert filepath.exists(), f"Template manquant: lms/templates/{template}"

    @pytest.mark.unit
    @pytest.mark.parametrize("template", REQUIRED_STATIC_TEMPLATES)
    def test_static_template_exists(self, template):
        filepath = LMS_TEMPLATES / template
        assert filepath.exists(), f"Template statique manquant: {template}"

    @pytest.mark.unit
    @pytest.mark.parametrize("static_file", REQUIRED_STATIC_FILES)
    def test_static_file_exists(self, static_file):
        filepath = LMS_STATIC / static_file
        assert filepath.exists(), f"Asset statique manquant: {static_file}"
        assert filepath.stat().st_size > 0, f"Asset vide: {static_file}"

    @pytest.mark.unit
    def test_scss_entry_point_exists(self):
        scss = LMS_STATIC / "sass" / "lms-main-v1.scss"
        assert scss.exists(), "Point d'entree SCSS manquant: lms-main-v1.scss"

    @pytest.mark.unit
    def test_cms_footer_exists(self):
        footer = CMS_TEMPLATES / "widgets" / "footer.html"
        assert footer.exists(), "Footer CMS manquant: cms/templates/widgets/footer.html"


# ── 2. SYNTAXE MAKO ────────────────────────────────────────────────────────

class TestMakoSyntax:
    """Verification basique de la syntaxe Mako des templates."""

    MAKO_TEMPLATES_WITH_INHERIT = [
        "index.html",
        "dashboard.html",
        "student_account/login_and_register.html",
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("template", MAKO_TEMPLATES_WITH_INHERIT)
    def test_has_inherit_directive(self, template):
        """Les templates principales doivent heriter de main.html."""
        filepath = LMS_TEMPLATES / template
        if not filepath.exists():
            pytest.skip(f"{template} absent")
        content = filepath.read_text(encoding="utf-8")
        assert "<%inherit" in content, (
            f"{template}: directive <%inherit manquante"
        )

    @pytest.mark.unit
    @pytest.mark.parametrize("template", MAKO_TEMPLATES_WITH_INHERIT)
    def test_has_pagetitle_block(self, template):
        filepath = LMS_TEMPLATES / template
        if not filepath.exists():
            pytest.skip(f"{template} absent")
        content = filepath.read_text(encoding="utf-8")
        assert "pagetitle" in content, (
            f"{template}: bloc pagetitle manquant"
        )

    @pytest.mark.unit
    def test_no_unclosed_mako_blocks(self):
        """Detecte les blocs <%block> non fermes."""
        for template_path in LMS_TEMPLATES.rglob("*.html"):
            content = template_path.read_text(encoding="utf-8", errors="ignore")
            opens = len(re.findall(r'<%block\s', content))
            closes = len(re.findall(r'</%block>', content))
            assert opens == closes, (
                f"{template_path.relative_to(THEME_DIR)}: "
                f"{opens} <%block ouvert(s) vs {closes} </%block> ferme(s)"
            )

    @pytest.mark.unit
    def test_no_unclosed_mako_defs(self):
        """Detecte les <%def> non fermes."""
        for template_path in LMS_TEMPLATES.rglob("*.html"):
            content = template_path.read_text(encoding="utf-8", errors="ignore")
            opens = len(re.findall(r'<%def\s', content))
            closes = len(re.findall(r'</%def>', content))
            assert opens == closes, (
                f"{template_path.relative_to(THEME_DIR)}: "
                f"{opens} <%def ouvert(s) vs {closes} </%def> ferme(s)"
            )

    @pytest.mark.unit
    def test_dashboard_includes_partials(self):
        """Le dashboard doit inclure ses sous-templates."""
        filepath = LMS_TEMPLATES / "dashboard.html"
        if not filepath.exists():
            pytest.skip("dashboard.html absent")
        content = filepath.read_text(encoding="utf-8")
        required_includes = [
            "_mf_dashboard_sidebar.html",
            "_mf_dashboard_hero.html",
        ]
        for include in required_includes:
            assert include in content, (
                f"dashboard.html: include manquant pour {include}"
            )


# ── 3. DESIGN SYSTEM ───────────────────────────────────────────────────────

class TestDesignSystem:
    """Les couleurs et polices Mission Formations sont presentes."""

    @pytest.mark.unit
    def test_css_contains_brand_colors(self):
        css_path = LMS_STATIC / "css" / "lms-main-v1.css"
        if not css_path.exists():
            pytest.skip("CSS compile absent")
        content = css_path.read_text(encoding="utf-8", errors="ignore")
        for name, color in MF_COLORS.items():
            # Cherche la couleur en minuscules (CSS)
            assert color.lower() in content.lower(), (
                f"Couleur {name} ({color}) absente du CSS compile"
            )

    @pytest.mark.unit
    def test_css_not_empty(self):
        css_path = LMS_STATIC / "css" / "lms-main-v1.css"
        if not css_path.exists():
            pytest.skip("CSS compile absent")
        size = css_path.stat().st_size
        assert size > 10_000, (
            f"CSS compile trop petit ({size} octets) — compilation probablement cassee"
        )

    @pytest.mark.unit
    def test_dashboard_js_has_mf_dashboard(self):
        js_path = LMS_STATIC / "js" / "mf-dashboard.js"
        if not js_path.exists():
            pytest.skip("mf-dashboard.js absent")
        content = js_path.read_text(encoding="utf-8")
        assert "MF_DASHBOARD" in content, "mf-dashboard.js: objet MF_DASHBOARD manquant"

    @pytest.mark.unit
    def test_login_js_has_brand_panel(self):
        # Le fichier peut etre a la racine lms/ ou dans js/
        for candidate in [
            LMS_STATIC.parent / "login.js",
            LMS_STATIC / "js" / "mf-login.js",
        ]:
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8")
                assert "updateBrandPanel" in content or "brandCopy" in content, (
                    f"{candidate.name}: logique brand panel manquante"
                )
                return
        pytest.skip("Aucun fichier login JS trouve")


# ── 4. SECURITE DES TEMPLATES ──────────────────────────────────────────────

class TestTemplateSecurity:
    """Pas de failles de securite dans les templates."""

    @pytest.mark.unit
    def test_no_hardcoded_passwords(self):
        """Aucun mot de passe en dur dans les templates."""
        password_pattern = re.compile(
            r'(password|passwd|secret)\s*[:=]\s*["\'][^"\']+["\']',
            re.IGNORECASE,
        )
        for template_path in LMS_TEMPLATES.rglob("*.html"):
            content = template_path.read_text(encoding="utf-8", errors="ignore")
            match = password_pattern.search(content)
            # Ignorer les champs de formulaire (type="password")
            if match and 'type=' not in match.group():
                pytest.fail(
                    f"{template_path.relative_to(THEME_DIR)}: "
                    f"possible mot de passe en dur: {match.group()[:40]}"
                )

    @pytest.mark.unit
    def test_csrf_in_forms(self):
        """Tous les formulaires POST doivent avoir un token CSRF.
        Exclusion: static_templates/ (pages Mako statiques sans contexte Django)
        et templates email (pas de formulaire interactif)."""
        form_pattern = re.compile(r'<form[^>]*method=["\']?post', re.IGNORECASE)
        csrf_pattern = re.compile(r'csrf_token|csrfmiddlewaretoken', re.IGNORECASE)
        exclude_dirs = {"static_templates", "edx_ace", "courseware"}
        for template_path in LMS_TEMPLATES.rglob("*.html"):
            if any(part in template_path.parts for part in exclude_dirs):
                continue
            content = template_path.read_text(encoding="utf-8", errors="ignore")
            if form_pattern.search(content):
                assert csrf_pattern.search(content), (
                    f"{template_path.relative_to(THEME_DIR)}: "
                    f"formulaire POST sans token CSRF"
                )
