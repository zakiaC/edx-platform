"""
Tests unitaires — Pipeline CSS thème mission-theme
Vérifient que les causes racines identifiées sont corrigées.

Usage:
    python3 -m unittest discover -s custom-infra/tests -p 'test_*.py' -v

Ou directement:
    python3 custom-infra/tests/test_theme_css_pipeline.py
"""

import os
import re
import glob
import unittest


def find_repo_root():
    """Remonte l'arborescence pour trouver la racine du repo edx-platform."""
    path = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(path, "themes")) or os.path.isfile(
            os.path.join(path, "setup.py")
        ):
            return path
        path = os.path.dirname(path)
    # Fallback: essayer le chemin connu
    fallback = os.path.expanduser("~/edx-platform")
    if os.path.isdir(fallback):
        return fallback
    return os.getcwd()


REPO_ROOT = find_repo_root()
THEME_NAME = "mission-theme"
THEME_DIR = os.path.join(REPO_ROOT, "themes", THEME_NAME)
THEME_SASS = os.path.join(THEME_DIR, "lms", "static", "sass")
EXTRAS_FILE = os.path.join(
    THEME_SASS, "partials", "lms", "theme", "_extras.scss"
)
THEME_TEMPLATES = os.path.join(THEME_DIR, "lms", "templates")


