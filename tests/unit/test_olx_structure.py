# -*- coding: utf-8 -*-
"""
Tests unitaires — Structure OLX des cours (olx-courses/).

Verifie:
- XML valide dans tous les fichiers
- Integrite referentielle (course → chapter → sequential → vertical → html/problem)
- Conventions de nommage
- Pas de fichiers orphelins
"""
import xml.etree.ElementTree as ET

import pytest

from tests.conftest import OLX_DIR

# ── Helpers ─────────────────────────────────────────────────────────────────


def _parse_xml(filepath):
    """Parse un fichier XML et retourne le root element."""
    try:
        tree = ET.parse(filepath)
        return tree.getroot()
    except ET.ParseError as exc:
        pytest.fail(f"XML invalide dans {filepath.name}: {exc}")


def _collect_xml_files(subdir):
    """Collecte tous les .xml dans un sous-dossier OLX."""
    folder = OLX_DIR / subdir
    if not folder.exists():
        return []
    return sorted(folder.glob("*.xml"))


# ── 1. VALIDITE XML ────────────────────────────────────────────────────────

class TestXmlValidity:
    """Tous les fichiers XML doivent etre parsables."""

    @pytest.mark.unit
    def test_course_xml_valid(self):
        course_xml = OLX_DIR / "course.xml"
        if not course_xml.exists():
            pytest.skip("course.xml absent")
        root = _parse_xml(course_xml)
        assert root.tag == "course", f"Tag racine attendu: course, obtenu: {root.tag}"

    @pytest.mark.unit
    @pytest.mark.parametrize("subdir", ["chapter", "sequential", "vertical", "html"])
    def test_all_xml_files_valid(self, subdir):
        files = _collect_xml_files(subdir)
        if not files:
            pytest.skip(f"Aucun fichier dans {subdir}/")
        for filepath in files:
            _parse_xml(filepath)  # echoue avec pytest.fail si invalide

    @pytest.mark.unit
    @pytest.mark.parametrize("subdir", ["chapter", "sequential", "vertical", "html"])
    def test_xml_has_display_name(self, subdir):
        """Chaque element OLX doit avoir un display_name."""
        files = _collect_xml_files(subdir)
        if not files:
            pytest.skip(f"Aucun fichier dans {subdir}/")
        for filepath in files:
            root = _parse_xml(filepath)
            assert "display_name" in root.attrib, (
                f"{subdir}/{filepath.name}: attribut display_name manquant"
            )


# ── 2. INTEGRITE REFERENTIELLE ──────────────────────────────────────────────

class TestReferentialIntegrity:
    """Chaque reference url_name doit pointer vers un fichier existant."""

    @pytest.mark.unit
    def test_course_references_chapters(self):
        course_xml = OLX_DIR / "course.xml"
        if not course_xml.exists():
            pytest.skip("course.xml absent")
        root = _parse_xml(course_xml)
        for chapter_ref in root.findall("chapter"):
            url_name = chapter_ref.get("url_name")
            assert url_name, "Reference chapter sans url_name"
            chapter_file = OLX_DIR / "chapter" / f"{url_name}.xml"
            assert chapter_file.exists(), (
                f"chapter/{url_name}.xml reference dans course.xml mais absent"
            )

    @pytest.mark.unit
    def test_chapters_reference_sequentials(self):
        chapter_files = _collect_xml_files("chapter")
        if not chapter_files:
            pytest.skip("Aucun chapter")
        for filepath in chapter_files:
            root = _parse_xml(filepath)
            for seq_ref in root.findall("sequential"):
                url_name = seq_ref.get("url_name")
                assert url_name, f"{filepath.name}: sequential sans url_name"
                seq_file = OLX_DIR / "sequential" / f"{url_name}.xml"
                assert seq_file.exists(), (
                    f"sequential/{url_name}.xml reference dans {filepath.name} mais absent"
                )

    @pytest.mark.unit
    def test_sequentials_reference_verticals(self):
        seq_files = _collect_xml_files("sequential")
        if not seq_files:
            pytest.skip("Aucun sequential")
        for filepath in seq_files:
            root = _parse_xml(filepath)
            for vert_ref in root.findall("vertical"):
                url_name = vert_ref.get("url_name")
                assert url_name, f"{filepath.name}: vertical sans url_name"
                vert_file = OLX_DIR / "vertical" / f"{url_name}.xml"
                assert vert_file.exists(), (
                    f"vertical/{url_name}.xml reference dans {filepath.name} mais absent"
                )

    @pytest.mark.unit
    def test_verticals_reference_content(self):
        """Chaque vertical doit pointer vers un html ou problem existant."""
        vert_files = _collect_xml_files("vertical")
        if not vert_files:
            pytest.skip("Aucun vertical")
        missing = []
        for filepath in vert_files:
            root = _parse_xml(filepath)
            for child in root:
                url_name = child.get("url_name")
                if not url_name:
                    continue
                tag = child.tag  # "html" ou "problem"
                content_file = OLX_DIR / tag / f"{url_name}.xml"
                if not content_file.exists():
                    missing.append(f"{tag}/{url_name}.xml (ref: {filepath.name})")
        if missing:
            pytest.fail(
                f"{len(missing)} fichier(s) de contenu manquant(s):\n"
                + "\n".join(f"  - {m}" for m in missing[:10])
                + ("\n  ..." if len(missing) > 10 else "")
            )


