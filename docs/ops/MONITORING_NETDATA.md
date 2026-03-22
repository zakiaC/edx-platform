# Monitoring Netdata — Mission Formations

> Guide d'utilisation du monitoring serveur staging/prod

---

## Qu'est-ce que Netdata ?

Netdata est un outil de monitoring temps reel installe sur le serveur.
Il affiche dans un dashboard web :

- **RAM** : utilisation par process et par container
- **CPU** : charge, par coeur, par container
- **Disque** : espace utilise, vitesse lecture/ecriture
- **Reseau** : trafic entrant/sortant
- **Containers Docker** : RAM, CPU, I/O de chaque container
- **Alertes** : notifications quand un seuil est depasse

---

## Comment y acceder

Netdata n'est **pas expose sur internet** (port 19999 ferme par le pare-feu).
On y accede via un **tunnel SSH** securise.

### Etape 1 — Ouvrir le tunnel

Dans un terminal sur ton Mac :

```bash
ssh -L 19999:localhost:19999 staging-openedx
```

Ce terminal doit **rester ouvert** tant que tu veux acceder a Netdata.

### Etape 2 — Ouvrir le dashboard

Dans ton navigateur, aller a :

```
http://localhost:19999
```

Le dashboard Netdata s'affiche avec toutes les metriques en temps reel.

### Etape 3 — Fermer

Quand tu as fini, ferme le terminal SSH. Le tunnel se coupe automatiquement.

---

## Que surveiller

### Vue rapide (page d'accueil)

| Metrique | Seuil normal | Alerte si |
|----------|-------------|-----------|
| CPU | < 50% en moyenne | > 80% pendant 5 min |
| RAM | < 70% utilisee | > 85% |
| Disque | < 80% utilise | > 90% |
| Swap | 0 utilise | > 0 (manque de RAM) |

### Containers Docker (section "Docker containers")

| Container | RAM normale | Si plus |
|-----------|-----------|---------|
| tutor_local-lms-1 | 300-500 Mo | Fuite memoire ou charge |
| tutor_local-cms-1 | 200-400 Mo | Normal si edition en cours |
| tutor_local-mysql-1 | 200-300 Mo | Requetes lourdes |
| tutor_local-mongodb-1 | 50-150 Mo | Cache WiredTiger (limite 512 Mo) |
| tutor_local-mfe-1 | 15-30 Mo | Statique, ne devrait pas bouger |
| chatwoot-rails | 300-500 Mo | Normal pour Ruby/Rails |
| chatwoot-sidekiq | 300-500 Mo | Normal pour Sidekiq |
| netdata | 100-200 Mo | Le monitoring lui-meme |

### Dashboards utiles

| Dashboard | Ou le trouver | Ce qu'il montre |
|-----------|--------------|-----------------|
| **System Overview** | Page d'accueil | CPU, RAM, disque, reseau global |
| **Docker Containers** | Menu > Containers & VMs > Docker | RAM et CPU par container |
| **Disk Space** | Menu > Disks > Space Usage | Espace disque par partition |
| **Network** | Menu > Networking > eth0 | Trafic reseau |
| **MySQL** | Menu > Databases > MySQL | Requetes, connexions, buffer pool |

---

## Quand utiliser Netdata

| Situation | Ce qu'il faut regarder |
|-----------|----------------------|
| **Avant un deploy** | RAM et CPU de base (pour comparer apres) |
| **Apres un deploy** | RAM augmente ? CPU spike ? Container crash ? |
| **Site lent** | CPU > 80% ? RAM saturee ? Disque I/O eleve ? |
| **Erreur 500** | Container LMS crash ? MySQL down ? |
| **Avant la demo** | Tout est vert ? Pas d'alerte ? |
| **Diagnostic mensuel** | Tendance RAM, disque qui se remplit ? |

---

## Alertes automatiques

Netdata a des alertes preconfigures. Par defaut il alerte sur :

- RAM > 90% → alerte critique
- Disque > 90% → alerte critique
- CPU > 90% pendant 10 min → alerte warning
- Container arrete → alerte warning

Les alertes apparaissent en haut du dashboard (cloche rouge).

---

## Commandes utiles

### Verifier que Netdata tourne

```bash
ssh staging-openedx "docker ps | grep netdata"
```

### Redemarrer Netdata

```bash
ssh staging-openedx "docker restart netdata"
```

### Voir les logs Netdata

```bash
ssh staging-openedx "docker logs netdata --tail 20"
```

### Mesure rapide sans Netdata (en cas de panne)

```bash
ssh staging-openedx "docker stats --no-stream"
```

---

## Architecture

```
Mac (navigateur)
  │
  │ http://localhost:19999
  │
  ▼
Tunnel SSH (port 19999)
  │
  ▼
VPS OVH
  │
  ▼
Container netdata (:19999)
  │
  ├── /proc (CPU, RAM, processus)
  ├── /sys (disque, reseau)
  ├── /var/run/docker.sock (containers Docker)
  └── Collecte toutes les 1 seconde
```

Le container netdata a acces en **lecture seule** au systeme hote.
Il ne peut rien modifier — il observe uniquement.

---

## Infos techniques

| Element | Valeur |
|---------|--------|
| Image | netdata/netdata:latest |
| Port | 19999 (non expose, tunnel SSH) |
| RAM consommee | ~100-200 Mo |
| Restart | unless-stopped |
| Volumes | netdataconfig, netdatalib, netdatacache |
| Acces Docker | /var/run/docker.sock (lecture seule) |
| Acces systeme | /proc, /sys, /etc (lecture seule) |
