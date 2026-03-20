# Specification API — App Qualiopi (Hub Central)

> Version 1.0 — 20 mars 2026
> L'app Qualiopi est le hub API unique de l'ecosysteme Mission Formations
> Tous les services communiquent via cette API

---

## ARCHITECTURE API

```
                         APP QUALIOPI — API HUB
                    ════════════════════════════════

  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │  OpenEdX    │   │    Odoo     │   │  WeWill     │   │  Dashboard  │
  │   (LMS)     │   │   (ERP)    │   │  (Chat)     │   │  Admin LMS  │
  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │                                                                    │
  │  /api/v1/webhooks/openedx/*     (Groupe 1 — Signaux LMS)          │
  │  /api/v1/webhooks/odoo/*        (Groupe 2 — Evenements ERP)       │
  │  /api/v1/webhooks/chat/*        (Groupe 3 — Evenements chat)      │
  │  /api/v1/data/*                 (Groupe 4 — Donnees dashboard)    │
  │  /api/v1/documents/*            (Groupe 5 — Generation PDFs)      │
  │  /api/v1/forms/*                (Groupe 6 — Formulaires apprenant)│
  │  /api/v1/admin/*                (Groupe 7 — CRUD registres)       │
  │  /api/v1/notifications/*        (Groupe 8 — Alertes)              │
  │  /api/v1/scorecard/*            (Groupe 9 — Indicateurs Qualiopi) │
  │  /api/v1/veille/*               (Groupe 10 — Veille reglementaire)│
  │  /api/v1/emails/*               (Groupe 11 — Templates email)     │
  │  /api/v1/automation/*           (Groupe 12 — Regles et logs)      │
  │  /api/v1/export/*               (Groupe 13 — Exports CSV/ZIP)     │
  │  /api/v1/config/*               (Groupe 14 — Configuration)       │
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘
```

---

## AUTHENTIFICATION ET SECURITE

### 3 modes d'authentification selon le client

| Client | Methode | Comment |
|--------|---------|---------|
| **OpenEdX (plugin LMS)** | Header secret interne | `X-Internal-Secret: {QUALIOPI_INTERNAL_SECRET}` — reseau Docker interne |
| **Odoo** | Signature HMAC-SHA256 | `X-Odoo-Signature: hmac(secret, body)` + IP whitelist |
| **WeWill (Chatwoot)** | Token API | `X-Chatwoot-Token: {token}` |
| **Dashboard admin LMS** | JWT OpenEdX | Cookie `edx-jwt-cookie` ou `Authorization: Bearer {jwt}` |
| **Apprenant (formulaires)** | JWT OpenEdX | Meme JWT que les MFEs |

### Verification JWT OpenEdX

```python
# L'app Qualiopi valide les JWT emis par le LMS
JWT_PUBLIC_KEY = "..."  # cle publique du LMS (dans les settings Tutor)
JWT_ALGORITHM = "RS256"
JWT_AUDIENCE = "lms-key"
JWT_ISSUER = "https://academie.staging.missionformations.com/oauth2"
```

### Verification HMAC Odoo

```python
import hmac, hashlib

def verify_odoo_signature(request):
    signature = request.headers.get('X-Odoo-Signature')
    body = request.body
    expected = hmac.new(
        ODOO_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Rate limiting

| Groupe | Limite |
|--------|--------|
| Webhooks (1-3) | 100 req/min par source |
| Data (4) | 60 req/min par user |
| Documents (5) | 10 req/min par user (generation lourde) |
| Forms (6) | 30 req/min par user |
| Admin (7) | 120 req/min par user |
| Export (13) | 5 req/min par user |

---

## GROUPE 1 — WEBHOOKS OPENEDX (signaux forwardes par le plugin LMS)

### POST /api/v1/webhooks/openedx/enrollment-created

**Declencheur** : Signal `COURSE_ENROLLMENT_CREATED`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "enrollment_created",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "user_id": 42,
    "username": "jean.dupont",
    "email": "jean@example.com",
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "mode": "honor",
    "is_active": true
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["recueil_besoin_created", "eval_pre_scheduled"]
}

// Response 400
{
  "status": "error",
  "message": "course_id not found"
}
```

### POST /api/v1/webhooks/openedx/certificate-created

**Declencheur** : Signal `CERTIFICATE_CREATED` ou `COURSE_CERT_AWARDED`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "certificate_created",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "user_id": 42,
    "username": "jean.dupont",
    "email": "jean@example.com",
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "status": "downloadable",
    "grade": "0.85",
    "mode": "honor"
  }
}

// Response 200
{
  "status": "ok",
  "actions": [
    "attestation_generated",
    "certificat_realisation_generated",
    "satisfaction_survey_sent",
    "post_assessment_sent",
    "cold_survey_scheduled_j90",
    "insertion_survey_scheduled_j180",
    "odoo_contact_updated"
  ]
}
```

### POST /api/v1/webhooks/openedx/grade-changed

**Declencheur** : Signal `COURSE_GRADE_CHANGED`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "grade_changed",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "user_id": 42,
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "percent_grade": 0.72,
    "letter_grade": "Pass",
    "passed": true
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["scorecard_updated"]
}
```

### POST /api/v1/webhooks/openedx/course-published

**Declencheur** : Signal `course_published`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "course_published",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "display_name": "Certificat VTC",
    "org": "MF-VTC",
    "start_date": "2026-04-01",
    "end_date": "2026-06-30"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["program_pdf_generated", "odoo_product_synced", "catalog_updated"]
}
```

### POST /api/v1/webhooks/openedx/login

**Declencheur** : Signal `SESSION_LOGIN_COMPLETED`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "login",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "user_id": 42,
    "username": "jean.dupont",
    "email": "jean@example.com"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["attendance_logged"]
}
```

### POST /api/v1/webhooks/openedx/unenroll

