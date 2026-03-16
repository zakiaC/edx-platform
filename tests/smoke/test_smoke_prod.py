# -*- coding: utf-8 -*-
"""
Tests smoke — Verification post-deploiement.

Lancer immediatement apres un deploy:
    pytest tests/smoke/ -m smoke

Verifie:
- Homepage LMS accessible + contenu attendu
- Studio accessible
- Assets statiques charges (CSS, JS, images)
- MFE apps accessibles
- TLS valide
- Pas de page d'erreur 500
"""
import subprocess

import pytest

from tests.conftest import STAGING_LMS_URL, STAGING_CMS_URL, STAGING_MFE_URL


def _curl_status(url, timeout=15, follow_redirects=True):
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "--max-time", str(timeout),
    ]
    if follow_redirects:
        cmd.append("-L")
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0


def _curl_body(url, timeout=15):
    cmd = ["curl", "-s", "-L", "--max-time", str(timeout), url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return result.stdout


# ── 1. HOMEPAGE & PAGES CRITIQUES ──────────────────────────────────────────

class TestCriticalPages:
    """Les pages critiques repondent 200."""

    @pytest.mark.smoke
    def test_homepage_200(self, staging_urls):
        status = _curl_status(staging_urls["lms"])
        assert status == 200, f"Homepage retourne {status}"

    @pytest.mark.smoke
    def test_homepage_has_mission_content(self, staging_urls):
        body = _curl_body(staging_urls["lms"])
        assert "mission" in body.lower(), "Homepage ne contient pas 'Mission'"
        assert "mf-" in body, "Homepage ne contient pas de classes CSS Mission (mf-)"

    @pytest.mark.smoke
    def test_login_200(self, staging_urls):
        status = _curl_status(f"{staging_urls['lms']}/login")
        assert status == 200, f"/login retourne {status}"

    @pytest.mark.smoke
    def test_register_200(self, staging_urls):
        status = _curl_status(f"{staging_urls['lms']}/register")
        assert status == 200, f"/register retourne {status}"

    @pytest.mark.smoke
    def test_studio_200(self, staging_urls):
        status = _curl_status(staging_urls["cms"])
        assert status in (200, 302), f"Studio retourne {status}"

    @pytest.mark.smoke
    def test_contact_200(self, staging_urls):
        status = _curl_status(f"{staging_urls['lms']}/contact/")
        assert status == 200, f"/contact/ retourne {status}"


# ── 2. ASSETS STATIQUES ────────────────────────────────────────────────────

class TestStaticAssets:
    """Les assets CSS/JS/images sont charges."""

    @pytest.mark.smoke
    def test_favicon_loads(self, staging_urls):
        status = _curl_status(f"{staging_urls['lms']}/favicon.ico")
        assert status == 200, f"favicon.ico retourne {status}"

    @pytest.mark.smoke
    def test_logo_loads(self, staging_urls):
        status = _curl_status(
            f"{staging_urls['lms']}/theming/asset/images/logo.png"
        )
        assert status == 200, f"logo.png retourne {status}"

    @pytest.mark.smoke
    def test_css_theme_loaded(self, staging_urls):
        """Le CSS Mission est present dans la homepage."""
        body = _curl_body(staging_urls["lms"])
        # Cherche un lien vers le CSS compile du theme
        assert "lms-main" in body or "mission" in body.lower(), (
            "CSS theme Mission non detecte dans la homepage"
        )


# ── 3. MFE APPS ────────────────────────────────────────────────────────────

class TestMfeApps:
    """Les micro-frontends repondent."""

    MFE_PATHS = [
        "/account/",
        "/learning/",
        "/authoring/",
    ]

    @pytest.mark.smoke
    @pytest.mark.parametrize("path", MFE_PATHS)
    def test_mfe_accessible(self, staging_urls, path):
        status = _curl_status(f"{staging_urls['mfe']}{path}")
        # MFE retournent 200 ou 302 (redirect vers login)
        assert status in (200, 302), (
            f"MFE {path} retourne {status}"
        )


# ── 4. PAS D'ERREURS 500 ───────────────────────────────────────────────────

class TestNo500Errors:
    """Aucune page critique ne doit retourner 500."""

    PAGES = [
        "/",
        "/login",
        "/register",
        "/contact/",
        "/heartbeat",
        "/api/courses/v1/courses/",
    ]

    @pytest.mark.smoke
    @pytest.mark.parametrize("path", PAGES)
    def test_no_500(self, staging_urls, path):
        status = _curl_status(f"{staging_urls['lms']}{path}")
        assert status != 500, (
            f"{path} retourne 500 — ERREUR SERVEUR. Verifier les logs: "
            f"tutor local logs --follow lms"
        )


# ── 5. TLS ──────────────────────────────────────────────────────────────────

class TestTls:
    """Le certificat TLS est valide."""

    @pytest.mark.smoke
    def test_tls_valid(self, staging_urls):
        """Le certificat ne doit pas etre expire."""
        cmd = [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "--max-time", "10",
            staging_urls["lms"],
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        # Si curl echoue avec erreur SSL, le returncode sera non-0
        assert result.returncode == 0, (
            f"Erreur TLS: {result.stderr.strip()}"
        )

    @pytest.mark.smoke
    def test_tls_certificate_expiry(self, staging_urls):
        """Le certificat expire dans plus de 7 jours."""
        domain = staging_urls["lms"].replace("https://", "").replace("http://", "")
        cmd = [
            "bash", "-c",
            f'echo | openssl s_client -servername {domain} -connect {domain}:443 2>/dev/null '
            f'| openssl x509 -noout -checkend 604800'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, (
            f"Certificat TLS expire dans moins de 7 jours pour {domain}"
        )
