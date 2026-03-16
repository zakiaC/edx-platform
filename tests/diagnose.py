#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic de production — Mission Formations

Script autonome qui se connecte au serveur staging via SSH,
verifie chaque couche, et identifie la CAUSE RACINE d'un probleme.

Usage:
    python3 tests/diagnose.py                    # staging par defaut
    python3 tests/diagnose.py --host mon-serveur  # autre host SSH
    python3 tests/diagnose.py --url https://...   # autre URL

Sortie: rapport avec [OK] [FAIL] [WARN] + cause racine identifiee.
"""
import argparse
import subprocess
import sys

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_SSH_HOST = "staging-openedx"
DEFAULT_LMS_URL = "https://academie.staging.missionformations.com"
DEFAULT_CONTAINER = "tutor_local-lms-1"

# ── Helpers ─────────────────────────────────────────────────────────────────

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

results = []
root_causes = []


def ok(msg):
    results.append(("OK", msg))
    print(f"  {GREEN}[OK]{RESET}   {msg}")


def fail(msg, fix="", cause=""):
    results.append(("FAIL", msg))
    print(f"  {RED}[FAIL]{RESET} {msg}")
    if cause:
        root_causes.append({"symptom": msg, "cause": cause, "fix": fix})
        print(f"         {CYAN}Cause: {cause}{RESET}")
    if fix:
        print(f"         {YELLOW}Fix: {fix}{RESET}")


def warn(msg):
    results.append(("WARN", msg))
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def info(msg):
    print(f"  {DIM}       {msg}{RESET}")


def ssh(host, cmd, timeout=20):
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", host, cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def curl(url, timeout=10):
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
        fail(f"SSH vers {host} echoue: {err}",
             fix=f"ssh {host}",
             cause="Connexion SSH refusee ou cle invalide")
        return False


# ── Couche 1: Infra ─────────────────────────────────────────────────────────

def check_infra(host, container):
    print(f"\n{BOLD}=== COUCHE 1 — Infra (containers + ressources serveur) ==={RESET}")

    # Ressources serveur
    code, out, _ = ssh(host, "df -h / | tail -1 | awk '{print $5}'")
    if code == 0 and out:
        usage = int(out.replace("%", "")) if out.replace("%", "").isdigit() else 0
        if usage > 90:
            fail(f"Disque {out} plein",
                 fix="Nettoyer: docker system prune -a --volumes",
                 cause=f"Disque a {out} — les services crashent quand le disque est plein (MySQL, MongoDB)")
        elif usage > 80:
            warn(f"Disque a {out} — surveiller")
        else:
            ok(f"Disque a {out}")

    code, out, _ = ssh(host, "free -m | awk '/Mem:/{printf \"%d/%dMB (%.0f%%)\", $3, $2, $3/$2*100}'")
    if code == 0 and out:
        ok(f"RAM: {out}")
        # Extraire le pourcentage
        import re
        pct_match = re.search(r'\((\d+)%\)', out)
        if pct_match and int(pct_match.group(1)) > 90:
            warn(f"RAM a plus de 90% — risque d'OOM killer sur MySQL/MongoDB")

    # LMS container
    code, out, _ = ssh(host, f"docker ps --filter name={container} --format '{{{{.Status}}}}'")
    if code == 0 and "Up" in out:
        ok(f"Container {container} actif ({out})")
    else:
        # Pourquoi le container est down ?
        code2, logs, _ = ssh(host, f"docker logs {container} --tail 10 2>&1")
        fail(f"Container {container} DOWN",
             fix=f"docker start {container}",
             cause=f"Container arrete. Derniers logs: {logs[:150]}")
        return False

    # Services critiques — avec diagnostic approfondi sur chaque FAIL
    services = [
        ("mysql", "tutor_local-mysql-1",
         "mysqladmin ping -h localhost --silent 2>&1"),
        ("mongodb", "tutor_local-mongodb-1",
         "mongosh --eval 'db.runCommand({ping:1})' --quiet 2>&1 || mongo --eval 'db.runCommand({ping:1})' --quiet 2>&1"),
        ("redis", "tutor_local-redis-1",
         "redis-cli ping 2>&1"),
    ]

    for svc_name, svc_container, check_cmd in services:
        # D'abord verifier si le container tourne
        code, out, _ = ssh(host, f"docker ps --filter name={svc_container} --format '{{{{.Status}}}}'")
        if not out or "Up" not in (out or ""):
            # Container down — pourquoi ?
            code2, logs, _ = ssh(host, f"docker logs {svc_container} --tail 5 2>&1")
            code3, inspect, _ = ssh(host, f"docker inspect {svc_container} --format '{{{{.State.ExitCode}}}} {{{{.State.OOMKilled}}}}' 2>&1")

            if "true" in (inspect or "").lower():
                fail(f"{svc_name} container KILLED par OOM",
                     fix=f"Augmenter la RAM ou reduire les limites. Puis: docker start {svc_container}",
                     cause=f"Out Of Memory — le serveur n'a plus assez de RAM. Le kernel a tue {svc_name}.")
            elif "137" in (inspect or ""):
                fail(f"{svc_name} container crash (exit code 137 = OOM/SIGKILL)",
                     fix=f"docker start {svc_container}",
                     cause=f"Processus tue par le systeme (OOM killer ou kill manuel). Logs: {logs[:100]}")
            else:
                fail(f"{svc_name} container DOWN (exit: {inspect})",
                     fix=f"docker start {svc_container}",
                     cause=f"Container arrete. Logs: {logs[:150]}")
            continue

        # Container tourne — verifier si le service repond
        code, out, _ = ssh(host, f"docker exec {svc_container} {check_cmd}")
        if code == 0 and ("alive" in out.lower() or "pong" in out.lower() or "ok" in out.lower() or "1" in out):
            ok(f"{svc_name} repond")
        else:
            # Service ne repond pas — creuser
            code2, logs, _ = ssh(host, f"docker logs {svc_container} --tail 15 2>&1")

            if svc_name == "mysql":
                # Causes MySQL courantes
                if "disk full" in logs.lower() or "no space" in logs.lower():
                    fail(f"MySQL ne repond pas",
                         fix=f"Liberer de l'espace disque puis: docker restart {svc_container}",
                         cause="Disque plein — MySQL ne peut plus ecrire")
                elif "innodb" in logs.lower() and "corrupt" in logs.lower():
                    fail(f"MySQL ne repond pas",
                         fix=f"docker exec {svc_container} mysqlcheck --repair --all-databases",
                         cause="Tables InnoDB corrompues (crash precedent ou disque plein)")
                elif "too many connections" in logs.lower():
                    fail(f"MySQL ne repond pas",
                         fix=f"docker restart {svc_container}",
                         cause="Trop de connexions ouvertes — fuite de connexions ou pic de charge")
                elif "oom" in logs.lower() or "killed" in logs.lower():
                    fail(f"MySQL ne repond pas",
                         fix=f"Augmenter la RAM ou reduire innodb_buffer_pool_size. Puis restart.",
                         cause="MySQL tue par OOM killer — pas assez de RAM")
                elif "initializing" in logs.lower() or "starting" in logs.lower():
                    warn(f"MySQL en cours de demarrage — reessayer dans 30s")
                    info(f"Logs: {logs[-100:]}")
                else:
                    fail(f"MySQL ne repond pas",
                         fix=f"docker restart {svc_container}",
                         cause=f"Raison inconnue. Logs: {logs[-200:]}")
                    info("Verifier manuellement: docker logs tutor_local-mysql-1 --tail 30")
            else:
                fail(f"{svc_name} ne repond pas",
                     fix=f"docker restart {svc_container}",
                     cause=f"Service demarre mais ne repond pas. Logs: {logs[-150:]}")

    return True


# ── Couche 2: Config (webpack, fichiers critiques) ──────────────────────────

def check_config(host, container):
    print(f"\n{BOLD}=== COUCHE 2 — Config & Assets critiques ==={RESET}")

    # webpack-stats.json
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'ls -la /openedx/staticfiles/webpack-stats.json 2>&1'")
    if code == 0 and "No such file" not in out:
        ok("webpack-stats.json present")

        code2, out2, _ = ssh(host,
            f"docker exec {container} python3 -c \""
            f"import json; d=json.load(open('/openedx/staticfiles/webpack-stats.json')); "
            f"print(d.get('status','?'))\" 2>&1")
        if code2 == 0 and "error" not in out2.lower():
            ok(f"webpack-stats.json valide (status: {out2})")
        else:
            fail("webpack-stats.json corrompu",
                 fix=f"docker exec {container} bash -c 'cd /openedx/edx-platform && npm run webpack'",
                 cause="Le fichier JSON est invalide — probablement une compilation webpack interrompue")
    else:
        fail("webpack-stats.json MANQUANT",
             fix=(f"docker exec {container} bash -c 'cd /openedx/edx-platform && npm run webpack' && "
                  f"docker exec {container} ./manage.py lms collectstatic --noinput && "
                  f"docker restart {container}"),
             cause="collectstatic --clear a supprime le fichier, ou webpack n'a jamais ete lance. "
                   "Sans ce fichier, TOUTES les pages retournent 500.")
        return False

    # Theme
    code, out, _ = ssh(host,
        f"docker exec {container} python3 -c \""
        f"import django; django.setup(); "
        f"from django.conf import settings; "
        f"print(settings.DEFAULT_SITE_THEME)\" 2>&1")
    if "mission-theme" in (out or ""):
        ok("DEFAULT_SITE_THEME = mission-theme")
    else:
        fail(f"Theme = '{out}' au lieu de 'mission-theme'",
             fix="Verifier tutor-patches/lms-production.py",
             cause="La variable DEFAULT_SITE_THEME n'est pas definie correctement dans la config Django")

    # Staticfiles
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'ls /openedx/staticfiles/css/ 2>&1 | wc -l'")
    count = int(out.strip()) if out.strip().isdigit() else 0
    if count > 0:
        ok(f"staticfiles/css/ contient {count} fichier(s)")
    else:
        fail("staticfiles/css/ vide ou absent",
             fix=f"docker exec {container} ./manage.py lms collectstatic --noinput",
             cause="collectstatic n'a pas ete lance ou a echoue")

    return True


# ── Couche 3: App (pages HTTP) ──────────────────────────────────────────────

def check_app(lms_url, host, container):
    print(f"\n{BOLD}=== COUCHE 3 — App (pages HTTP) ==={RESET}")

    pages = [
        ("/", "Homepage"),
        ("/login", "Login"),
        ("/heartbeat", "Heartbeat API"),
        ("/contact/", "Contact"),
        ("/admin/mission-dashboard/", "Dashboard admin"),
        ("/admin/mission-dashboard/tests/", "Tests & QA"),
    ]

    statuses = {}
    for path, name in pages:
        status, body = curl(f"{lms_url}{path}")
        statuses[path] = (status, body, name)

        if status == 500:
            # Chercher l'erreur exacte dans les logs
            code, logs, _ = ssh(host,
                f"docker logs {container} --tail 30 2>&1 | grep -A3 '{path}.*500\\|Error.*{path}' | head -10")
            if not logs:
                code, logs, _ = ssh(host,
                    f"docker logs {container} --tail 30 2>&1 | grep -i -A3 'error\\|traceback' | head -10")

            # Analyser le log pour trouver la cause
            logs_lower = (logs or "").lower()
            if "webpack-stats.json" in logs_lower:
                fail(f"{name} ({path}) → 500",
                     fix=f"docker exec {container} bash -c 'cd /openedx/edx-platform && npm run webpack' && "
                         f"docker exec {container} ./manage.py lms collectstatic --noinput && "
                         f"docker restart {container}",
                     cause="webpack-stats.json manquant — main.html ne peut pas charger les bundles JS")
            elif "mako" in logs_lower or "template" in logs_lower and "error" in logs_lower:
                fail(f"{name} ({path}) → 500",
                     fix=f"docker exec {container} bash -c 'find /tmp -name \"*.mako.py\" -delete' && "
                         f"docker restart {container}",
                     cause=f"Erreur Mako (template corrompu ou variable manquante). Log: {logs[:150]}")
            elif "database" in logs_lower or "mysql" in logs_lower or "operational" in logs_lower:
                fail(f"{name} ({path}) → 500",
                     fix="docker restart tutor_local-mysql-1",
                     cause=f"Erreur base de donnees. Log: {logs[:150]}")
            elif "import" in logs_lower and "error" in logs_lower:
                fail(f"{name} ({path}) → 500",
                     fix="Verifier le code Python du plugin",
                     cause=f"ImportError dans le code. Log: {logs[:150]}")
            elif logs:
                fail(f"{name} ({path}) → 500",
                     fix=f"docker logs {container} --tail 50",
                     cause=f"Erreur serveur. Log: {logs[:200]}")
            else:
                fail(f"{name} ({path}) → 500",
                     fix=f"docker logs {container} --tail 50 2>&1 | grep -i error",
                     cause="Erreur 500 sans log identifiable — verifier les logs manuellement")
        elif status == 0:
            fail(f"{name} ({path}) → pas de reponse",
                 fix="Verifier Caddy / DNS / TLS / firewall",
                 cause="Le serveur ne repond pas du tout — probleme reseau, DNS ou reverse proxy")
        elif status == 404:
            warn(f"{name} ({path}) → 404 (page non trouvee)")
            info("Route non enregistree — verifier urls.py du plugin ou apps.py ready()")
        elif status in (200, 302, 403):
            ok(f"{name} ({path}) → {status}")
        else:
            warn(f"{name} ({path}) → {status}")

    # Diagnostic global
    all_500 = all(s == 500 for s, _, _ in statuses.values())
    any_500 = any(s == 500 for s, _, _ in statuses.values())

    if all_500:
        print(f"\n  {RED}{BOLD}→ TOUTES les pages en 500 = probleme global (webpack / DB / config){RESET}")
    elif any_500:
        failed_pages = [name for path, (s, _, name) in statuses.items() if s == 500]
        print(f"\n  {YELLOW}{BOLD}→ Pages en 500: {', '.join(failed_pages)} = bug specifique (template / vue){RESET}")


# ── Couche 4: Theme & Custom ───────────────────────────────────────────────

def check_theme(lms_url, host, container):
    print(f"\n{BOLD}=== COUCHE 4 — Theme & Custom ==={RESET}")

    status, body = curl(f"{lms_url}/")
    if status == 200:
        if "mf-" in body:
            ok("Classes CSS 'mf-' presentes dans la homepage")
        else:
            fail("Classes CSS 'mf-' absentes de la homepage",
                 fix="npm run compile-sass + collectstatic + restart",
                 cause="Le theme mission-theme n'est pas compile ou collectstatic n'a pas copie les CSS")

        if "mission" in body.lower():
            ok("Mot 'Mission' present dans la homepage")
        else:
            warn("Mot 'Mission' absent de la homepage")
    elif status == 500:
        info("Homepage en 500 — diagnostic theme impossible (voir couche 3)")
    else:
        warn(f"Homepage retourne {status}")

    # Cache Mako
    code, out, _ = ssh(host,
        f"docker exec {container} bash -c 'find /tmp -name \"*.mako.py\" 2>/dev/null | wc -l'")
    count = int(out.strip()) if out.strip().isdigit() else 0
    if count > 100:
        warn(f"{count} fichiers cache Mako — risque de servir des templates perimes apres deploy")
        info("Fix preventif: docker exec tutor_local-lms-1 bash -c 'find /tmp -name \"*.mako.py\" -delete'")
    elif count > 0:
        ok(f"Cache Mako: {count} fichier(s) compiles")
    else:
        ok("Cache Mako vide")

    # Git sync
    code, out, _ = ssh(host,
        f"cd /root/edx-platform 2>/dev/null && git diff --name-only -- themes/ 2>/dev/null | head -5")
    if out and out.strip():
        fail(f"Fichiers theme modifies sans commit sur le serveur: {out.strip()}",
             fix="git checkout -- themes/ ou git add + git commit",
             cause="Le code sur le serveur diverge du repo — le prochain git pull va echouer")
    else:
        ok("Code serveur synchronise avec git (themes/)")

    # Git HEAD
    code, local_head, _ = ssh(host,
        "cd /root/edx-platform && git rev-parse --short HEAD 2>/dev/null")
    code2, remote_head, _ = ssh(host,
        "cd /root/edx-platform && git rev-parse --short origin/staging 2>/dev/null")
    if local_head and remote_head:
        if local_head.strip() == remote_head.strip():
            ok(f"Serveur a jour (HEAD = origin/staging = {local_head.strip()})")
        else:
            warn(f"Serveur ({local_head.strip()}) != origin/staging ({remote_head.strip()}) — git pull necessaire")


# ── Rapport final ───────────────────────────────────────────────────────────

def print_report():
    print(f"\n{BOLD}{'=' * 60}")
    print(f"RAPPORT FINAL")
    print(f"{'=' * 60}{RESET}")

    fails = [msg for status, msg in results if status == "FAIL"]
    warns = [msg for status, msg in results if status == "WARN"]
    oks = [msg for status, msg in results if status == "OK"]

    print(f"\n  {GREEN}{len(oks)} OK{RESET}  |  {YELLOW}{len(warns)} WARN{RESET}  |  {RED}{len(fails)} FAIL{RESET}")

    if root_causes:
        print(f"\n{RED}{BOLD}CAUSES RACINES IDENTIFIEES:{RESET}")
        print(f"{'-' * 60}")
        for i, rc in enumerate(root_causes, 1):
            print(f"\n  {BOLD}{i}. {rc['symptom']}{RESET}")
            print(f"     {CYAN}Cause : {rc['cause']}{RESET}")
            if rc['fix']:
                print(f"     {YELLOW}Fix   : {rc['fix']}{RESET}")

        # Identifier LA cause racine principale (cascade)
        causes_text = " ".join(rc["cause"].lower() for rc in root_causes)
        print(f"\n{BOLD}{'=' * 60}")
        print(f"CAUSE RACINE PRINCIPALE:")
        print(f"{'=' * 60}{RESET}")

        if "webpack" in causes_text:
            print(f"  {RED}{BOLD}webpack-stats.json manquant ou corrompu{RESET}")
            print(f"  Cascade: webpack absent → main.html crash → 500 sur TOUTES les pages")
            print(f"  Origine probable: collectstatic --clear a supprime le fichier")
            print(f"\n  {YELLOW}Fix complet:{RESET}")
            print(f"  docker exec tutor_local-lms-1 bash -c 'cd /openedx/edx-platform && npm run webpack'")
            print(f"  docker exec tutor_local-lms-1 ./manage.py lms collectstatic --noinput")
            print(f"  docker restart tutor_local-lms-1")
        elif "oom" in causes_text or "ram" in causes_text or "memory" in causes_text:
            print(f"  {RED}{BOLD}Memoire insuffisante (OOM){RESET}")
            print(f"  Cascade: RAM saturee → OOM killer tue MySQL/MongoDB → DB indisponible → 500")
            print(f"  Origine probable: pas assez de RAM pour tous les services Docker")
            print(f"\n  {YELLOW}Fix:{RESET}")
            print(f"  1. docker restart tutor_local-mysql-1 tutor_local-mongodb-1")
            print(f"  2. Si ca revient: augmenter la RAM du VPS (actuellement 16 Go)")
            print(f"  3. Ou reduire innodb_buffer_pool_size dans la config MySQL")
        elif "disque" in causes_text or "disk" in causes_text or "space" in causes_text:
            print(f"  {RED}{BOLD}Disque plein{RESET}")
            print(f"  Cascade: disque plein → MySQL ne peut plus ecrire → crash → 500")
            print(f"\n  {YELLOW}Fix:{RESET}")
            print(f"  docker system prune -a --volumes  # supprime images/containers inutilises")
            print(f"  Puis: docker restart tutor_local-mysql-1")
        elif "mysql" in causes_text or "database" in causes_text:
            print(f"  {RED}{BOLD}MySQL indisponible{RESET}")
            print(f"  Cascade: MySQL down → Django ne peut pas lire/ecrire → 500 sur les pages avec DB")
            print(f"\n  {YELLOW}Fix:{RESET}")
            print(f"  docker restart tutor_local-mysql-1")
            print(f"  Si ca ne marche pas: docker logs tutor_local-mysql-1 --tail 30")
        elif "mako" in causes_text or "template" in causes_text:
            print(f"  {RED}{BOLD}Cache Mako corrompu{RESET}")
            print(f"  Cascade: ancien template compile en cache → variables manquantes → 500")
            print(f"  Origine probable: deploy sans vider le cache")
            print(f"\n  {YELLOW}Fix:{RESET}")
            print(f"  docker exec tutor_local-lms-1 bash -c 'find /tmp -name \"*.mako.py\" -delete'")
            print(f"  docker restart tutor_local-lms-1")
        elif "ssh" in causes_text or "connexion" in causes_text:
            print(f"  {RED}{BOLD}Serveur inaccessible{RESET}")
            print(f"  Pas de connexion SSH — verifier que le VPS est allume et accessible")
        else:
            print(f"  {YELLOW}Cause non identifiee automatiquement{RESET}")
            print(f"  Lancer manuellement:")
            print(f"  ssh staging-openedx 'docker logs tutor_local-lms-1 --tail 50 2>&1 | grep -i error'")
    elif fails:
        print(f"\n{RED}Problemes detectes mais cause racine non identifiee.{RESET}")
        print(f"Lancer: ssh staging-openedx 'docker logs tutor_local-lms-1 --tail 50'")
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
    check_app(args.url, args.host, args.container)
    if infra_ok:
        check_theme(args.url, args.host, args.container)

    print_report()

    fails = [s for s, _ in results if s == "FAIL"]
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
