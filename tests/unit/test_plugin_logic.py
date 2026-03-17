# -*- coding: utf-8 -*-
"""
Tests unitaires — Plugin mission_central_admin.

Verifie:
- Structure du plugin (fichiers requis)
- Syntaxe Python de tous les modules
- Coherence des URLs
- Modele InternalMessageAudit
- Fonctions helpers (logic pure, sans Django)
- Configuration app
"""
import ast
import re

import pytest

from tests.conftest import PLUGIN_DIR, THEME_DIR

# ── Constantes ──────────────────────────────────────────────────────────────

PLUGIN_PY_FILES = [
    "__init__.py",
    "apps.py",
    "models.py",
    "views.py",
    "urls.py",
    "forms.py",
    "tasks.py",
    "error_views.py",
]

PLUGIN_TEMPLATES = [
    # Templates dans le theme
    THEME_DIR / "lms" / "templates" / "mission_internal_messaging.html",
    THEME_DIR / "lms" / "templates" / "mission_internal_notifications.html",
    THEME_DIR / "lms" / "templates" / "admin_central_dashboard.html",
    THEME_DIR / "lms" / "templates" / "admin_formateur_detail.html",
    THEME_DIR / "lms" / "templates" / "admin_test_dashboard.html",
    THEME_DIR / "lms" / "templates" / "admin_delete_user.html",
    THEME_DIR / "lms" / "templates" / "aide" / "index.html",
    # Academy Manager templates
    THEME_DIR / "lms" / "templates" / "academy_manager" / "dashboard.html",
    THEME_DIR / "lms" / "templates" / "academy_manager" / "create.html",
    THEME_DIR / "lms" / "templates" / "academy_manager" / "detail.html",
    # Template dans le plugin
    PLUGIN_DIR / "templates" / "mission_central_admin" / "contact.html",
]

# URLs attendues du plugin
EXPECTED_URLS = [
    ("/contact/", "contact"),
    ("/aide/", "mission-aide"),
    ("/messagerie/interne/", "mission-internal-messaging"),
    ("/notifications/interne/", "mission-internal-notifications"),
    ("/admin/mission-dashboard/", "mission-central-dashboard"),
    ("/admin/mission-dashboard/formateur/", "mission-formateur-detail"),
    ("/admin/mission-dashboard/tests/", "mission-test-dashboard"),
    ("/admin/mission-dashboard/users/delete/", "mission-delete-user"),
    ("/academy-manager/", "academy-manager"),
    ("/academy-manager/create/", "academy-create"),
    ("/api/admin/formateurs-sessions/", "mission-central-api"),
    ("/api/admin/formateurs-sessions/export.csv", "mission-central-export-csv"),
]


# ── 1. STRUCTURE DU PLUGIN ─────────────────────────────────────────────────

class TestPluginStructure:
    """Le plugin doit avoir tous les fichiers requis."""

    @pytest.mark.unit
    def test_plugin_dir_exists(self):
        assert PLUGIN_DIR.exists(), (
            f"Repertoire plugin manquant: {PLUGIN_DIR}"
        )

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", PLUGIN_PY_FILES)
    def test_module_exists(self, filename):
        filepath = PLUGIN_DIR / filename
        assert filepath.exists(), f"Module manquant: {filename}"

    @pytest.mark.unit
    def test_migrations_dir_exists(self):
        migrations = PLUGIN_DIR / "migrations"
        assert migrations.exists(), "Dossier migrations/ manquant"
        init = migrations / "__init__.py"
        assert init.exists(), "migrations/__init__.py manquant"

    @pytest.mark.unit
    def test_initial_migration_exists(self):
        migration = PLUGIN_DIR / "migrations" / "0001_initial.py"
        assert migration.exists(), "Migration initiale 0001_initial.py manquante"


# ── 2. SYNTAXE PYTHON ──────────────────────────────────────────────────────

class TestPluginPythonSyntax:
    """Tous les modules Python du plugin doivent etre parsables."""

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", PLUGIN_PY_FILES)
    def test_syntax_valid(self, filename):
        filepath = PLUGIN_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} absent")
        source = filepath.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=filename)
        except SyntaxError as exc:
            pytest.fail(f"SyntaxError dans {filename} L{exc.lineno}: {exc.msg}")

    @pytest.mark.unit
    def test_migration_syntax(self):
        migration = PLUGIN_DIR / "migrations" / "0001_initial.py"
        if not migration.exists():
            pytest.skip("Migration absente")
        source = migration.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename="0001_initial.py")
        except SyntaxError as exc:
            pytest.fail(f"SyntaxError dans migration L{exc.lineno}: {exc.msg}")