**Declencheur** : Signal `UNENROLL_DONE`
**Auth** : `X-Internal-Secret`

```json
// Request
{
  "event": "unenroll",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "user_id": 42,
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "reason": "student_request"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["abandon_log_created", "odoo_notified"]
}
```

---

## GROUPE 2 — WEBHOOKS ODOO

### POST /api/v1/webhooks/odoo/order-confirmed

**Declencheur** : Commande confirmee dans Odoo
**Auth** : HMAC-SHA256

```json
// Request
{
  "event": "order_confirmed",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "order_id": 1234,
    "order_name": "SO/2026/0042",
    "client": {
      "name": "Jean Dupont",
      "email": "jean@example.com",
      "phone": "+33612345678",
      "type": "individual"
    },
    "company": null,
    "lines": [
      {
        "product_id": 10,
        "product_name": "Certificat VTC",
        "course_id": "course-v1:MF-VTC+VTC001+2026",
        "quantity": 1,
        "unit_price": 1500.00,
        "total": 1500.00
      }
    ],
    "total_ht": 1500.00,
    "total_ttc": 1500.00,
    "payment_method": "stripe",
    "financeur": null,
    "opco": null
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["enrollment_created", "welcome_email_sent", "convention_created"]
}
```

### POST /api/v1/webhooks/odoo/order-confirmed (B2B avec OPCO)

```json
// Request — variante B2B
{
  "event": "order_confirmed",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "order_id": 1235,
    "order_name": "SO/2026/0043",
    "client": null,
    "company": {
      "name": "Entreprise ABC",
      "siret": "12345678901234",
      "contact_name": "Marie Martin",
      "contact_email": "marie@abc.com",
      "academy_id": 5
    },
    "lines": [
      {
        "product_id": 10,
        "course_id": "course-v1:MF-VTC+VTC001+2026",
        "quantity": 5,
        "unit_price": 1200.00,
        "total": 6000.00
      }
    ],
    "total_ht": 6000.00,
    "total_ttc": 6000.00,
    "financeur": {
      "type": "opco",
      "name": "OPCO Mobilites",
      "prise_en_charge": "OPC-2026-789",
      "contact_email": "formation@opco-mobilites.fr"
    },
    "stagiaires": [
      {"name": "Pierre Durand", "email": "pierre@abc.com"},
      {"name": "Sophie Leroy", "email": "sophie@abc.com"},
      {"name": "Marc Petit", "email": "marc@abc.com"},
      {"name": "Julie Grand", "email": "julie@abc.com"},
      {"name": "Thomas Blanc", "email": "thomas@abc.com"}
    ]
  }
}

// Response 200
{
  "status": "ok",
  "actions": [
    "academy_verified",
    "5_enrollments_created",
    "5_welcome_emails_sent",
    "convention_b2b_created",
    "opco_bilan_scheduled"
  ]
}
```

### POST /api/v1/webhooks/odoo/payment-received

**Declencheur** : Paiement recu dans Odoo
**Auth** : HMAC-SHA256

```json
// Request
{
  "event": "payment_received",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "payment_id": 567,
    "order_id": 1234,
    "amount": 1500.00,
    "currency": "EUR",
    "payment_method": "stripe",
    "invoice_id": 890,
    "invoice_number": "INV/2026/0042",
    "client_email": "jean@example.com",
    "course_id": "course-v1:MF-VTC+VTC001+2026"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["access_activated", "convocation_sent"]
}
```

### POST /api/v1/webhooks/odoo/convention-signed

**Declencheur** : Convention signee electroniquement dans Odoo
**Auth** : HMAC-SHA256

```json
// Request
{
  "event": "convention_signed",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "convention_id": 321,
    "order_id": 1234,
    "signed_pdf_url": "https://odoo.missionformations.com/documents/convention_321.pdf",
    "signer_name": "Jean Dupont",
    "signer_email": "jean@example.com",
    "signed_at": "2026-03-20T14:28:00Z"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["convention_archived", "scorecard_updated"]
}
```

### POST /api/v1/webhooks/odoo/invoice-created

**Declencheur** : Facture emise dans Odoo
**Auth** : HMAC-SHA256

```json
// Request
{
  "event": "invoice_created",
  "timestamp": "2026-03-20T14:30:00Z",
  "data": {
    "invoice_id": 890,
    "invoice_number": "INV/2026/0042",
    "client_name": "Jean Dupont",
    "client_email": "jean@example.com",
    "amount_ht": 1500.00,
    "amount_ttc": 1500.00,
    "tva": 0.00,
    "course_id": "course-v1:MF-VTC+VTC001+2026",
    "formation_name": "Certificat VTC",
    "pdf_url": "https://odoo.missionformations.com/invoices/INV_2026_0042.pdf"
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["financial_data_updated"]
}
```

---

## GROUPE 3 — WEBHOOKS CHAT (WeWill / Chatwoot)

### POST /api/v1/webhooks/chat/conversation-created

**Declencheur** : Nouvelle conversation dans WeWill
**Auth** : `X-Chatwoot-Token`

```json
// Request (format Chatwoot webhook)
{
  "event": "conversation_created",
  "id": 456,
  "account": {"id": 3},
  "contact": {
    "id": 789,
    "name": "Jean Dupont",
    "email": "jean@example.com",
    "phone_number": "+33612345678"
  },
  "messages": [
    {
      "id": 1001,
      "content": "Bonjour, je voudrais des informations sur la formation VTC",
      "created_at": "2026-03-20T14:30:00Z"
    }
  ],
  "labels": []
}

// Response 200
{
  "status": "ok",
  "actions": ["odoo_lead_created"]
}
```

### POST /api/v1/webhooks/chat/conversation-updated

**Declencheur** : Label ajoute sur une conversation
**Auth** : `X-Chatwoot-Token`