class TestNoLegacyCSSLinks(unittest.TestCase):
    """
    Vérifie qu'aucun template n'utilise un lien CSS legacy hors pipeline.
    Anti-pattern: <link href="mf-homepage.css"> dans un template.
    """

    def _get_all_templates(self):
        """Récupère tous les fichiers HTML du thème."""
        pattern = os.path.join(THEME_TEMPLATES, "**", "*.html")
        return glob.glob(pattern, recursive=True)

    def test_no_mf_homepage_css_link(self):
        """Aucun template ne doit référencer mf-homepage.css (legacy)."""
        templates = self._get_all_templates()
        if not templates:
            self.skipTest(f"Pas de templates trouvés dans {THEME_TEMPLATES}")

        violations = []
        for tpl_path in templates:
            with open(tpl_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "mf-homepage.css" in content:
                violations.append(os.path.relpath(tpl_path, REPO_ROOT))

        self.assertEqual(
            violations,
            [],
            f"Templates utilisant le CSS legacy mf-homepage.css: {violations}. "
            f"Tous les styles doivent être dans le pipeline Sass (_extras.scss).",
        )

    def test_no_adhoc_css_links_outside_pipeline(self):
        """
        Aucun template ne doit contenir de <link> vers un CSS custom
        hors du pipeline standard (mf-*.css, mission-*.css, custom-*.css).
        Les seuls CSS autorisés sont ceux du pipeline Open edX.
        """
        templates = self._get_all_templates()
        if not templates:
            self.skipTest(f"Pas de templates trouvés dans {THEME_TEMPLATES}")

        # Pattern: <link ... href="...mf-*.css..." ou mission-*.css ou custom-*.css
        adhoc_pattern = re.compile(
            r'<link[^>]+href="[^"]*(?:mf-|mission-|custom-)[^"]*\.css[^"]*"',
            re.IGNORECASE,
        )

        violations = []
        for tpl_path in templates:
            with open(tpl_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            matches = adhoc_pattern.findall(content)
            if matches:
                rel_path = os.path.relpath(tpl_path, REPO_ROOT)
                violations.append(f"{rel_path}: {matches}")

        self.assertEqual(
            violations,
            [],
            f"Templates avec liens CSS ad-hoc hors pipeline: {violations}. "
            f"Utiliser _extras.scss dans le pipeline Sass.",
        )


class TestExtrasScssInPipeline(unittest.TestCase):
    """
    Vérifie que _extras.scss est correctement intégré dans le pipeline
    Sass du thème et sera compilé dans le bundle lms-main-v1.
    """

    def test_extras_file_exists(self):
        """Le fichier _extras.scss doit exister."""
        self.assertTrue(
            os.path.isfile(EXTRAS_FILE),
            f"_extras.scss introuvable: {EXTRAS_FILE}",
        )

    def test_extras_file_not_empty(self):
        """Le fichier _extras.scss ne doit pas être vide."""
        if not os.path.isfile(EXTRAS_FILE):
            self.skipTest("_extras.scss n'existe pas")

        size = os.path.getsize(EXTRAS_FILE)
        self.assertGreater(
            size, 50, f"_extras.scss semble vide ou quasi-vide ({size} bytes)"
        )

    def test_extras_contains_mf_classes(self):
        """_extras.scss doit contenir les classes mf-* du design Mission."""
        if not os.path.isfile(EXTRAS_FILE):
            self.skipTest("_extras.scss n'existe pas")

        with open(EXTRAS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        required_classes = ["mf-nav", "mf-hero"]
        optional_classes = ["mf-section", "mf-footer", "mf-card"]

        for cls in required_classes:
            self.assertIn(
                cls,
                content,
                f"Classe obligatoire .{cls} absente de _extras.scss",
            )

        found_optional = sum(1 for cls in optional_classes if cls in content)
        self.assertGreater(
            found_optional,
            0,
            f"Aucune classe optionnelle ({optional_classes}) trouvée dans _extras.scss",
        )

    def test_entry_point_exists(self):
        """
        Un entry-point lms-main-v1.scss doit exister dans le thème
        pour override le pipeline LMS core.
        """
        entry_v1 = os.path.join(THEME_SASS, "lms-main-v1.scss")
        self.assertTrue(
            os.path.isfile(entry_v1),
            f"Entry-point manquant: {entry_v1}. "
            f"Sans ce fichier, le thème ne peut pas injecter _extras.scss "
            f"dans le bundle lms-main-v1 compilé.",
        )

    def test_entry_point_imports_extras(self):
        """L'entry-point doit importer _extras.scss (directement ou indirectement)."""
        entry_v1 = os.path.join(THEME_SASS, "lms-main-v1.scss")
        if not os.path.isfile(entry_v1):
            self.skipTest("Entry-point lms-main-v1.scss absent")

        with open(entry_v1, "r", encoding="utf-8") as f:
            content = f.read()

        # Vérifier import direct de extras
        has_extras_import = bool(
            re.search(r"@import\s+['\"].*extras['\"]", content)
        )

        self.assertTrue(
            has_extras_import,
            f"lms-main-v1.scss n'importe pas _extras.scss. "
            f"Ajouter: @import 'partials/lms/theme/extras';",
        )

    def test_entry_point_imports_core_first(self):
        """L'entry-point doit importer le core LMS AVANT les extras."""
        entry_v1 = os.path.join(THEME_SASS, "lms-main-v1.scss")
        if not os.path.isfile(entry_v1):
            self.skipTest("Entry-point lms-main-v1.scss absent")

        with open(entry_v1, "r", encoding="utf-8") as f:
            content = f.read()

        core_match = re.search(r"@import\s+['\"].*lms-main-v1['\"]", content)
        extras_match = re.search(r"@import\s+['\"].*extras['\"]", content)

        if core_match and extras_match:
            self.assertLess(
                core_match.start(),
                extras_match.start(),
                "L'import du core LMS doit précéder l'import des extras. "
                "Sinon les variables et mixins du core ne sont pas disponibles.",
            )


class TestNoViewIndexDependency(unittest.TestCase):
    """
    Vérifie que les sélecteurs CSS du thème ne dépendent PAS de
    body.view-index, qui n'est pas présent sur la homepage LMS réelle.

    C'est la cause racine #1 identifiée dans le RCA.
    """

    def test_no_body_view_index_in_extras(self):
        """_extras.scss ne doit PAS contenir body.view-index."""
        if not os.path.isfile(EXTRAS_FILE):
            self.skipTest("_extras.scss n'existe pas")

        with open(EXTRAS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Chercher toutes les variantes
        patterns = [
            r"body\.view-index",
            r"body\s+\.view-index",
            r"\.view-index\s*\{",
        ]

        violations = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                violations.extend(matches)

        self.assertEqual(
            violations,
            [],
            f"_extras.scss contient des sélecteurs dépendant de view-index: "
            f"{violations}. "
            f"Le body réel de la homepage est <body class='ltr lang_fr'> "
            f"(PAS view-index). Utiliser .mf-home comme scope à la place.",
        )

    def test_no_view_index_in_any_theme_scss(self):
        """Aucun fichier Sass du thème ne doit utiliser body.view-index."""
        pattern_path = os.path.join(THEME_SASS, "**", "*.scss")
        scss_files = glob.glob(pattern_path, recursive=True)

        if not scss_files:
            self.skipTest(f"Pas de fichiers .scss trouvés dans {THEME_SASS}")

        violations = []
        for scss_path in scss_files:
            with open(scss_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if re.search(r"body\.view-index|\.view-index", content):
                violations.append(os.path.relpath(scss_path, REPO_ROOT))

        self.assertEqual(
            violations,
            [],
            f"Fichiers Sass utilisant view-index: {violations}. "
            f"Ce sélecteur ne matche pas le body réel de la homepage.",
        )

    def test_scoping_uses_mf_prefix(self):
        """
        Si un scope est utilisé dans _extras.scss, il doit utiliser
        le préfixe mf- (convention projet), pas une classe Open edX interne.
        """
        if not os.path.isfile(EXTRAS_FILE):
            self.skipTest("_extras.scss n'existe pas")

        with open(EXTRAS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Chercher les sélecteurs de scope (premier niveau)
        # On vérifie qu'il n'y a pas de dépendance sur des classes internes edX
        edx_internal_selectors = [
            r"body\.view-",
            r"\.courses-container",
            r"\.find-courses",
            r"#content\b",
        ]

        violations = []
        for sel_pattern in edx_internal_selectors:
            if re.search(sel_pattern, content):
                matches = re.findall(sel_pattern, content)
                violations.extend(matches)

        self.assertEqual(
            violations,
            [],
            f"_extras.scss dépend de sélecteurs internes Open edX: {violations}. "
            f"Utiliser des classes mf-* contrôlées par le thème.",
        )


class TestThemeDirectoryStructure(unittest.TestCase):
    """Vérifie que la structure du thème est correcte pour Open edX."""

    def test_theme_directory_exists(self):
        """Le répertoire du thème doit exister."""
        self.assertTrue(
            os.path.isdir(THEME_DIR),
            f"Répertoire thème introuvable: {THEME_DIR}",
        )

    def test_sass_directory_structure(self):
        """La structure Sass doit suivre la convention Open edX theming."""
        required_dirs = [
            os.path.join(THEME_SASS),
            os.path.join(THEME_SASS, "partials"),
            os.path.join(THEME_SASS, "partials", "lms"),
            os.path.join(THEME_SASS, "partials", "lms", "theme"),
        ]

        for dir_path in required_dirs:
            self.assertTrue(
                os.path.isdir(dir_path),
                f"Répertoire manquant dans la structure Sass: {dir_path}",
            )


if __name__ == "__main__":
    print(f"\nRepo root: {REPO_ROOT}")
    print(f"Theme dir: {THEME_DIR}")
    print(f"Extras:    {EXTRAS_FILE}")
    print()
    unittest.main(verbosity=2)