# ── 3. COHERENCE DES URLS ──────────────────────────────────────────────────

class TestPluginUrls:
    """Les URLs declarees correspondent aux vues."""

    @pytest.mark.unit
    def test_urls_file_has_expected_patterns(self):
        urls_file = PLUGIN_DIR / "urls.py"
        if not urls_file.exists():
            pytest.skip("urls.py absent")
        content = urls_file.read_text(encoding="utf-8")
        for path, name in EXPECTED_URLS:
            assert name in content, (
                f"URL name '{name}' manquant dans urls.py (path attendu: {path})"
            )

    @pytest.mark.unit
    def test_views_match_urls(self):
        """Chaque vue referencee dans urls.py doit exister dans views.py ou error_views.py."""
        urls_file = PLUGIN_DIR / "urls.py"
        views_file = PLUGIN_DIR / "views.py"
        error_views_file = PLUGIN_DIR / "error_views.py"
        if not urls_file.exists():
            pytest.skip("urls.py absent")

        urls_content = urls_file.read_text(encoding="utf-8")
        all_views_content = ""
        for f in [views_file, error_views_file]:
            if f.exists():
                all_views_content += f.read_text(encoding="utf-8")

        # Extraire les noms de fonctions referencees dans urls.py
        view_refs = re.findall(r'views\.(\w+)', urls_content)
        view_refs += re.findall(r'error_views\.(\w+)', urls_content)

        for view_name in view_refs:
            assert f"def {view_name}" in all_views_content, (
                f"Vue '{view_name}' referencee dans urls.py mais non definie"
            )


# ── 4. MODELE INTERNALMESSAGEAUDIT ──────────────────────────────────────────

class TestModelDefinition:
    """Verification de la definition du modele sans charger Django."""

    @pytest.mark.unit
    def test_model_has_required_fields(self):
        models_file = PLUGIN_DIR / "models.py"
        if not models_file.exists():
            pytest.skip("models.py absent")
        content = models_file.read_text(encoding="utf-8")

        required_fields = [
            "sender",
            "recipient_group",
            "recipient_count",
            "recipients_json",
            "subject",
            "body",
            "status",
            "task_id",
            "sent_count",
            "error_message",
            "sent_at",
            "created",
            "modified",
        ]
        for field in required_fields:
            assert field in content, (
                f"models.py: champ '{field}' manquant dans InternalMessageAudit"
            )

    @pytest.mark.unit
    def test_model_has_status_choices(self):
        models_file = PLUGIN_DIR / "models.py"
        if not models_file.exists():
            pytest.skip("models.py absent")
        content = models_file.read_text(encoding="utf-8")
        for status in ["queued", "sent", "failed"]:
            assert status in content, (
                f"models.py: statut '{status}' manquant dans les choices"
            )

    @pytest.mark.unit
    def test_model_has_recipients_method(self):
        models_file = PLUGIN_DIR / "models.py"
        if not models_file.exists():
            pytest.skip("models.py absent")
        content = models_file.read_text(encoding="utf-8")
        assert "def recipients" in content, (
            "models.py: methode recipients() manquante"
        )


# ── 5. TEMPLATES DU PLUGIN ─────────────────────────────────────────────────

class TestPluginTemplates:
    """Les templates du plugin doivent exister."""

    @pytest.mark.unit
    @pytest.mark.parametrize("template_path", PLUGIN_TEMPLATES)
    def test_template_exists(self, template_path):
        assert template_path.exists(), (
            f"Template plugin manquant: {template_path.name}"
        )

    @pytest.mark.unit
    def test_contact_template_has_form(self):
        contact = PLUGIN_DIR / "templates" / "mission_central_admin" / "contact.html"
        if not contact.exists():
            pytest.skip("contact.html absent")
        content = contact.read_text(encoding="utf-8", errors="ignore")
        assert "<form" in content, "contact.html: balise <form> manquante"
        assert "csrf" in content.lower(), "contact.html: token CSRF manquant"

    @pytest.mark.unit
    def test_messaging_template_has_form(self):
        messaging = THEME_DIR / "lms" / "templates" / "mission_internal_messaging.html"
        if not messaging.exists():
            pytest.skip("mission_internal_messaging.html absent")
        content = messaging.read_text(encoding="utf-8", errors="ignore")
        assert "<form" in content, "messaging: balise <form> manquante"


# ── 5b. SECTION AIDE ───────────────────────────────────────────────────────