```json
// Request — label "reclamation" ajoute
{
  "event": "conversation_updated",
  "id": 456,
  "contact": {
    "email": "jean@example.com",
    "name": "Jean Dupont"
  },
  "labels": ["reclamation"],
  "changed_attributes": {
    "labels": {
      "previous_value": [],
      "current_value": ["reclamation"]
    }
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["reclamation_created", "receipt_sent"]
}
```

```json
// Request — label "abandon" ajoute
{
  "event": "conversation_updated",
  "id": 457,
  "contact": {
    "email": "marie@example.com"
  },
  "labels": ["abandon"],
  "changed_attributes": {
    "labels": {
      "previous_value": [],
      "current_value": ["abandon"]
    }
  }
}

// Response 200
{
  "status": "ok",
  "actions": ["abandon_alert_created", "odoo_contact_flagged"]
}
```

---

## GROUPE 4 — API DONNEES (consommees par le dashboard admin LMS)

**Auth** : JWT OpenEdX (role staff ou superuser)

### GET /api/v1/data/revenues

**Usage** : Onglet "Revenus" du dashboard admin

```json
// Response 200
{
  "period": "2026-01",
  "total_ht": 45000.00,
  "total_ttc": 45000.00,
  "by_month": [
    {"month": "2026-01", "amount": 12000.00},
    {"month": "2026-02", "amount": 15000.00},
    {"month": "2026-03", "amount": 18000.00}
  ],
  "by_formation": [
    {"course_id": "course-v1:MF-VTC+VTC001+2026", "name": "Certificat VTC", "amount": 30000.00},
    {"course_id": "course-v1:MF-IA+IA001+2026", "name": "IA en entreprise", "amount": 15000.00}
  ],
  "by_financeur": [
    {"type": "opco", "amount": 25000.00},
    {"type": "individuel", "amount": 12000.00},
    {"type": "entreprise", "amount": 8000.00}
  ],
  "cached_at": "2026-03-20T14:15:00Z",
  "cache_ttl": 900
}
```

### GET /api/v1/data/invoices?page=1&per_page=20&status=posted

**Usage** : Onglet "Factures" du dashboard admin

```json
// Response 200
{
  "total": 42,
  "page": 1,
  "per_page": 20,
  "invoices": [
    {
      "invoice_number": "INV/2026/0042",
      "client_name": "Jean Dupont",
      "formation": "Certificat VTC",
      "amount_ttc": 1500.00,
      "status": "paid",
      "date": "2026-03-15",
      "pdf_url": "https://odoo.missionformations.com/invoices/INV_2026_0042.pdf"
    }
  ]
}
```

### GET /api/v1/data/trainer-fees?period=2026-03

**Usage** : Onglet "Frais formateurs" du dashboard admin

```json
// Response 200
{
  "period": "2026-03",
  "total": 8500.00,
  "by_trainer": [
    {
      "name": "Ahmed Formateur",
      "status": "independant",
      "hours": 45,
      "rate": 80.00,
      "total": 3600.00,
      "invoices": ["FACT-2026-012"]
    }
  ],
  "by_formation": [
    {"name": "Certificat VTC", "trainer_cost": 5000.00, "revenue": 30000.00, "margin": 25000.00}
  ]
}
```

### GET /api/v1/data/kpis

**Usage** : Overview du dashboard admin (KPIs hero)

```json
// Response 200
{
  "apprenants_actifs": 127,
  "formations_actives": 12,
  "formateurs": 8,
  "academies_b2b": 5,
  "taux_completion": 73.5,
  "taux_satisfaction": 4.2,
  "taux_reussite": 85.0,
  "taux_abandon": 8.3,
  "ca_mensuel": 18000.00,
  "ca_annuel": 145000.00,
  "nps": 42,
  "reclamations_en_cours": 2,
  "updated_at": "2026-03-20T07:30:00Z"
}
```

### GET /api/v1/data/analytics?period=2026-Q1

**Usage** : Onglet "Analytics" du dashboard admin

```json
// Response 200
{
  "period": "2026-Q1",
  "enrollments_by_month": [
    {"month": "2026-01", "count": 35},
    {"month": "2026-02", "count": 42},
    {"month": "2026-03", "count": 50}
  ],
  "completion_by_course": [
    {"course": "Certificat VTC", "taux": 78.5, "inscrits": 45, "termines": 35},
    {"course": "IA en entreprise", "taux": 65.0, "inscrits": 30, "termines": 20}
  ],
  "satisfaction_by_course": [
    {"course": "Certificat VTC", "moyenne": 4.3, "nps": 45, "reponses": 32},
    {"course": "IA en entreprise", "moyenne": 4.1, "nps": 38, "reponses": 18}
  ],
  "abandons_by_course": [
    {"course": "Certificat VTC", "taux": 6.7, "count": 3},
    {"course": "IA en entreprise", "taux": 10.0, "count": 3}
  ],
  "top_financeurs": [
    {"name": "OPCO Mobilites", "amount": 25000.00, "stagiaires": 20},
    {"name": "Individuels", "amount": 12000.00, "stagiaires": 8}
  ]
}
```

### GET /api/v1/data/planning?month=2026-04

**Usage** : Onglet "Planning" du dashboard admin

```json
// Response 200
{
  "month": "2026-04",
  "sessions": [
    {
      "course_id": "course-v1:MF-VTC+VTC001+2026",
      "course_name": "Certificat VTC",
      "start_date": "2026-04-01",
      "end_date": "2026-06-30",
      "formateur": "Ahmed Formateur",
      "inscrits": 15,
      "modalite": "distanciel"
    }
  ],
  "reunions_pedagogiques": [
    {"date": "2026-04-15", "sujet": "Bilan Q1", "participants": 4}
  ],
  "echeances_qualiopi": [
    {"date": "2026-04-30", "type": "bilan_opco", "formation": "VTC Session Mars"},
    {"date": "2026-04-15", "type": "enquete_froid", "count": 12}
  ]
}
```

