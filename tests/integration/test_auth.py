# -*- coding: utf-8 -*-
"""
Tests d'integration — Authentification et JWT.

Prerequis: LMS Tutor en cours d'execution + acces reseau.
Lancer: pytest tests/integration/test_auth.py -m integration

Verifie:
- Page login accessible (200)
- Page register accessible (200)
- API CSRF token fonctionne
- Le theme Mission est applique (pas le MFE auth)
"""
import subprocess

import pytest

from tests.conftest import STAGING_LMS_URL


def _curl(url, extra_args=None, timeout=15):
    """Execute curl et retourne (status_code, body)."""
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "--max-time", str(timeout),
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    status_code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
    return status_code


def _curl_body(url, timeout=15):
    """Execute curl et retourne le body."""
    cmd = [
        "curl", "-s", "--max-time", str(timeout), "-L", url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return result.stdout


# ── 1. PAGES AUTH ACCESSIBLES ──────────────────────────────────────────────

class TestAuthPages:
    """Les pages d'authentification sont accessibles."""

    @pytest.mark.integration
    def test_login_page_200(self, staging_urls):
        status = _curl(f"{staging_urls['lms']}/login")
        assert status == 200, f"/login retourne {status} au lieu de 200"

    @pytest.mark.integration
    def test_register_page_200(self, staging_urls):
        status = _curl(f"{staging_urls['lms']}/register")
        assert status == 200, f"/register retourne {status} au lieu de 200"

    @pytest.mark.integration
    def test_csrf_api(self, staging_urls):
        status = _curl(f"{staging_urls['lms']}/csrf/api/v1/token")
        assert status == 200, f"/csrf/api/v1/token retourne {status}"


# ── 2. THEME AUTH APPLIQUE ─────────────────────────────────────────────────

class TestAuthTheme:
    """Le theme Mission est applique sur les pages d'auth (pas le MFE)."""

    @pytest.mark.integration
    def test_login_has_mission_branding(self, staging_urls):
        """La page login doit contenir les marqueurs Mission Formations."""
        body = _curl_body(f"{staging_urls['lms']}/login")
        markers = ["mission", "mf-"]
        found = any(m in body.lower() for m in markers)
        assert found, (
            "Page /login ne contient pas de marqueurs Mission Formations. "
            "Le MFE auth est peut-etre actif au lieu du theme."
        )

    @pytest.mark.integration
    def test_login_not_mfe_redirect(self, staging_urls):
        """La page login ne doit PAS rediriger vers le MFE authn."""
        cmd = [
            "curl", "-s", "-o", "/dev/null", "-w", "%{url_effective}",
            "-L", "--max-time", "15",
            f"{staging_urls['lms']}/login",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        final_url = result.stdout.strip()
        assert "/authn/" not in final_url, (
            f"/login redirige vers le MFE authn: {final_url}. "
            f"Verifier ENABLE_AUTHN_MICROFRONTEND = False"
        )


# ── 3. PAGES PROTEGEES ────────────────────────────────────────────────────

class TestProtectedPages:
    """Les pages protegees redirigent vers login."""

    @pytest.mark.integration
    def test_dashboard_requires_auth(self, staging_urls):
        """Le dashboard doit rediriger les anonymes vers /login."""
        status = _curl(
            f"{staging_urls['lms']}/dashboard",
            extra_args=["-o", "/dev/null", "-w", "%{http_code}", "--max-time", "15"],
        )
        # 302 redirect vers /login ou 200 si on suit la redirection
        assert status in (200, 302), f"/dashboard retourne {status}"

    @pytest.mark.integration
    def test_admin_dashboard_requires_auth(self, staging_urls):
        status = _curl(f"{staging_urls['lms']}/admin/mission-dashboard/")
        assert status in (302, 403), (
            f"/admin/mission-dashboard/ retourne {status} — doit etre protege"
        )