# ── 3. PAS DE FICHIERS ORPHELINS ───────────────────────────────────────────

class TestNoOrphanFiles:
    """Tous les fichiers XML doivent etre references quelque part."""

    @pytest.mark.unit
    def test_no_orphan_chapters(self):
        course_xml = OLX_DIR / "course.xml"
        if not course_xml.exists():
            pytest.skip("course.xml absent")
        root = _parse_xml(course_xml)
        referenced = {ch.get("url_name") for ch in root.findall("chapter")}
        actual = {f.stem for f in _collect_xml_files("chapter")}
        orphans = actual - referenced
        assert not orphans, f"Chapters orphelins (non references dans course.xml): {orphans}"

    @pytest.mark.unit
    def test_no_orphan_html(self):
        """Chaque fichier html/*.xml doit etre reference par un vertical."""
        vert_files = _collect_xml_files("vertical")
        html_files = _collect_xml_files("html")
        if not html_files:
            pytest.skip("Aucun fichier html/")
        referenced = set()
        for filepath in vert_files:
            root = _parse_xml(filepath)
            for child in root.findall("html"):
                url_name = child.get("url_name")
                if url_name:
                    referenced.add(url_name)
        actual = {f.stem for f in html_files}
        orphans = actual - referenced
        assert not orphans, f"Fichiers HTML orphelins: {orphans}"


# ── 4. CONVENTIONS DE NOMMAGE ──────────────────────────────────────────────

class TestNamingConventions:
    """Verification des conventions de nommage OLX Mission Formations."""

    @pytest.mark.unit
    def test_chapter_naming(self):
        """Chapters: s{N}_{description}"""
        for filepath in _collect_xml_files("chapter"):
            assert filepath.stem.startswith("s"), (
                f"chapter/{filepath.name}: doit commencer par 's' (ex: s1_introduction)"
            )

    @pytest.mark.unit
    def test_html_naming(self):
        """HTML: html_s{chapter}_{seq}_u{unit}_{description}"""
        for filepath in _collect_xml_files("html"):
            assert filepath.stem.startswith("html_s"), (
                f"html/{filepath.name}: doit commencer par 'html_s' "
                f"(ex: html_s1_1_u1_presentation)"
            )

    @pytest.mark.unit
    def test_course_metadata(self):
        """course.xml doit avoir les attributs obligatoires."""
        course_xml = OLX_DIR / "course.xml"
        if not course_xml.exists():
            pytest.skip("course.xml absent")
        root = _parse_xml(course_xml)
        required_attrs = ["org", "course", "url_name", "display_name"]
        for attr in required_attrs:
            assert attr in root.attrib, (
                f"course.xml: attribut '{attr}' manquant"
            )