---

## GROUPE 5 — API DOCUMENTS (generation PDF)

**Auth** : JWT OpenEdX (role staff)

### POST /api/v1/documents/generate

**Usage** : Bouton "Generer" dans le dashboard

```json
// Request
{
  "document_type": "DOC-07",
  "params": {
    "user_id": 42,
    "course_id": "course-v1:MF-VTC+VTC001+2026"
  }
}

// Response 202 Accepted
{
  "task_id": "abc123-def456",
  "status": "pending",
  "document_type": "DOC-07",
  "estimated_seconds": 5,
  "status_url": "/api/v1/documents/abc123-def456/status"
}
```

### POST /api/v1/documents/generate-batch

**Usage** : Generer plusieurs documents d'un coup

```json
// Request
{
  "documents": [
    {"document_type": "DOC-07", "params": {"user_id": 42, "course_id": "..."}},
    {"document_type": "DOC-07", "params": {"user_id": 43, "course_id": "..."}},
    {"document_type": "DOC-07", "params": {"user_id": 44, "course_id": "..."}}
  ]
}

// Response 202 Accepted
{
  "batch_id": "batch-789",
  "tasks": [
    {"task_id": "abc123", "document_type": "DOC-07", "user_id": 42, "status": "pending"},
    {"task_id": "abc124", "document_type": "DOC-07", "user_id": 43, "status": "pending"},
    {"task_id": "abc125", "document_type": "DOC-07", "user_id": 44, "status": "pending"}
  ],
  "status_url": "/api/v1/documents/batch/batch-789/status"
}
```

### GET /api/v1/documents/{task_id}/status

```json
// Response 200 — en cours
{
  "task_id": "abc123-def456",
  "status": "generating",
  "progress": 60
}

// Response 200 — termine
{
  "task_id": "abc123-def456",
  "status": "ready",
  "document": {
    "id": 789,
    "type": "DOC-07",
    "filename": "attestation_VTC_jean_dupont.pdf",
    "download_url": "/api/v1/documents/789/download",
    "size_bytes": 45678,
    "generated_at": "2026-03-20T14:32:00Z"
  }
}

// Response 200 — erreur
{
  "task_id": "abc123-def456",
  "status": "failed",
  "error": "User not found"
}
```

### GET /api/v1/documents/{id}/download

**Response** : PDF binaire (`Content-Type: application/pdf`)
Ou redirect 302 vers l'URL S3 signee

### POST /api/v1/documents/audit-pack

**Usage** : Bouton "Dossier auditeur" → ZIP complet

```json
// Request
{
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "session_start": "2026-01-15",
  "session_end": "2026-03-15",
  "include": ["DOC-01", "DOC-02", "DOC-06", "DOC-07", "DOC-08",
              "DOC-09", "DOC-10", "DOC-11", "DOC-13", "DOC-16"]
}

// Response 202 Accepted
{
  "task_id": "zip-456",
  "status": "pending",
  "estimated_seconds": 30,
  "documents_count": 47,
  "status_url": "/api/v1/documents/zip-456/status"
}
```

### GET /api/v1/documents/list?course_id={id}&type={type}&page=1

**Usage** : Historique des documents generes

```json
// Response 200
{
  "total": 156,
  "page": 1,
  "documents": [
    {
      "id": 789,
      "type": "DOC-07",
      "type_label": "Attestation de fin de formation",
      "user_name": "Jean Dupont",
      "course_name": "Certificat VTC",
      "filename": "attestation_VTC_jean_dupont.pdf",
      "download_url": "/api/v1/documents/789/download",
      "generated_at": "2026-03-20T14:32:00Z",
      "generated_by": "auto",
      "version": 1
    }
  ]
}
```

---

## GROUPE 6 — API FORMULAIRES APPRENANT

**Auth** : JWT OpenEdX (tout utilisateur authentifie)

### GET /api/v1/forms/recueil-besoins/{course_id}

**Usage** : Afficher le formulaire de recueil des besoins

```json
// Response 200
{
  "form_id": "recueil_besoins",
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "course_name": "Certificat VTC",
  "status": "a_remplir",
  "questions": [
    {"id": "q1", "type": "scale_1_5", "label": "Niveau de connaissance du sujet"},
    {"id": "q2", "type": "text", "label": "Experience professionnelle liee"},
    {"id": "q3", "type": "text", "label": "Attentes specifiques"},
    {"id": "q4", "type": "text", "label": "Objectifs personnels"},
    {"id": "q5", "type": "checkbox_list", "label": "Contraintes", "options": [
      "Handicap", "Horaires specifiques", "Materiel adapte"
    ]}
  ]
}
```

### POST /api/v1/forms/recueil-besoins/{course_id}

```json
// Request
{
  "responses": {
    "q1": 3,
    "q2": "2 ans dans le transport",
    "q3": "Obtenir la carte VTC",
    "q4": "Reconversion professionnelle",
    "q5": ["Horaires specifiques"]
  }
}

// Response 200
{
  "status": "ok",
  "message": "Questionnaire enregistre",
  "score": 3
}
```

### GET /api/v1/forms/evaluation/{type}/{course_id}

**type** : `pre` ou `post`

```json
// Response 200
{
  "form_id": "eval_pre",
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "status": "a_remplir",
  "questions": [
    {"id": "e1", "type": "scale_1_5", "label": "Connaissances reglementaires VTC"},
    {"id": "e2", "type": "scale_1_5", "label": "Maitrise de la conduite professionnelle"},
    {"id": "e3", "type": "scale_1_5", "label": "Connaissance du marche VTC"},
    {"id": "e4", "type": "qcm", "label": "Quelle est la duree minimale d'un examen VTC ?",
     "options": ["30 min", "1h", "2h", "3h30"], "answer": 3}
  ]
}
```

