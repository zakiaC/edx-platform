#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic de production — Mission Formations

Script autonome qui se connecte au serveur staging via SSH,
verifie chaque couche, et identifie la cause racine d'un 500.

Usage:
    python3 tests/diagnose.py                    # staging par defaut
    python3 tests/diagnose.py --host mon-serveur  # autre host SSH
    python3 tests/diagnose.py --url https://...   # autre URL

Sortie: rapport avec [OK] [FAIL] [WARN] pour chaque verification.
"""
import argparse
import subprocess
import sys
import json

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_SSH_HOST = "staging-openedx"
DEFAULT_LMS_URL = "https://academie.staging.missionformations.com"
DEFAULT_CONTAINER = "tutor_local-lms-1"

# ── Helpers ─────────────────────────────────────────────────────────────────

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

results = []


def ok(msg):
    results.append(("OK", msg))
    print(f"  {GREEN}[OK]{RESET}   {msg}")


def fail(msg, fix=""):
    results.append(("FAIL", msg))
    print(f"  {RED}[FAIL]{RESET} {msg}")
    if fix:
        print(f"         {YELLOW}Fix: {fix}{RESET}")


def warn(msg):
    results.append(("WARN", msg))
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def ssh(host, cmd, timeout=15):
    """Execute une commande via SSH et retourne (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", host, cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def curl(url, timeout=10):
    """HTTP GET et retourne (status_code, body_preview)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-w", "\n%{http_code}", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        lines = result.stdout.rsplit("\n", 1)
        status = int(lines[-1]) if lines[-1].strip().isdigit() else 0
        body = lines[0] if len(lines) > 1 else ""
        return status, body
    except Exception:
        return 0, ""


# ── Couche 0: Connectivite SSH ──────────────────────────────────────────────

def check_ssh(host):
    print(f"\n{BOLD}=== COUCHE 0 — Connectivite SSH ==={RESET}")
    code, out, err = ssh(host, "echo OK")
    if code == 0 and "OK" in out:
        ok(f"SSH vers {host} fonctionne")
        return True
    else:
        fail(f"SSH vers {host} echoue: {err}", f"Verifier: ssh {host}")
        return False


# ── Couche 1: Infra (containers) ───────────────────────────────────────────

def check_infra(host, container):
    print(f"\n{BOLD}=== COUCHE 1 — Infra (containers Docker) ==={RESET}")

    # LMS container
    code, out, _ = ssh(host, f"docker ps --filter name={container} --format '{{{{.Status}}}}'")
    if code == 0 and "Up" in out:
        ok(f"Container {container} actif ({out})")
    else:
        fail(f"Container {container} DOWN", f"docker start {container}")
        return False

    # Services critiques
    for svc, check_cmd in [
        ("mysql", "docker exec tutor_local-mysql-1 mysqladmin ping -h localhost --silent 2>&1"),
        ("mongodb", "docker exec tutor_local-mongodb-1 mongosh --eval 'db.runCommand({ping:1})' --quiet 2>&1 || docker exec tutor_local-mongodb-1 mongo --eval 'db.runCommand({ping:1})' --quiet 2>&1"),
        ("redis", "docker exec tutor_local-redis-1 redis-cli ping 2>&1"),
    ]:
        code, out, _ = ssh(host, check_cmd)
        if code == 0 and ("alive" in out.lower() or "pong" in out.lower() or "ok" in out.lower() or "1" in out):
            ok(f"{svc} repond")
        else:
            fail(f"{svc} ne repond pas: {out[:80]}", f"docker restart tutor_local-{svc}-1")

    return True


# ── Couche 2: Config (webpack, fichiers critiques) ──────────────────────────

def check_config(host, container):
    print(f"\n{BOLD}=== COUCHE 2 — Config & Assets critiques ==={RESET}")

    # webpack-stats.json
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'ls -la /openedx/staticfiles/webpack-stats.json 2>&1'")
    if code == 0 and "No such file" not in out:
        ok("webpack-stats.json present")

        # Verifier que le JSON est valide
        code2, out2, _ = ssh(host,
            f"docker exec {container} python3 -c \"import json; d=json.load(open('/openedx/staticfiles/webpack-stats.json')); print(d.get('status','?'))\" 2>&1")
        if code2 == 0 and "error" not in out2.lower():
            ok(f"webpack-stats.json valide (status: {out2})")
        else:
            fail("webpack-stats.json corrompu (JSON invalide)",
                 f"docker exec {container} bash -c 'cd /openedx/edx-platform && npm run webpack'")
    else:
        fail("webpack-stats.json MANQUANT — cause 500 sur TOUTES les pages",
             f"docker exec {container} bash -c 'cd /openedx/edx-platform && npm run webpack' && "
             f"docker exec {container} ./manage.py lms collectstatic --noinput && "
             f"docker restart {container}")
        return False

    # Theme charge
    code, out, _ = ssh(host,
        f"docker exec {container} python3 -c \""
        f"import django; django.setup(); "
        f"from django.conf import settings; "
        f"print(settings.DEFAULT_SITE_THEME)\" 2>&1")
    if "mission-theme" in (out or ""):
        ok("DEFAULT_SITE_THEME = mission-theme")
    else:
        fail(f"Theme incorrect: {out}", "Verifier tutor-patches/lms-production.py")

    # Staticfiles directory
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'ls /openedx/staticfiles/css/ 2>&1 | head -5'")
    if code == 0 and out and "No such" not in out:
        ok("Repertoire staticfiles/css/ existe")
    else:
        fail("staticfiles/css/ manquant",
             f"docker exec {container} ./manage.py lms collectstatic --noinput")

    return True


# ── Couche 3: App (pages HTTP) ──────────────────────────────────────────────

def check_app(lms_url):
    print(f"\n{BOLD}=== COUCHE 3 — App (pages HTTP) ==={RESET}")

    pages = [
        ("/", "Homepage"),
        ("/login", "Login"),
        ("/heartbeat", "Heartbeat API"),
        ("/contact/", "Contact"),
        ("/admin/mission-dashboard/", "Dashboard admin"),
        ("/admin/mission-dashboard/tests/", "Tests & QA"),
    ]

    all_500 = True
    any_500 = False

    for path, name in pages:
        status, body = curl(f"{lms_url}{path}")
        if status == 500:
            any_500 = True
            fail(f"{name} ({path}) → 500")
        elif status == 0:
            fail(f"{name} ({path}) → pas de reponse", "Verifier Caddy / DNS / TLS")
            all_500 = False
        elif status in (200, 302, 403):
            ok(f"{name} ({path}) → {status}")
            all_500 = False
        else:
            warn(f"{name} ({path}) → {status}")
            all_500 = False

    if any_500 and all_500:
        print(f"\n  {RED}{BOLD}DIAGNOSTIC: TOUTES les pages en 500 → webpack-stats.json manquant{RESET}")
    elif any_500:
        print(f"\n  {YELLOW}{BOLD}DIAGNOSTIC: Certaines pages en 500 → bug template ou cache Mako{RESET}")


# ── Couche 4: Theme & Custom ───────────────────────────────────────────────

def check_theme(lms_url, host, container):
    print(f"\n{BOLD}=== COUCHE 4 — Theme & Custom ==={RESET}")

    # Verifier que le theme est dans le HTML
    status, body = curl(f"{lms_url}/")
    if status == 200:
        if "mf-" in body:
            ok("Classes CSS 'mf-' presentes dans la homepage")
        else:
            fail("Classes CSS 'mf-' absentes — theme Mission non charge",
                 "collectstatic + restart")

        if "mission" in body.lower():
            ok("Mot 'Mission' present dans la homepage")
        else:
            warn("Mot 'Mission' absent de la homepage")
    else:
        warn(f"Homepage retourne {status} — impossible de verifier le theme")

    # Cache Mako
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'find /tmp -name \"*.mako.py\" 2>/dev/null | wc -l'")
    count = int(out.strip()) if out.strip().isdigit() else 0
    if count > 0:
        warn(f"{count} fichiers cache Mako dans /tmp — penser a vider apres deploy")
    else:
        ok("Cache Mako vide")

    # Git sync
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'cd /openedx/edx-platform 2>/dev/null && git diff --name-only -- themes/ 2>/dev/null | head -5'")
    if out and out.strip():
        fail(f"Fichiers theme modifies sans commit: {out.strip()}",
             "git checkout -- themes/ ou git commit")
    else:
        ok("Pas de modifications non commitees dans themes/")


# ── Rapport final ───────────────────────────────────────────────────────────

def print_report():
    print(f"\n{BOLD}{'=' * 60}")
    print(f"RAPPORT FINAL")
    print(f"{'=' * 60}{RESET}")

    fails = [msg for status, msg in results if status == "FAIL"]
    warns = [msg for status, msg in results if status == "WARN"]
    oks = [msg for status, msg in results if status == "OK"]

    print(f"  {GREEN}{len(oks)} OK{RESET}  |  {YELLOW}{len(warns)} WARN{RESET}  |  {RED}{len(fails)} FAIL{RESET}")

    if fails:
        print(f"\n{RED}{BOLD}PROBLEMES A CORRIGER:{RESET}")
        for i, msg in enumerate(fails, 1):
            print(f"  {i}. {msg}")

        # Diagnostic automatique
        fail_text = " ".join(fails).lower()
        print(f"\n{BOLD}DIAGNOSTIC AUTO:{RESET}")
        if "webpack" in fail_text:
            print(f"  → {RED}webpack-stats.json manquant = cause racine probable{RESET}")
            print(f"  → Fix: npm run webpack + collectstatic --noinput + restart")
        elif "500" in fail_text and "toutes" not in fail_text:
            print(f"  → {YELLOW}Template Mako corrompu ou bug dans une vue{RESET}")
            print(f"  → Fix: vider cache Mako + restart")
            print(f"  → Si persiste: docker logs {DEFAULT_CONTAINER} --tail 50")
        elif "container" in fail_text or "down" in fail_text:
            print(f"  → {RED}Infrastructure down{RESET}")
            print(f"  → Fix: tutor local start -d")
        elif "theme" in fail_text or "mf-" in fail_text:
            print(f"  → {YELLOW}Theme non charge{RESET}")
            print(f"  → Fix: collectstatic + restart")
    else:
        print(f"\n  {GREEN}{BOLD}Tout est OK — aucun probleme detecte.{RESET}")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Diagnostic production Mission Formations")
    parser.add_argument("--host", default=DEFAULT_SSH_HOST, help="Host SSH")
    parser.add_argument("--url", default=DEFAULT_LMS_URL, help="URL LMS")
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help="Nom container LMS")
    args = parser.parse_args()

    print(f"{BOLD}{'=' * 60}")
    print(f"DIAGNOSTIC PRODUCTION — Mission Formations")
    print(f"Host: {args.host}  |  URL: {args.url}")
    print(f"{'=' * 60}{RESET}")

    if not check_ssh(args.host):
        print_report()
        sys.exit(1)

    infra_ok = check_infra(args.host, args.container)
    if infra_ok:
        check_config(args.host, args.container)
    check_app(args.url)
    if infra_ok:
        check_theme(args.url, args.host, args.container)

    print_report()

    fails = [s for s, _ in results if s == "FAIL"]
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