class TestAideSection:
    """La section Aide est complete avec les 8 guides."""

    @pytest.mark.unit
    def test_aide_template_exists(self):
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        assert aide.exists(), "Template aide/index.html manquant"

    @pytest.mark.unit
    def test_aide_has_all_guides(self):
        """Les 8 guides doivent etre presents dans le template."""
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        if not aide.exists():
            pytest.skip("aide/index.html absent")
        content = aide.read_text(encoding="utf-8", errors="ignore")
        guides = [
            "guide-accueil",
            "guide-demarrer",
            "guide-naviguer",
            "guide-contenus",
            "guide-exercices",
            "guide-progression",
            "guide-certificat",
            "guide-discussions",
            "guide-faq",
        ]
        for guide_id in guides:
            assert guide_id in content, (
                f"aide/index.html: guide '{guide_id}' manquant"
            )

    @pytest.mark.unit
    def test_aide_has_sidebar_nav(self):
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        if not aide.exists():
            pytest.skip("aide/index.html absent")
        content = aide.read_text(encoding="utf-8", errors="ignore")
        assert "sb-guide" in content, "aide: navigation sidebar manquante"
        assert "aide-sidebar" in content, "aide: sidebar container manquant"

    @pytest.mark.unit
    def test_aide_has_faq_items(self):
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        if not aide.exists():
            pytest.skip("aide/index.html absent")
        content = aide.read_text(encoding="utf-8", errors="ignore")
        faq_count = content.count("faq-item")
        assert faq_count >= 9, (
            f"aide: seulement {faq_count // 2} questions FAQ (attendu: 9+)"
        )

    @pytest.mark.unit
    def test_aide_has_page_args(self):
        """Le template doit utiliser <%page args> (pas locals().get)."""
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        if not aide.exists():
            pytest.skip("aide/index.html absent")
        content = aide.read_text(encoding="utf-8", errors="ignore")
        assert "<%page" in content and "args=" in content, (
            "aide: doit utiliser <%page args=...> pour les variables de contexte"
        )
        assert "locals().get" not in content, (
            "aide: ne doit PAS utiliser locals().get() — utiliser <%page args>"
        )

    @pytest.mark.unit
    def test_aide_has_showguide_js(self):
        aide = THEME_DIR / "lms" / "templates" / "aide" / "index.html"
        if not aide.exists():
            pytest.skip("aide/index.html absent")
        content = aide.read_text(encoding="utf-8", errors="ignore")
        assert "function showGuide" in content, (
            "aide: fonction JavaScript showGuide() manquante"
        )


# ── 5c. ACADEMY MANAGER ────────────────────────────────────────────────────