### POST /api/v1/forms/evaluation/{type}/{course_id}

```json
// Request
{
  "responses": {
    "e1": 2,
    "e2": 3,
    "e3": 1,
    "e4": 3
  }
}

// Response 200
{
  "status": "ok",
  "score": 5.5,
  "max_score": 10,
  "comparison": null  // null pour pre, objet pour post
}
```

### POST /api/v1/forms/evaluation/post/{course_id}

```json
// Response 200 — avec comparaison pre/post
{
  "status": "ok",
  "score_post": 8.5,
  "score_pre": 5.5,
  "progression": 3.0,
  "comparison": {
    "e1": {"pre": 2, "post": 4, "delta": "+2"},
    "e2": {"pre": 3, "post": 5, "delta": "+2"},
    "e3": {"pre": 1, "post": 4, "delta": "+3"},
    "e4": {"pre": 3, "post": 5, "delta": "+2"}
  }
}
```

### GET /api/v1/forms/satisfaction/{type}/{course_id}

**type** : `chaud` ou `froid`

```json
// Response 200
{
  "form_id": "satisfaction_chaud",
  "questions": [
    {"id": "s1", "type": "stars_1_5", "label": "Satisfaction globale"},
    {"id": "s2", "type": "stars_1_5", "label": "Qualite du contenu"},
    {"id": "s3", "type": "stars_1_5", "label": "Qualite du formateur"},
    {"id": "s4", "type": "stars_1_5", "label": "Qualite des supports"},
    {"id": "s5", "type": "stars_1_5", "label": "Qualite de la plateforme"},
    {"id": "s6", "type": "stars_1_5", "label": "Adequation avec les objectifs"},
    {"id": "s7", "type": "radio", "label": "Rythme", "options": ["Trop lent", "Adapte", "Trop rapide"]},
    {"id": "s8", "type": "nps_0_10", "label": "Recommanderiez-vous cette formation ?"},
    {"id": "s9", "type": "text", "label": "Points forts"},
    {"id": "s10", "type": "text", "label": "Points a ameliorer"},
    {"id": "s11", "type": "text", "label": "Commentaire libre"}
  ]
}
```

### POST /api/v1/forms/satisfaction/{type}/{course_id}

```json
// Request
{
  "responses": {
    "s1": 4, "s2": 5, "s3": 4, "s4": 3, "s5": 4, "s6": 5,
    "s7": "Adapte",
    "s8": 8,
    "s9": "Contenu tres complet",
    "s10": "Plus de cas pratiques",
    "s11": ""
  }
}

// Response 200
{
  "status": "ok",
  "average": 4.2,
  "nps_category": "promoteur"
}
```

### GET /api/v1/forms/insertion/{course_id}

```json
// Response 200
{
  "form_id": "insertion",
  "questions": [
    {"id": "i1", "type": "stars_1_5", "label": "La formation a-t-elle repondu a vos attentes ?"},
    {"id": "i2", "type": "radio", "label": "Mise en pratique des acquis",
     "options": ["Oui", "Partiellement", "Non"]},
    {"id": "i3", "type": "stars_1_5", "label": "Impact sur votre activite professionnelle"},
    {"id": "i4", "type": "radio", "label": "Besoin de formation complementaire",
     "options": ["Oui", "Non"]},
    {"id": "i5", "type": "radio", "label": "Situation professionnelle actuelle",
     "options": ["En emploi (meme poste)", "En emploi (nouveau poste)", "En emploi (lie a la formation)",
                 "En recherche d'emploi", "En creation d'entreprise", "Autre"]},
    {"id": "i6", "type": "text", "label": "Suggestions d'amelioration"},
    {"id": "i7", "type": "nps_0_10", "label": "Recommanderiez-vous cette formation ?"}
  ]
}
```

---

## GROUPE 7 — API ADMIN (CRUD registres Qualiopi)

**Auth** : JWT OpenEdX (role staff ou superuser)
**Convention** : REST standard (GET list, GET detail, POST create, PUT update, DELETE)

### Reclamations

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/reclamations/` | Liste (filtre: status, urgence) |
| GET | `/api/v1/admin/reclamations/{id}/` | Detail |
| POST | `/api/v1/admin/reclamations/` | Creer |
| PUT | `/api/v1/admin/reclamations/{id}/` | Modifier (repondre, clore) |

### Formateurs

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/formateurs/` | Liste |
| GET | `/api/v1/admin/formateurs/{id}/` | Detail avec CV, diplomes |
| POST | `/api/v1/admin/formateurs/` | Creer fiche |
| PUT | `/api/v1/admin/formateurs/{id}/` | Modifier |
| POST | `/api/v1/admin/formateurs/{id}/upload/` | Upload CV, diplome, RC Pro |
| GET | `/api/v1/admin/formateurs/{id}/formations/` | Actions de formation du formateur |
| POST | `/api/v1/admin/formateurs/{id}/formations/` | Ajouter une action de formation |

### Reunions pedagogiques

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/reunions/` | Liste |
| POST | `/api/v1/admin/reunions/` | Creer |
| PUT | `/api/v1/admin/reunions/{id}/` | Modifier |
| POST | `/api/v1/admin/reunions/{id}/upload-cr/` | Upload compte-rendu PDF |

### Sous-traitants

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/sous-traitants/` | Liste |
| POST | `/api/v1/admin/sous-traitants/` | Creer |
| PUT | `/api/v1/admin/sous-traitants/{id}/` | Modifier |
| POST | `/api/v1/admin/sous-traitants/{id}/upload/` | Upload contrat, RC Pro |

