# -*- coding: utf-8 -*-
"""
Tests d'integration — Endpoints API critiques.

Prerequis: LMS Tutor en cours d'execution.
Lancer: pytest tests/integration/test_api.py -m integration

Verifie:
- API heartbeat
- API courses
- API user (protege)
- API MFE config
- Meilisearch accessible
"""
import json
import subprocess

import pytest

from tests.conftest import STAGING_LMS_URL


def _curl_json(url, timeout=15):
    """Fetch une URL et retourne (status_code, json_body)."""
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "--max-time", str(timeout),
        "-H", "Accept: application/json",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    lines = result.stdout.strip().rsplit("\n", 1)
    status = int(lines[-1]) if lines[-1].isdigit() else 0
    body = lines[0] if len(lines) > 1 else ""
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        data = None
    return status, data


# ── 1. API HEARTBEAT ───────────────────────────────────────────────────────

class TestApiHeartbeat:
    """Points de sante de l'API."""

    @pytest.mark.integration
    def test_lms_heartbeat(self, staging_urls):
        status, _ = _curl_json(f"{staging_urls['lms']}/heartbeat")
        assert status == 200, f"/heartbeat retourne {status}"

    @pytest.mark.integration
    def test_cms_heartbeat(self, staging_urls):
        status, _ = _curl_json(f"{staging_urls['cms']}/heartbeat")
        assert status == 200, f"CMS /heartbeat retourne {status}"


# ── 2. API COURSES ─────────────────────────────────────────────────────────

class TestCoursesApi:
    """L'API courses est accessible."""

    @pytest.mark.integration
    def test_courses_list(self, staging_urls):
        status, data = _curl_json(f"{staging_urls['lms']}/api/courses/v1/courses/")
        assert status == 200, f"API courses retourne {status}"
        assert data is not None, "API courses ne retourne pas de JSON"
        assert "results" in data or "pagination" in data or isinstance(data, list), (
            "API courses: structure de reponse inattendue"
        )


# ── 3. API USER (PROTEGEE) ─────────────────────────────────────────────────

class TestUserApi:
    """L'API user est protegee."""

    @pytest.mark.integration
    def test_user_api_requires_auth(self, staging_urls):
        status, _ = _curl_json(f"{staging_urls['lms']}/api/user/v1/me")
        assert status in (401, 403), (
            f"/api/user/v1/me retourne {status} — doit etre protege (401/403)"
        )


# ── 4. MFE CONFIG API ──────────────────────────────────────────────────────

class TestMfeConfigApi:
    """L'API de configuration MFE fonctionne."""

    @pytest.mark.integration
    def test_mfe_config_accessible(self, staging_urls):
        status, data = _curl_json(f"{staging_urls['lms']}/api/mfe_config/v1")
        if status == 404:
            pytest.skip("MFE config API non activee")
        assert status == 200, f"MFE config API retourne {status}"
        if data:
            assert "LMS_BASE_URL" in data or "BASE_URL" in data, (
                "MFE config: cles attendues manquantes"
            )

    @pytest.mark.integration
    def test_mfe_config_has_mission_branding(self, staging_urls):
        status, data = _curl_json(f"{staging_urls['lms']}/api/mfe_config/v1")
        if status != 200 or not data:
            pytest.skip("MFE config API non disponible")
        site_name = data.get("SITE_NAME", "")
        assert "mission" in site_name.lower(), (
            f"MFE config SITE_NAME='{site_name}' — 'Mission' attendu"
        )


# ── 5. ENDPOINTS MISSION CUSTOM ────────────────────────────────────────────

class TestMissionEndpoints:
    """Les endpoints custom Mission Formations repondent."""

    @pytest.mark.integration
    def test_contact_page(self, staging_urls):
        """La page contact est accessible publiquement."""
        cmd = [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "--max-time", "15", "-L",
            f"{staging_urls['lms']}/contact/",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        status = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        assert status == 200, f"/contact/ retourne {status}"

    @pytest.mark.integration
    def test_mission_errors_preview(self, staging_urls):
        """Les pages d'erreur custom sont accessibles."""
        for path in ["/mission-errors/403", "/mission-errors/404"]:
            cmd = [
                "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                "--max-time", "10",
                f"{staging_urls['lms']}{path}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            status = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            # Ces pages retournent leur code d'erreur respectif ou 200
            assert status in (200, 403, 404), (
                f"{path} retourne {status}"
            )