class TestAcademyManager:
    """Les templates et modeles Academy Manager sont complets."""

    ACADEMY_TEMPLATES = [
        "academy_manager/dashboard.html",
        "academy_manager/create.html",
        "academy_manager/detail.html",
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("template", ACADEMY_TEMPLATES)
    def test_academy_template_exists(self, template):
        filepath = THEME_DIR / "lms" / "templates" / template
        assert filepath.exists(), f"Template manquant: {template}"

    @pytest.mark.unit
    @pytest.mark.parametrize("template", ACADEMY_TEMPLATES)
    def test_academy_template_uses_page_args(self, template):
        filepath = THEME_DIR / "lms" / "templates" / template
        if not filepath.exists():
            pytest.skip(f"{template} absent")
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        assert "<%page" in content and "args=" in content, (
            f"{template}: doit utiliser <%page args=...>"
        )
        assert "locals().get" not in content, (
            f"{template}: ne doit PAS utiliser locals().get()"
        )

    @pytest.mark.unit
    def test_academy_model_in_models_py(self):
        models_file = PLUGIN_DIR / "models.py"
        if not models_file.exists():
            pytest.skip("models.py absent")
        content = models_file.read_text(encoding="utf-8")
        required_models = ["Academy", "AcademyAdmin", "AcademyCourse", "AcademyEnrollment"]
        for model in required_models:
            assert f"class {model}" in content, (
                f"models.py: modele '{model}' manquant"
            )

    @pytest.mark.unit
    def test_academy_model_has_required_fields(self):
        models_file = PLUGIN_DIR / "models.py"
        if not models_file.exists():
            pytest.skip("models.py absent")
        content = models_file.read_text(encoding="utf-8")
        required_fields = [
            "name", "short_name", "slug", "academy_type", "subdomain",
            "primary_color", "secondary_color", "is_active",
            "organization_id", "client_name", "max_seats",
        ]
        for field in required_fields:
            assert field in content, (
                f"models.py: champ Academy.{field} manquant"
            )

    @pytest.mark.unit
    def test_academy_migration_exists(self):
        migration = PLUGIN_DIR / "migrations" / "0002_academy_academyadmin_academycourse_academyenrollment.py"
        assert migration.exists(), "Migration 0002 Academy manquante"

    @pytest.mark.unit
    def test_academy_create_has_form(self):
        filepath = THEME_DIR / "lms" / "templates" / "academy_manager" / "create.html"
        if not filepath.exists():
            pytest.skip("create.html absent")
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        assert "<form" in content, "create.html: balise <form> manquante"
        assert "csrf_token" in content, "create.html: token CSRF manquant"
        assert "primary_color" in content, "create.html: champ couleur manquant"

    @pytest.mark.unit
    def test_academy_detail_has_tabs(self):
        filepath = THEME_DIR / "lms" / "templates" / "academy_manager" / "detail.html"
        if not filepath.exists():
            pytest.skip("detail.html absent")
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        tabs = ["overview", "courses", "learners", "admins", "settings"]
        for tab in tabs:
            assert tab in content, f"detail.html: onglet '{tab}' manquant"

    @pytest.mark.unit
    def test_delete_user_template_exists(self):
        filepath = THEME_DIR / "lms" / "templates" / "admin_delete_user.html"
        assert filepath.exists(), "Template admin_delete_user.html manquant"

    @pytest.mark.unit
    def test_delete_user_has_confirmation(self):
        filepath = THEME_DIR / "lms" / "templates" / "admin_delete_user.html"
        if not filepath.exists():
            pytest.skip("admin_delete_user.html absent")
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        assert "Confirmer" in content or "confirmer" in content, (
            "admin_delete_user.html: confirmation de suppression manquante"
        )
        assert "csrf_token" in content, (
            "admin_delete_user.html: token CSRF manquant"
        )


# ── 6. CONFIGURATION APP ───────────────────────────────────────────────────

class TestAppConfig:
    """La configuration Django de l'app est correcte."""

    @pytest.mark.unit
    def test_app_label(self):
        apps_file = PLUGIN_DIR / "apps.py"
        if not apps_file.exists():
            pytest.skip("apps.py absent")
        content = apps_file.read_text(encoding="utf-8")
        assert "mission_central_admin" in content, (
            "apps.py: app_label ne contient pas 'mission_central_admin'"
        )

    @pytest.mark.unit
    def test_ready_registers_handlers(self):
        """La methode ready() doit enregistrer les error handlers."""
        apps_file = PLUGIN_DIR / "apps.py"
        if not apps_file.exists():
            pytest.skip("apps.py absent")
        content = apps_file.read_text(encoding="utf-8")
        assert "def ready" in content, "apps.py: methode ready() manquante"
        assert "handler403" in content, "apps.py: handler403 non enregistre"
        assert "handler404" in content, "apps.py: handler404 non enregistre"
        assert "handler500" in content, "apps.py: handler500 non enregistre"


# ── 7. CELERY TASKS ────────────────────────────────────────────────────────

class TestCeleryTasks:
    """Les taches Celery sont correctement definies."""

    @pytest.mark.unit
    def test_task_exists(self):
        tasks_file = PLUGIN_DIR / "tasks.py"
        if not tasks_file.exists():
            pytest.skip("tasks.py absent")
        content = tasks_file.read_text(encoding="utf-8")
        assert "send_internal_message_task" in content, (
            "tasks.py: tache send_internal_message_task manquante"
        )
        assert "@shared_task" in content, (
            "tasks.py: decorateur @shared_task manquant"
        )

    @pytest.mark.unit
    def test_task_is_idempotent(self):
        """La tache doit verifier si le message a deja ete envoye."""
        tasks_file = PLUGIN_DIR / "tasks.py"
        if not tasks_file.exists():
            pytest.skip("tasks.py absent")
        content = tasks_file.read_text(encoding="utf-8")
        # Doit checker le statut avant d'envoyer
        assert "sent" in content.lower() and "status" in content.lower(), (
            "tasks.py: verification d'idempotence (statut 'sent') manquante"
        )


# ── 8. TUTOR PLUGINS (config Tutor) ────────────────────────────────────────

class TestTutorPlugins:
    """Les plugins Tutor pour Mission doivent etre presents et valides."""

    TUTOR_PLUGINS = [
        "mission_theme_lock.py",
        "mission_theme_assets.py",
        "mission_central_admin.py",
        "mission_certificates_policy.py",
        "mission_braze_enrollment.py",
        "mission_csp_report_only.py",
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("plugin_name", TUTOR_PLUGINS)
    def test_tutor_plugin_syntax(self, plugin_name):
        from tests.conftest import ROOT_DIR
        filepath = ROOT_DIR / "tutor_plugins" / plugin_name
        if not filepath.exists():
            pytest.skip(f"{plugin_name} absent")
        source = filepath.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=plugin_name)
        except SyntaxError as exc:
            pytest.fail(f"SyntaxError dans {plugin_name} L{exc.lineno}: {exc.msg}")