### Partenariats

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/partenariats/` | Liste |
| POST | `/api/v1/admin/partenariats/` | Creer |
| PUT | `/api/v1/admin/partenariats/{id}/` | Modifier |

### Conventions

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/conventions/` | Liste (filtre: statut, type) |
| GET | `/api/v1/admin/conventions/{id}/` | Detail |
| PUT | `/api/v1/admin/conventions/{id}/` | Modifier statut |

### Points de suivi

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/points-suivi/?course_id={id}` | Liste par formation |
| POST | `/api/v1/admin/points-suivi/` | Creer un point de suivi |

### Abandons

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/abandons/` | Liste |
| PUT | `/api/v1/admin/abandons/{id}/` | Documenter cause, remediation |

### Plan amelioration

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/plan-amelioration/?annee=2026` | Detail annuel |
| POST | `/api/v1/admin/plan-amelioration/` | Creer |
| PUT | `/api/v1/admin/plan-amelioration/{id}/` | Modifier |

### Revue direction

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/revue-direction/?annee=2026` | Detail annuel |
| POST | `/api/v1/admin/revue-direction/` | Creer |
| PUT | `/api/v1/admin/revue-direction/{id}/` | Modifier |

### Bilans financeurs

| Methode | URL | Action |
|---------|-----|--------|
| GET | `/api/v1/admin/bilans-financeurs/` | Liste |
| PUT | `/api/v1/admin/bilans-financeurs/{id}/` | MAJ statut (envoye, accuse recu) |

---

## GROUPE 8 — API NOTIFICATIONS

**Auth** : JWT OpenEdX (role staff)

### GET /api/v1/notifications/?is_read=false&urgency=critical

```json
// Response 200
{
  "total": 5,
  "unread": 3,
  "notifications": [
    {
      "id": 101,
      "title": "Reclamation #12 : J+25, URGENT",
      "message": "La reclamation de Jean Dupont depasse les 25 jours. Reponse requise avant le 25/03.",
      "urgency": "high",
      "category": "reclamation",
      "related_indicator": 32,
      "is_read": false,
      "created_at": "2026-03-20T07:00:00Z",
      "action_url": "/api/v1/admin/reclamations/12/"
    }
  ]
}
```

### PUT /api/v1/notifications/{id}/read

```json
// Response 200
{"status": "ok", "is_read": true, "read_at": "2026-03-20T14:35:00Z"}
```

### PUT /api/v1/notifications/read-all

```json
// Response 200
{"status": "ok", "marked_read": 5}
```

---

## GROUPE 9 — API SCORECARD QUALIOPI

**Auth** : JWT OpenEdX (role staff)

### GET /api/v1/scorecard/current

```json
// Response 200
{
  "date": "2026-03-20",
  "conformity_rate": 78.1,
  "total_vert": 25,
  "total_orange": 5,
  "total_rouge": 2,
  "alerts_count": 7,
  "indicators": {
    "1": {"status": "vert", "label": "Conditions d'acces", "details": "Toutes infos presentes sur le site"},
    "2": {"status": "vert", "label": "Delais d'acces", "details": "Delai moyen 12j, affiche 15j"},
    "3": {"status": "vert", "label": "Indicateurs publies", "details": "MAJ il y a 2 mois"},
    "4": {"status": "orange", "label": "Accessibilite handicap", "details": "Referent identifie, procedure non publiee"},
    "14": {"status": "rouge", "label": "Abandons", "details": "Taux 16.2% (seuil 15%)"},
    "32": {"status": "rouge", "label": "Reclamations", "details": "1 reclamation > 30j sans reponse"}
  }
}
```

### GET /api/v1/scorecard/history?from=2026-01-01&to=2026-03-20

```json
// Response 200
{
  "history": [
    {"date": "2026-01-01", "conformity_rate": 65.0, "vert": 21, "orange": 7, "rouge": 4},
    {"date": "2026-02-01", "conformity_rate": 72.0, "vert": 23, "orange": 6, "rouge": 3},
    {"date": "2026-03-01", "conformity_rate": 78.1, "vert": 25, "orange": 5, "rouge": 2}
  ]
}
```

### GET /api/v1/scorecard/indicator/{num}

```json
// Response 200 — detail d'un indicateur
{
  "indicator": 14,
  "label": "Abandons geres et traces",
  "critere": 3,
  "status": "rouge",
  "kpi_target": "Taux < 15%",
  "kpi_current": 16.2,
  "details": {
    "total_inscrits": 127,
    "total_abandons": 21,
    "abandons_documentes": 18,
    "abandons_non_documentes": 3,
    "by_course": [
      {"course": "Certificat VTC", "taux": 6.7, "count": 3},
      {"course": "IA en entreprise", "taux": 23.0, "count": 7}
    ]
  },
  "actions_requises": [
    "Documenter la cause des 3 abandons non traces",
    "Plan de remediation pour la formation IA (taux 23%)"
  ],
  "preuves": [
    {"type": "registre_abandons", "url": "/api/v1/admin/abandons/"},
    {"type": "rapport_suivi", "document_id": 456}
  ]
}
```

---

## GROUPE 10 — API VEILLE REGLEMENTAIRE

**Auth** : JWT OpenEdX (role staff)

### GET /api/v1/veille/articles?category=reglementaire&page=1

```json
// Response 200
{
  "total": 45,
  "articles": [
    {
      "id": 101,
      "title": "Reforme du CPF : nouvelles conditions d'eligibilite",
      "source": "France Competences",
      "category": "reglementaire",
      "url": "https://www.francecompetences.fr/...",
      "summary": "A partir du 1er avril 2026...",
      "published_at": "2026-03-19",
      "status": "nouveau",
      "is_saved": false,
      "comments": []
    }
  ]
}
```

### PUT /api/v1/veille/articles/{id}/save

```json
// Response 200
{"status": "ok", "is_saved": true}
```

### POST /api/v1/veille/articles/{id}/comment

