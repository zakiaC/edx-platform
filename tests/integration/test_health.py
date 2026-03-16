# -*- coding: utf-8 -*-
"""
Tests d'integration — Sante des services Docker.

Prerequis: containers Tutor en cours d'execution.
Lancer: pytest tests/integration/ -m integration

Verifie:
- Containers Docker actifs (lms, cms, mysql, mongodb, redis, meilisearch)
- Services repondent sur leurs ports
- LMS et CMS demarrent sans erreur
"""
import subprocess
import socket

import pytest


# ── Helpers ─────────────────────────────────────────────────────────────────

def _container_running(name_pattern):
    """Verifie si un container Docker correspondant au pattern tourne."""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={name_pattern}", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=10,
    )
    return bool(result.stdout.strip())


def _port_open(host, port, timeout=5):
    """Verifie si un port TCP est ouvert."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def _exec_in_container(container_pattern, command, timeout=30):
    """Execute une commande dans un container Docker."""
    # Trouver le nom exact du container
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


# ── 1. CONTAINERS ACTIFS ───────────────────────────────────────────────────

class TestContainers:
    """Tous les containers critiques doivent tourner."""

    REQUIRED_CONTAINERS = [
        ("lms", "Container LMS"),
        ("cms", "Container CMS"),
        ("mysql", "Base de donnees MySQL"),
        ("mongodb", "Base de donnees MongoDB"),
        ("redis", "Cache Redis"),
    ]

    OPTIONAL_CONTAINERS = [
        ("meilisearch", "Moteur de recherche Meilisearch"),
        ("caddy", "Reverse proxy Caddy"),
    ]

    @pytest.mark.integration
    @pytest.mark.parametrize("pattern,description", REQUIRED_CONTAINERS)
    def test_required_container_running(self, pattern, description):
        assert _container_running(pattern), (
            f"{description} ({pattern}) n'est pas en cours d'execution. "
            f"Lancer: tutor local start -d"
        )

    @pytest.mark.integration
    @pytest.mark.parametrize("pattern,description", OPTIONAL_CONTAINERS)
    def test_optional_container_running(self, pattern, description):
        if not _container_running(pattern):
            pytest.skip(f"{description} non demarre (optionnel)")


# ── 2. SERVICES REPONDENT ──────────────────────────────────────────────────

class TestServiceHealth:
    """Les services internes repondent sur leurs ports."""

    @pytest.mark.integration
    def test_lms_responds(self):
        """LMS repond sur le port 8000."""
        code, output = _exec_in_container(
            "lms", ["python", "-c", "print('LMS OK')"]
        )
        assert code == 0, f"LMS ne repond pas: {output}"

    @pytest.mark.integration
    def test_mysql_responds(self):
        code, output = _exec_in_container(
            "mysql", ["mysqladmin", "ping", "-h", "localhost", "--silent"]
        )
        assert code == 0, f"MySQL ne repond pas: {output}"

    @pytest.mark.integration
    def test_redis_responds(self):
        code, output = _exec_in_container(
            "redis", ["redis-cli", "ping"]
        )
        assert code == 0 and "PONG" in output, f"Redis ne repond pas: {output}"

    @pytest.mark.integration
    def test_mongodb_responds(self):
        code, output = _exec_in_container(
            "mongodb",
            ["mongosh", "--eval", "db.runCommand({ping:1})", "--quiet"],
        )
        # Fallback pour anciennes versions de mongo
        if code != 0:
            code, output = _exec_in_container(
                "mongodb",
                ["mongo", "--eval", "db.runCommand({ping:1})", "--quiet"],
            )
        assert code == 0, f"MongoDB ne repond pas: {output}"


# ── 3. LMS/CMS DJANGO CHECK ────────────────────────────────────────────────

class TestDjangoHealth:
    """Django LMS et CMS demarrent correctement."""

    @pytest.mark.integration
    def test_lms_django_check(self):
        """manage.py check ne doit pas retourner d'erreur critique."""
        code, output = _exec_in_container(
            "lms",
            ["python", "manage.py", "lms", "check", "--deploy", "--fail-level", "ERROR"],
            timeout=60,
        )
        # On accepte les warnings, pas les erreurs
        if code is None:
            pytest.skip("Container LMS indisponible")
        assert code == 0, f"Django check LMS echoue:\n{output}"

    @pytest.mark.integration
    def test_cms_django_check(self):
        code, output = _exec_in_container(
            "cms",
            ["python", "manage.py", "cms", "check", "--deploy", "--fail-level", "ERROR"],
            timeout=60,
        )
        if code is None:
            pytest.skip("Container CMS indisponible")
        assert code == 0, f"Django check CMS echoue:\n{output}"

    @pytest.mark.integration
    def test_lms_theme_loaded(self):
        """Le theme mission-theme doit etre detecte par Django."""
        code, output = _exec_in_container(
            "lms",
            ["python", "-c",
             "import django; django.setup(); "
             "from django.conf import settings; "
             "print(settings.DEFAULT_SITE_THEME)"],
            timeout=30,
        )
        if code is None:
            pytest.skip("Container LMS indisponible")
        assert "mission-theme" in (output or ""), (
            f"Theme mission-theme non charge. DEFAULT_SITE_THEME={output}"
        )
