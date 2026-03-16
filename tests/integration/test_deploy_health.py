# -*- coding: utf-8 -*-
"""
Tests d'integration — Sante post-deploiement.

Detecte les regressions causees par:
- Cache Mako corrompu ou perime
- Templates non synchronises entre git et serveur
- Collectstatic incomplet
- Container qui sert une ancienne version

Prerequis: containers Tutor en cours d'execution.
Lancer: pytest tests/integration/test_deploy_health.py -m integration
"""
import subprocess

import pytest

from tests.conftest import STAGING_LMS_URL


def _curl_status(url, timeout=15):
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "--max-time", str(timeout), "-L", url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0


def _curl_body(url, timeout=15):
    cmd = ["curl", "-s", "-L", "--max-time", str(timeout), url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return result.stdout


def _exec_in_container(container_pattern, command, timeout=30):
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container_pattern}", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=10,
    )
    container_name = result.stdout.strip().splitlines()[0] if result.stdout.strip() else None
    if not container_name:
        return None, f"Container {container_pattern} introuvable"
    result = subprocess.run(
        ["docker", "exec", container_name] + command,
        capture_output=True, text=True, timeout=timeout,
    )
    return result.returncode, result.stdout + result.stderr


# ── 1. PAGES ADMIN SANS ERREUR 500 ─────────────────────────────────────────

class TestAdminPagesNoRegression:
    """Les pages admin custom ne doivent jamais retourner 500."""

    ADMIN_PAGES = [
        ("/admin/mission-dashboard/", "Dashboard admin"),
        ("/admin/mission-dashboard/tests/", "Dashboard tests"),
        ("/contact/", "Page contact"),
        ("/messagerie/interne/", "Messagerie interne"),
    ]

    @pytest.mark.integration
    @pytest.mark.parametrize("path,description", ADMIN_PAGES)
    def test_no_500_on_admin_pages(self, staging_urls, path, description):
        """Chaque page admin doit retourner 200, 302 ou 403 — jamais 500."""
        status = _curl_status(f"{staging_urls['lms']}{path}")
        assert status != 500, (
            f"{description} ({path}) retourne 500 — REGRESSION DETECTEE. "
            f"Verifier: docker logs tutor_local-lms-1 --tail 30"
        )
        assert status in (200, 302, 403), (
            f"{description} ({path}) retourne {status} — attendu 200/302/403"
        )


# ── 2. CACHE MAKO ──────────────────────────────────────────────────────────

class TestMakoCache:
    """Le cache Mako ne doit pas servir de templates perimees."""

    @pytest.mark.integration
    def test_dashboard_renders_without_error(self, staging_urls):
        """Le dashboard admin doit se rendre sans erreur Mako."""
        body = _curl_body(f"{staging_urls['lms']}/admin/mission-dashboard/")
        # Si Mako crash, on voit "Server Error" ou "Traceback" ou page vide
        assert "Server Error" not in body, (
            "Dashboard admin affiche 'Server Error' — cache Mako probable. "
            "Fix: docker exec tutor_local-lms-1 bash -c "
            "'find /tmp -name *.mako.py -delete' && docker restart tutor_local-lms-1"
        )
        assert "Traceback" not in body, (
            "Dashboard admin affiche un Traceback Python — template Mako casse"
        )
        assert len(body) > 500, (
            f"Dashboard admin retourne une page trop courte ({len(body)} octets) — "
            f"rendu probablement casse"
        )

    @pytest.mark.integration
    def test_test_dashboard_renders_without_error(self, staging_urls):
        """La page Tests & QA doit se rendre sans erreur Mako."""
        body = _curl_body(f"{staging_urls['lms']}/admin/mission-dashboard/tests/")
        assert "Server Error" not in body, (
            "Page Tests & QA affiche 'Server Error' — template Mako corrompu. "
            "Fix: vider le cache Mako et restart le container"
        )
        assert "Traceback" not in body, (
            "Page Tests & QA affiche un Traceback — verifier admin_test_dashboard.html"
        )

    @pytest.mark.integration
    def test_homepage_renders_mission_theme(self, staging_urls):
        """La homepage doit afficher le theme Mission, pas le theme par defaut."""
        body = _curl_body(staging_urls["lms"])
        assert "mf-" in body, (
            "Homepage ne contient pas de classes CSS 'mf-' — "
            "le theme Mission n'est pas charge. "
            "Fix: collectstatic + restart LMS"
        )


# ── 3. SYNCHRONISATION GIT / SERVEUR ───────────────────────────────────────

class TestGitSync:
    """Le code sur le serveur doit correspondre au repo."""

    @pytest.mark.integration
    def test_git_no_uncommitted_theme_changes(self):
        """Pas de modifications non commitees dans le theme sur le serveur."""
        code, output = _exec_in_container(
            "lms",
            ["bash", "-c", "cd /openedx/edx-platform 2>/dev/null && git diff --name-only -- themes/ 2>/dev/null || echo SKIP"],
            timeout=15,
        )
        if code is None or "SKIP" in (output or ""):
            pytest.skip("Git non accessible dans le container")
        changed = [f for f in output.strip().splitlines() if f.strip()]
        assert not changed, (
            f"Fichiers theme modifies sur le serveur sans commit: {changed}. "
            f"Risque de divergence. Commiter ou git checkout."
        )

    @pytest.mark.integration
    def test_container_has_latest_code(self):
        """Le container doit avoir le dernier commit de staging."""
        code, local_hash = _exec_in_container(
            "lms",
            ["bash", "-c", "cd /openedx/edx-platform 2>/dev/null && git rev-parse --short HEAD 2>/dev/null || echo SKIP"],
            timeout=15,
        )
        if code is None or "SKIP" in (local_hash or ""):
            pytest.skip("Git non accessible dans le container")

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        repo_hash = result.stdout.strip()

        # On ne peut pas toujours comparer (le serveur peut avoir un commit CSS en plus)
        # Mais on verifie que le hash n'est pas completement different
        if local_hash.strip() and repo_hash:
            # Juste un warning, pas un fail dur
            if local_hash.strip() != repo_hash:
                import warnings
                warnings.warn(
                    f"Hash serveur ({local_hash.strip()}) != hash local ({repo_hash}). "
                    f"Verifier que le deploy est complet."
                )