```json
// Request
{"comment": "Impact sur nos formations CPF — verifier les conditions avec Odoo"}

// Response 200
{
  "comment_id": 55,
  "comment": "Impact sur nos formations CPF...",
  "author": "admin",
  "created_at": "2026-03-20T15:00:00Z"
}
```

### GET /api/v1/veille/sources

```json
// Response 200
{
  "sources": [
    {"id": 1, "name": "France Competences", "url": "https://rss...", "category": "reglementaire", "is_active": true, "last_fetched": "2026-03-20T06:00:00Z"},
    {"id": 2, "name": "Legifrance", "url": "https://rss...", "category": "reglementaire", "is_active": true}
  ]
}
```

### POST /api/v1/veille/sources

```json
// Request — ajouter une source personnalisee
{
  "name": "Blog IA et Formation",
  "url": "https://example.com/feed.xml",
  "category": "pedagogique",
  "keywords": ["IA", "intelligence artificielle", "formation"]
}
```

---

## GROUPE 11 — API TEMPLATES EMAIL

**Auth** : JWT OpenEdX (role superuser)

### GET /api/v1/emails/templates

```json
// Response 200
{
  "templates": [
    {
      "id": 1,
      "slug": "welcome",
      "name": "Email de bienvenue",
      "subject": "Bienvenue chez Mission Formations — {{formation}}",
      "is_active": true,
      "last_modified": "2026-03-15T10:00:00Z",
      "attachments": ["DOC-04", "DOC-15", "DOC-01", "DOC-05"]
    }
  ]
}
```

### GET /api/v1/emails/templates/{slug}

```json
// Response 200 — detail avec contenu HTML
{
  "slug": "welcome",
  "subject": "Bienvenue chez Mission Formations — {{formation}}",
  "body_html": "<h1>Bienvenue {{prenom}},</h1><p>Vous etes inscrit(e) a la formation...</p>",
  "body_text": "Bienvenue {{prenom}}, Vous etes inscrit(e)...",
  "variables": ["prenom", "nom", "formation", "date_debut", "date_fin", "url_plateforme"],
  "attachments": ["DOC-04", "DOC-15", "DOC-01", "DOC-05"]
}
```

### PUT /api/v1/emails/templates/{slug}

```json
// Request — modifier le template
{
  "subject": "Bienvenue — Votre formation {{formation}} commence le {{date_debut}}",
  "body_html": "<h1>Bonjour {{prenom}},</h1>..."
}
```

### POST /api/v1/emails/templates/{slug}/preview

```json
// Request — previsualiser avec des donnees de test
{
  "test_data": {
    "prenom": "Jean",
    "nom": "Dupont",
    "formation": "Certificat VTC",
    "date_debut": "01/04/2026"
  }
}

// Response 200
{
  "subject_rendered": "Bienvenue — Votre formation Certificat VTC commence le 01/04/2026",
  "body_html_rendered": "<h1>Bonjour Jean,</h1>..."
}
```

### POST /api/v1/emails/send-test

```json
// Request — envoyer un email de test
{
  "template_slug": "welcome",
  "to_email": "admin@missionformations.com",
  "test_data": {"prenom": "Test", "formation": "Test Formation"}
}
```

---

## GROUPE 12 — API AUTOMATISATION

**Auth** : JWT OpenEdX (role superuser)

### GET /api/v1/automation/rules

```json
// Response 200
{
  "rules": [
    {
      "id": 1,
      "name": "Paiement → Inscription + Welcome",
      "event_type": "payment_received",
      "is_active": true,
      "actions": ["create_enrollment", "generate_welcome_docs", "send_welcome_email", "send_pre_assessment"],
      "executions_today": 3,
      "last_executed": "2026-03-20T14:30:00Z"
    }
  ]
}
```

### PUT /api/v1/automation/rules/{id}

```json
// Request — activer/desactiver une regle
{"is_active": false}
```

### GET /api/v1/automation/logs?event_type=payment_received&page=1

```json
// Response 200
{
  "total": 156,
  "logs": [
    {
      "id": 500,
      "rule_name": "Paiement → Inscription + Welcome",
      "event_type": "payment_received",
      "event_data": {"user_email": "jean@example.com", "course_id": "..."},
      "actions_executed": [
        {"action": "create_enrollment", "status": "success", "duration_ms": 450},
        {"action": "generate_welcome_docs", "status": "success", "duration_ms": 3200},
        {"action": "send_welcome_email", "status": "success", "duration_ms": 800}
      ],
      "status": "success",
      "created_at": "2026-03-20T14:30:00Z"
    }
  ]
}
```

### GET /api/v1/automation/scheduled?status=pending

```json
// Response 200
{
  "total": 23,
  "tasks": [
    {
      "id": 100,
      "task_type": "relance_satisfaction_chaud",
      "user_email": "jean@example.com",
      "course_name": "Certificat VTC",
      "scheduled_at": "2026-03-23T09:00:00Z",
      "attempt_count": 0,
      "max_attempts": 3,
      "status": "pending"
    }
  ]
}
```

### DELETE /api/v1/automation/scheduled/{id}

```json
// Response 200
{"status": "ok", "cancelled": true}
```

---

## GROUPE 13 — API EXPORTS

**Auth** : JWT OpenEdX (role staff)

### POST /api/v1/export/apprenants

```json
// Request
{
  "format": "csv",
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "fields": ["nom", "email", "progression", "grade", "assiduite", "statut"]
}

// Response 200
// Content-Type: text/csv
// Content-Disposition: attachment; filename="apprenants_VTC_2026-03-20.csv"
```

### POST /api/v1/export/satisfaction

```json
// Request
{
  "format": "csv",
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "type": "chaud"
}
```

### POST /api/v1/export/emargement

