# Mail Ingestion Test Hyperbios

Outil Python pour envoyer des emails de test vers une boite Microsoft 365 d'ingestion, en simulant plusieurs profils d'expediteurs sans posseder leurs boites.

## Prerequis
- Python 3.11+
- Docker (pour le mode local Mailpit)

## Installation
```bash
make setup
```

## Configuration
- Copier `.env.example` vers `.env` et renseigner les variables si vous utilisez le mode SMTP.
- Les scenarios se trouvent dans `scenarios/scenarios.yaml`.

### Variables d'environnement (mode SMTP)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
- `SMTP_STARTTLS=true/false`
- `SMTP_FROM_REAL` (optionnel mais recommande)

Si le serveur SMTP refuse un `From` factice, l'outil retente automatiquement avec:
- `From: "<entity_display_name>" <SMTP_FROM_REAL>`
- `Reply-To` conserve l'email factice
- headers `X-Simulated-*`
- premiere ligne du body: `Simulated-From: ...`

## Mode local (Mailpit)
```bash
make local-up
```
Interface Mailpit: `http://localhost:8025`

Envoyer un email de test local:
```bash
make local-send
```

## Mode SMTP (prod-like)
```bash
ingestion-tester send --to zakia.semiai@provence.ai --scenario BANK_RELEVE_JAN
```

Batch de scenarios:
```bash
ingestion-tester batch --to zakia.semiai@provence.ai --count 30 --random --seed 42
```

Lister les scenarios:
```bash
ingestion-tester list-scenarios
```

Valider le YAML:
```bash
ingestion-tester validate-config scenarios/scenarios.yaml
```

## Logs et reporting
- `out/run_log.jsonl`: log JSONL par email envoye
- `out/summary.md`: resume global de la campagne

## Exemples de scenarios
- BANK_RELEVE_JAN (banque, releve PDF)
- TAX_AVIS_IMPOSITION (impots, avis PDF)
- SUPPLIER_FACTURE_MAT (fournisseur, facture PDF + CSV)