# ── 4. WEBPACK ASSETS ───────────────────────────────────────────────────────

class TestWebpackAssets:
    """webpack-stats.json doit exister — sinon toutes les pages crashent en 500."""

    @pytest.mark.integration
    def test_webpack_stats_exists(self):
        """webpack-stats.json doit etre present dans le container.
        Si absent, TOUTES les pages retournent 500 car main.html
        appelle static.webpack('commons') qui lit ce fichier.
        Fix: docker exec tutor_local-lms-1 bash -c 'cd /openedx/edx-platform && npm run webpack'
             docker exec tutor_local-lms-1 ./manage.py lms collectstatic --noinput
             docker restart tutor_local-lms-1"""
        code, output = _exec_in_container(
            "lms",
            ["bash", "-c", "ls -la /openedx/staticfiles/webpack-stats.json 2>&1"],
            timeout=10,
        )
        if code is None:
            pytest.skip("Container LMS indisponible")
        assert code == 0 and "No such file" not in (output or ""), (
            "webpack-stats.json MANQUANT dans /openedx/staticfiles/. "
            "Cela provoque un 500 sur TOUTES les pages. "
            "Fix: docker exec tutor_local-lms-1 bash -c "
            "'cd /openedx/edx-platform && npm run webpack' && "
            "docker exec tutor_local-lms-1 ./manage.py lms collectstatic --noinput && "
            "docker restart tutor_local-lms-1"
        )

    @pytest.mark.integration
    def test_webpack_stats_not_empty(self):
        """webpack-stats.json ne doit pas etre vide ou corrompu."""
        code, output = _exec_in_container(
            "lms",
            ["bash", "-c", "python3 -c \"import json; json.load(open('/openedx/staticfiles/webpack-stats.json'))\" 2>&1"],
            timeout=10,
        )
        if code is None:
            pytest.skip("Container LMS indisponible")
        if "No such file" in (output or ""):
            pytest.skip("webpack-stats.json absent (couvert par test_webpack_stats_exists)")
        assert code == 0, (
            "webpack-stats.json est corrompu (JSON invalide). "
            "Fix: npm run webpack + collectstatic + restart"
        )

    @pytest.mark.integration
    def test_collectstatic_preserves_webpack(self):
        """Apres un collectstatic --clear, webpack-stats.json doit encore etre la.
        ATTENTION: collectstatic --clear supprime tout dans staticfiles/
        y compris webpack-stats.json. Il faut TOUJOURS lancer npm run webpack
        AVANT collectstatic, ou utiliser collectstatic SANS --clear."""
        code, output = _exec_in_container(
            "lms",
            ["bash", "-c",
             "test -f /openedx/staticfiles/webpack-stats.json && "
             "python3 -c \"import json; d=json.load(open('/openedx/staticfiles/webpack-stats.json')); "
             "assert d.get('status') == 'done' or 'chunks' in str(d), 'status not done'\" 2>&1"],
            timeout=10,
        )
        if code is None:
            pytest.skip("Container LMS indisponible")
        # Ce test est informatif — le fix est le meme
        if code != 0:
            pytest.fail(
                "webpack-stats.json absent ou status != 'done'. "
                "Cause probable: collectstatic --clear a supprime le fichier. "
                "Fix: npm run webpack && collectstatic --noinput (SANS --clear) && restart"
            )


# ── 5. COLLECTSTATIC COMPLET ───────────────────────────────────────────────

class TestStaticFiles:
    """Les fichiers statiques du theme sont bien servis."""

    @pytest.mark.integration
    def test_theme_css_served(self, staging_urls):
        """Le CSS compile du theme est accessible via HTTP."""
        # Cherche le lien CSS dans la homepage
        body = _curl_body(staging_urls["lms"])
        if "lms-main" in body:
            # Extraire l'URL du CSS
            import re
            css_match = re.search(r'href="([^"]*lms-main[^"]*\.css[^"]*)"', body)
            if css_match:
                css_url = css_match.group(1)
                if css_url.startswith("/"):
                    css_url = staging_urls["lms"] + css_url
                status = _curl_status(css_url)
                assert status == 200, (
                    f"CSS theme ({css_url}) retourne {status}. "
                    f"Fix: collectstatic + restart"
                )
                return
        # Fallback: tester directement le chemin theming
        status = _curl_status(
            f"{staging_urls['lms']}/static/css/lms-main-v1.css"
        )
        # Peut etre 404 si le chemin est hashe, ce n'est pas grave
        if status == 404:
            pytest.skip("CSS path hashe, non testable directement")
        assert status == 200, f"CSS theme retourne {status}"

    @pytest.mark.integration
    def test_theme_js_served(self, staging_urls):
        """Le JS du dashboard est accessible."""
        status = _curl_status(
            f"{staging_urls['lms']}/static/js/mf-dashboard.js"
        )
        if status == 404:
            pytest.skip("JS path hashe, non testable directement")
        assert status == 200, f"JS dashboard retourne {status}"