```json
// Request
{
  "format": "csv",
  "course_id": "course-v1:MF-VTC+VTC001+2026",
  "period_start": "2026-03-01",
  "period_end": "2026-03-31"
}
```

### POST /api/v1/export/scorecard

```json
// Request
{
  "format": "pdf",
  "date": "2026-03-20"
}
```

### POST /api/v1/export/fec

**Usage** : Fichier des Ecritures Comptables (expert comptable)

```json
// Request
{
  "format": "csv",
  "period_start": "2026-01-01",
  "period_end": "2026-03-31"
}
// Source : API Odoo → reformate en FEC
```

---

## GROUPE 14 — API CONFIGURATION

**Auth** : JWT OpenEdX (role superuser)

### GET /api/v1/config/qualiopi

```json
// Response 200
{
  "organisme": {
    "nom": "Mission Formations",
    "siret": "XXXXXXXXX",
    "numero_da": "XXXXXXXXXXX",
    "adresse": "...",
    "telephone": "...",
    "email_contact": "contact@missionformations.com",
    "site_web": "https://www.missionformations.com"
  },
  "referent_handicap": {
    "nom": "...",
    "email": "...",
    "telephone": "..."
  },
  "dpo": {
    "nom": "...",
    "email": "..."
  },
  "responsable_pedagogique": {
    "nom": "...",
    "email": "..."
  },
  "responsable_qualite": {
    "nom": "...",
    "email": "..."
  },
  "delai_acces_affiche": "15 jours",
  "politique_rgpd_url": "https://...",
  "cgv_url": "https://...",
  "mention_tva": "Exonere de TVA au titre de la formation professionnelle continue"
}
```

### PUT /api/v1/config/qualiopi

```json
// Request — modifier la config
{
  "referent_handicap": {
    "nom": "Marie Martin",
    "email": "marie@missionformations.com"
  }
}
```

### GET /api/v1/config/webhooks

```json
// Response 200
{
  "webhooks": [
    {
      "id": 1,
      "name": "Odoo → Qualiopi",
      "source": "odoo",
      "endpoint": "/api/v1/webhooks/odoo/",
      "secret_configured": true,
      "is_active": true,
      "last_received": "2026-03-20T14:30:00Z",
      "error_count_24h": 0
    },
    {
      "id": 2,
      "name": "OpenEdX → Qualiopi",
      "source": "openedx",
      "endpoint": "/api/v1/webhooks/openedx/",
      "secret_configured": true,
      "is_active": true,
      "last_received": "2026-03-20T14:28:00Z",
      "error_count_24h": 0
    },
    {
      "id": 3,
      "name": "WeWill → Qualiopi",
      "source": "chat",
      "endpoint": "/api/v1/webhooks/chat/",
      "secret_configured": true,
      "is_active": true,
      "last_received": "2026-03-20T13:15:00Z",
      "error_count_24h": 0
    }
  ]
}
```

### GET /api/v1/config/health

**Usage** : Diagnostic de tous les services connectes

```json
// Response 200
{
  "qualiopi_app": "ok",
  "postgresql": "ok",
  "redis": "ok",
  "celery_workers": {"active": 2, "queued": 3},
  "celery_beat": "ok",
  "openedx_mysql_readonly": "ok",
  "odoo_api": "ok",
  "chatwoot_api": "ok",
  "s3_storage": "ok",
  "smtp": "ok",
  "last_scorecard": "2026-03-20T07:30:00Z",
  "last_watch_scrape": "2026-03-20T06:00:00Z",
  "uptime_seconds": 345600
}
```

---

## RESUME TOTAL

| Groupe | Endpoints | Auth | Client principal |
|--------|-----------|------|-----------------|
| 1. Webhooks OpenEdX | 6 | Secret interne | Plugin LMS |
| 2. Webhooks Odoo | 5 | HMAC-SHA256 | Odoo.sh |
| 3. Webhooks Chat | 2 | Token API | WeWill |
| 4. Data (dashboard) | 6 | JWT OpenEdX | Dashboard admin LMS |
| 5. Documents (PDF) | 5 | JWT OpenEdX | Dashboard admin/formateur |
| 6. Formulaires | 8 | JWT OpenEdX | Dashboard apprenant |
| 7. Admin CRUD | ~30 | JWT OpenEdX | Dashboard admin |
| 8. Notifications | 3 | JWT OpenEdX | Dashboard admin |
| 9. Scorecard | 3 | JWT OpenEdX | Dashboard admin |
| 10. Veille | 5 | JWT OpenEdX | Dashboard admin |
| 11. Email templates | 5 | JWT OpenEdX | Super admin |
| 12. Automatisation | 4 | JWT OpenEdX | Super admin |
| 13. Exports | 5 | JWT OpenEdX | Dashboard admin |
| 14. Configuration | 4 | JWT OpenEdX | Super admin |
| **TOTAL** | **~91 endpoints** | | |

### Codes de retour HTTP

| Code | Usage |
|------|-------|
| 200 | Succes (GET, PUT) |
| 201 | Cree (POST) |
| 202 | Accepte (generation async) |
| 400 | Requete invalide (champs manquants) |
| 401 | Non authentifie |
| 403 | Non autorise (role insuffisant) |
| 404 | Ressource non trouvee |
| 429 | Rate limit depasse |
| 500 | Erreur serveur |

### Pagination standard

```json
{
  "total": 156,
  "page": 1,
  "per_page": 20,
  "pages": 8,
  "next": "/api/v1/...?page=2",
  "previous": null,
  "results": [...]
}
```

### Filtres standard

```
?status=en_cours              Filtrer par statut
?course_id=course-v1:...     Filtrer par formation
?user_id=42                   Filtrer par apprenant
?from=2026-01-01&to=2026-03-31  Periode
?search=dupont                Recherche texte
?ordering=-created_at         Tri (- = descendant)
?page=2&per_page=50           Pagination
```
