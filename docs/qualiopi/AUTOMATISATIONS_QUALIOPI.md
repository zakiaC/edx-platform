# Automatisations Qualiopi — Specifications completes

> Version 1.0 — 20 mars 2026
> Objectif : repliquer et depasser les automatisations de Teetche
> Tous les declencheurs, actions, relances et alertes

---

## ARCHITECTURE DES AUTOMATISATIONS

```
                    SOURCES D'EVENEMENTS
                    ════════════════════

  OpenEdX (Signaux Django)          Odoo (Webhooks)          Celery Beat (Cron)
  ┌────────────────────┐           ┌──────────────┐         ┌──────────────┐
  │ COURSE_ENROLLMENT  │           │ order.confirm│         │ Quotidien    │
  │ CERTIFICATE_CREATED│           │ payment.recv │         │ Hebdomadaire │
  │ COURSE_GRADE_CHANGE│           │ convention.  │         │ Mensuel      │
  │ SESSION_LOGIN      │           │   signed     │         │ Trimestriel  │
  │ course_published   │           └──────┬───────┘         └──────┬───────┘
  └────────┬───────────┘                  │                        │
           │                              │                        │
           ▼                              ▼                        ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                     APP QUALIOPI — MOTEUR D'AUTOMATISATION             │
  │                                                                        │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
  │  │ Signal Router│  │ Webhook      │  │ Scheduler    │                 │
  │  │ (receivers)  │  │ Handler      │  │ (Celery Beat)│                 │
  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
  │         │                 │                  │                         │
  │         ▼                 ▼                  ▼                         │
  │  ┌─────────────────────────────────────────────────┐                  │
  │  │            AUTOMATION ENGINE                     │                  │
  │  │                                                  │                  │
  │  │  1. Evaluer les regles (AutomationRule)          │                  │
  │  │  2. Executer les actions (Celery tasks)          │                  │
  │  │  3. Logger (AutomationLog)                       │                  │
  │  │  4. Notifier (email, dashboard, webhook)         │                  │
  │  └─────────────────────────────────────────────────┘                  │
  │         │              │              │                               │
  │         ▼              ▼              ▼                               │
  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐                        │
  │  │ PDF Gen  │  │ Emails   │  │ Webhooks out │                        │
  │  │ (Celery) │  │ (SMTP)   │  │ (Odoo, etc.) │                        │
  │  └──────────┘  └──────────┘  └──────────────┘                        │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## SIGNAUX OPENEDX UTILISES

### Signaux a ecouter depuis l'app Qualiopi

| Signal | Module OpenEdX | Donnees | Usage |
|--------|---------------|---------|-------|
| `COURSE_ENROLLMENT_CREATED` | `openedx_events.learning.signals` | user, course_key, mode | Declenchement parcours inscription |
| `CERTIFICATE_CREATED` | `openedx_events.learning.signals` | user, course_key, mode, status | Fin de formation → attestation |
| `COURSE_CERT_AWARDED` | `openedx.core.djangoapps.signals.signals` | user, course_key, mode, status | Certificat delivre |
| `COURSE_GRADE_NOW_PASSED` | `openedx.core.djangoapps.signals.signals` | user, course_id | Apprenant a reussi → evaluer |
| `COURSE_GRADE_CHANGED` | `openedx.core.djangoapps.signals.signals` | user, course_grade, course_key | Suivi progression |
| `COURSE_GRADE_NOW_FAILED` | `openedx.core.djangoapps.signals.signals` | user, course_id, grade | Detection difficulte |
| `SESSION_LOGIN_COMPLETED` | `openedx_events.learning.signals` | user (username, email) | Tracking assiduite / emargement |
| `STUDENT_REGISTRATION_COMPLETED` | `openedx_events.learning.signals` | user | Nouveau compte cree |
| `UNENROLL_DONE` | `common.djangoapps.student.signals.signals` | course_enrollment, skip_refund | Detection abandon |
| `course_published` | `xmodule.modulestore.django.SignalHandler` | course_key | Cours publie → programme PDF |
| `COURSE_START_DATE_CHANGED` | `openedx.core.djangoapps.content.course_overviews.signals` | course_overview, previous_date | MAJ planning |
| `SUBSECTION_SCORE_CHANGED` | `lms.djangoapps.grades.signals.signals` | course, user, subsection_grade | Suivi quiz/evaluations |
| `ENROLL_STATUS_CHANGE` | `common.djangoapps.student.signals.signals` | event, user, course_id, mode | Changement statut inscription |

### Comment l'app Qualiopi ecoute ces signaux

L'app Qualiopi ne tourne PAS dans le process LMS. Elle ecoute via deux mecanismes :

**Mecanisme 1 — Listener dans le LMS (plugin leger)**

Un mini-plugin reste dans `mission_central_admin` (LMS) et forward les signaux
vers l'app Qualiopi via webhook interne :

```python
# mission_central_admin/signal_forwarder.py (dans le LMS)
from openedx_events.learning.signals import CERTIFICATE_CREATED
from django.dispatch import receiver
import requests

QUALIOPI_WEBHOOK_URL = "http://qualiopi:8000/api/v1/webhooks/openedx/"

@receiver(CERTIFICATE_CREATED)
def forward_certificate_created(sender, signal, **kwargs):
    """Forward le signal vers l'app Qualiopi via webhook interne"""
    requests.post(
        f"{QUALIOPI_WEBHOOK_URL}certificate-created",
        json={
            "user_id": kwargs.get("certificate").user.id,
            "course_id": str(kwargs.get("certificate").course.course_key),
            "status": kwargs.get("certificate").status,
        },
        headers={"X-Internal-Secret": settings.QUALIOPI_INTERNAL_SECRET},
        timeout=5
    )
```

**Mecanisme 2 — Polling MySQL read-only (pour les donnees historiques)**

Pour les donnees qui ne passent pas par des signaux (tracking logs, dernieres connexions),
l'app Qualiopi interroge directement MySQL en lecture :

```python
# qualiopi/services/openedx_reader.py
from django.db import connections

def get_last_activity(user_id, course_id):
    with connections['openedx_readonly'].cursor() as cursor:
        cursor.execute("""
            SELECT MAX(modified) FROM courseware_studentmodule
            WHERE student_id = %s AND course_id = %s
        """, [user_id, course_id])
        return cursor.fetchone()[0]
```

---

## WORKFLOWS AUTOMATISES COMPLETS

### WORKFLOW 1 : Cours publie dans Studio

**Declencheur** : Signal `course_published` (forwarde par le plugin LMS)

```
Cours publie dans Studio
  │
  ├─► [CELERY TASK] generate_program_pdf
  │     → Lire la structure OLX du cours (chapters, sequentials, verticals)
  │     → Generer DOC-01 (programme de formation PDF)
  │     → Stocker sur S3
  │     → Creer/MAJ DocumentQualiopi(type="DOC-01", course_id=...)
  │
  ├─► [CELERY TASK] sync_odoo_product
  │     → Appeler API Odoo : creer/MAJ le produit
  │     → Sync : titre, description, duree, prix, course_id
  │
  ├─► [CELERY TASK] update_catalog_page
  │     → Invalider le cache de la page /catalogue/
  │     → MAJ les metadonnees Meilisearch
  │
  ├─► [CELERY TASK] check_qualiopi_completeness
  │     → Verifier : description presente ? prerequis ? objectifs ? tarif ?
  │     → Si incomplet → alerte admin "Formation X publiee mais informations manquantes"
  │     → MAJ scorecard indicateur 1
  │
  └─► [LOG] AutomationLog(event="course_published", course_id=..., actions=[...])
```

---

### WORKFLOW 2 : Paiement confirme (webhook Odoo)

**Declencheur** : `POST /api/v1/webhooks/odoo/payment-received`

```
Paiement confirme dans Odoo
  │
  ├─► [VALIDATION]
  │     → Verifier signature HMAC
  │     → Verifier que le course_id existe
  │     → Verifier que l'utilisateur existe (sinon le creer)
  │
  ├─► [CELERY TASK] create_enrollment
  │     → Appeler API OpenEdX : inscrire l'apprenant au cours
  │     → Si B2B : verifier/creer l'Academy + AcademyEnrollment
  │     → Creer RecueilBesoin(apprenant=..., statut="a_remplir")
  │     → Creer Convention(statut="a_signer") si B2B
  │
  ├─► [CELERY TASK] generate_welcome_documents
  │     → Generer DOC-04 (convocation) avec dates, lieu/URL, identifiants
  │     → Generer DOC-15 (livret d'accueil) personnalise
  │     → Recuperer DOC-01 (programme) deja genere
  │     → Recuperer DOC-05 (reglement interieur) statique
  │     → Stocker tous les PDFs sur S3
  │
  ├─► [CELERY TASK] send_welcome_email
  │     → Email template "bienvenue" avec :
  │       - Pieces jointes : convocation, livret, programme, reglement
  │       - Lien vers le questionnaire de besoins
  │       - Lien vers l'evaluation pre-formation
  │       - Identifiants de connexion plateforme
  │       - Dates de la formation
  │       - Contact support
  │
  ├─► [CELERY TASK] send_pre_assessment
  │     → Creer EvaluationPrePost(type="pre", statut="envoyee")
  │     → Email avec lien vers le formulaire d'eval pre-formation
  │
  ├─► [SCHEDULE] schedule_reminders
  │     → Planifier relance J+3 si questionnaire besoins non rempli
  │     → Planifier relance J+3 si eval pre-formation non remplie
  │     → Planifier relance J+7 si convention non signee (B2B)
  │
  ├─► [WEBHOOK] notify_odoo_enrollment_done
  │     → Callback Odoo : confirmer que l'inscription est faite
  │     → MAJ fiche contact Odoo (statut = "inscrit")
  │
  └─► [LOG] AutomationLog(event="payment_received", user=..., course=..., actions=[...])
```

---

### WORKFLOW 3 : Convention signee (webhook Odoo)

**Declencheur** : `POST /api/v1/webhooks/odoo/convention-signed`

```
Convention signee dans Odoo (signature electronique)
  │
  ├─► [CELERY TASK] archive_convention
  │     → Telecharger le PDF signe depuis Odoo
  │     → Stocker sur S3
  │     → MAJ Convention(statut="signee", pdf_url=..., date_signature=...)
  │     → Creer DocumentQualiopi(type="DOC-02" ou "DOC-03")
  │
  ├─► [CELERY TASK] update_qualiopi_scorecard
  │     → MAJ indicateurs 7 et 8 pour cet apprenant
  │
  └─► [LOG] AutomationLog(event="convention_signed", ...)
```

---

### WORKFLOW 4 : Apprenant se connecte (tracking assiduite)

**Declencheur** : Signal `SESSION_LOGIN_COMPLETED` (forwarde) + Celery beat quotidien

```
Connexion de l'apprenant
  │
  ├─► [CELERY TASK] log_attendance
  │     → Enregistrer dans Emargement : user, date, heure_debut
  │     → Calculer la duree de la session precedente (heure_fin = maintenant si reconnexion)
  │
  Celery beat quotidien (minuit) :
  │
  ├─► [CELERY TASK] calculate_daily_attendance
  │     → Pour chaque apprenant actif :
  │       - Agreger les logs de connexion du jour
  │       - Calculer le temps total passe
  │       - MAJ Emargement(donnees_json)
  │       - Calculer le taux d'assiduite cumule
  │
  ├─► [CELERY TASK] detect_inactivity
  │     → Pour chaque apprenant inscrit a un cours en cours :
  │       - Derniere connexion > 15 jours ?
  │         → Notification admin "Apprenant X inactif depuis 15 jours"
  │         → Email relance apprenant "Nous avons remarque votre absence..."
  │       - Derniere connexion > 30 jours ?
  │         → Creer AbandonLog(statut="detecte", cause="inactivite")
  │         → Alerte urgente admin "Risque d'abandon — X"
  │         → MAJ scorecard indicateur 14
  │         → Webhook Odoo : MAJ fiche contact (risque perte)
  │
  └─► [LOG] AutomationLog(event="daily_attendance_check", ...)
```

---

### WORKFLOW 5 : Apprenant termine le cours / certificat delivre

**Declencheur** : Signal `CERTIFICATE_CREATED` ou `COURSE_CERT_AWARDED` (forwarde)

```
Certificat delivre
  │
  ├─► [CELERY TASK] generate_completion_documents
  │     → Generer DOC-07 (attestation de fin de formation)
  │     → Generer DOC-08 (certificat de realisation)
  │     → Generer DOC-16 (attestation d'assiduite)
  │     → Generer DOC-06 (feuille d'emargement finale)
  │     → Stocker tous les PDFs sur S3
  │
  ├─► [CELERY TASK] send_completion_email
  │     → Email template "Felicitations" avec :
  │       - Attestation en PJ
  │       - Certificat en PJ
  │       - Lien de telechargement
  │
  ├─► [CELERY TASK] send_post_assessment
  │     → Creer EvaluationPrePost(type="post", statut="envoyee")
  │     → Email avec lien vers le formulaire d'eval post-formation
  │     → Planifier relance J+3 si non remplie
  │
  ├─► [CELERY TASK] send_satisfaction_survey
  │     → Creer EnqueteSatisfaction(type="chaud", statut="envoyee")
  │     → Email avec lien vers le formulaire de satisfaction a chaud
  │     → Planifier relance J+3 si non remplie
  │     → Planifier relance J+7 si toujours non remplie
  │
  ├─► [SCHEDULE] schedule_followup
  │     → Planifier enquete satisfaction a froid a J+90
  │     → Planifier enquete insertion a J+180
  │
  ├─► [WEBHOOK] notify_odoo_completion
  │     → MAJ fiche contact Odoo (statut = "formation terminee", note = grade)
  │
  ├─► [CELERY TASK] update_qualiopi_scorecard
  │     → Recalculer : taux de completion, taux de reussite, indicateurs 3, 11
  │
  └─► [LOG] AutomationLog(event="certificate_created", ...)
```

---

### WORKFLOW 6 : Relances automatiques

**Declencheur** : Celery beat (toutes les heures)

```
Celery beat (toutes les heures) :
  │
  ├─► [CELERY TASK] process_scheduled_reminders
  │     → Pour chaque ScheduledTask en attente dont la date est passee :
  │
  │     TYPE "relance_questionnaire_besoins" (J+3) :
  │       → Si RecueilBesoin.statut == "a_remplir"
  │         → Email relance "N'oubliez pas de remplir votre questionnaire..."
  │         → Planifier 2eme relance J+7
  │       → Si deja rempli → annuler la tache
  │
  │     TYPE "relance_eval_pre" (J+3) :
  │       → Si EvaluationPrePost(type="pre").statut == "envoyee"
  │         → Email relance
  │         → Planifier 2eme relance J+7
  │
  │     TYPE "relance_convention" (J+7) :
  │       → Si Convention.statut != "signee"
  │         → Email relance au signataire
  │         → Alerte admin "Convention X toujours non signee"
  │
  │     TYPE "relance_satisfaction_chaud" (J+3, puis J+7) :
  │       → Si EnqueteSatisfaction(type="chaud").statut == "envoyee"
  │         → Email relance
  │       → Si J+7 et toujours pas repondu
  │         → Derniere relance + notification admin
  │
  │     TYPE "enquete_froid" (J+90 apres fin de formation) :
  │       → Creer EnqueteSatisfaction(type="froid", statut="envoyee")
  │       → Email avec lien vers le formulaire
  │       → Planifier relance J+93, J+100
  │
  │     TYPE "enquete_insertion" (J+180 apres fin de formation) :
  │       → Creer EnqueteInsertion(statut="envoyee")
  │       → Email avec lien vers le formulaire
  │       → Planifier relance J+183, J+190
  │
  │     TYPE "relance_eval_post" (J+3) :
  │       → Si EvaluationPrePost(type="post").statut == "envoyee"
  │         → Email relance
  │
  └─► [LOG] AutomationLog(event="reminders_processed", count=N)
```

---

### WORKFLOW 7 : Veille reglementaire automatique

**Declencheur** : Celery beat quotidien (6h du matin)

```
Celery beat quotidien (6h00) :
  │
  ├─► [CELERY TASK] scrape_regulatory_watch
  │     → Pour chaque RSSSource active :
  │       - Telecharger le flux RSS
  │       - Parser les nouveaux articles (depuis last_fetched)
  │       - Filtrer par mots-cles (formation professionnelle, Qualiopi,
  │         OPCO, CPF, certification, France Competences, etc.)
  │       - Pour chaque article pertinent :
  │         → Creer VeilleEntry(
  │             type=source.categorie,  # reglementaire/pedagogique/emploi/prospective
  │             source=source.nom,
  │             titre=article.titre,
  │             url=article.url,
  │             resume=article.description[:500],
  │             date=article.pub_date,
  │             statut="nouveau"
  │           )
  │       - MAJ RSSSource.last_fetched = now()
  │
  ├─► [CELERY TASK] notify_new_watch_entries
  │     → Compter les nouveaux articles du jour
  │     → Si > 0 : email admin "X nouveaux articles de veille aujourd'hui"
  │     → Lien vers le dashboard veille
  │
  ├─► [CELERY TASK] check_watch_compliance
  │     → Derniere entree de veille reglementaire > 80 jours ?
  │       → Alerte rouge admin "Aucune veille reglementaire depuis X jours"
  │       → MAJ scorecard indicateur 24 = ROUGE
  │     → Derniere entree de veille sectorielle par domaine > 6 mois ?
  │       → Alerte orange admin
  │       → MAJ scorecard indicateur 25 = ORANGE
  │     → Derniere entree de veille pedagogique > 12 mois ?
  │       → Alerte rouge admin
  │       → MAJ scorecard indicateur 26 = ROUGE
  │
  └─► [LOG] AutomationLog(event="regulatory_watch", new_entries=N)

Sources RSS par defaut :
  │
  ├── Reglementaire :
  │   ├── Legifrance (formation professionnelle)
  │   ├── France Competences (actualites)
  │   ├── Ministere du Travail (formation)
  │   └── DGEFP (emploi et formation)
  │
  ├── Pedagogique :
  │   ├── Thot Cursus (innovation pedagogique)
  │   ├── FFFOD (formation a distance)
  │   └── Centre Inffo (actualites formation)
  │
  ├── Emploi/Marche :
  │   ├── DARES (statistiques emploi)
  │   ├── Pole Emploi (marche du travail)
  │   └── OPCO specifiques (selon domaines MF)
  │
  └── Prospective :
      ├── EdTech France
      └── Digital Learning (tendances)
```

---

### WORKFLOW 8 : Alertes qualite automatiques

**Declencheur** : Celery beat quotidien (7h du matin, apres la veille)

```
Celery beat quotidien (7h00) :
  │
  ├─► [CELERY TASK] check_reclamation_sla
  │     → Pour chaque Reclamation(statut="en_cours") :
  │       - Calculer delai = now() - date_reception
  │       - Si delai > 20 jours → Notification.create("Reclamation #X : J+20, 10 jours restants")
  │       - Si delai > 25 jours → Notification.create(urgence="haute", "Reclamation #X : J+25, URGENT")
  │       - Si delai > 30 jours → Notification.create(urgence="critique", "Reclamation #X : NON CONFORME")
  │         → MAJ scorecard indicateur 32 = ROUGE
  │         → Email admin + responsable qualite
  │
  ├─► [CELERY TASK] check_formateur_compliance
  │     → Pour chaque FicheFormateur :
  │       - CV date_maj > 18 mois ?
  │         → Alerte "CV de X expire dans 6 mois"
  │       - CV date_maj > 24 mois ?
  │         → Alerte rouge "CV de X expire"
  │         → MAJ scorecard indicateur 20 = ROUGE
  │       - Aucune ActionFormationFormateur dans l'annee en cours ?
  │         → Alerte "Formateur X : aucune formation continue cette annee"
  │         → MAJ scorecard indicateur 22 = ORANGE
  │       - Sous-traitant sans contrat signe ?
  │         → Alerte rouge
  │         → MAJ scorecard indicateur 19, 21 = ROUGE
  │
  ├─► [CELERY TASK] check_reunion_pedagogique
  │     → Derniere ReunionPedagogique > 5 mois ?
  │       → Alerte "Planifier une reunion pedagogique (min 2/an)"
  │     → Moins de 2 reunions dans l'annee en cours et on est apres le 30 juin ?
  │       → Alerte rouge "Objectif 2 reunions/an en danger"
  │       → MAJ scorecard indicateur 23 = ORANGE
  │
  ├─► [CELERY TASK] check_satisfaction_rates
  │     → Calculer taux de retour enquetes satisfaction a chaud
  │       - Si < 80% → alerte "Taux de retour satisfaction : X% (objectif 80%)"
  │       → MAJ scorecard indicateur 12
  │     → Calculer taux de retour enquetes a froid
  │       - Si < 50% → alerte
  │       → MAJ scorecard indicateur 13
  │     → Calculer satisfaction moyenne globale
  │       - Si < 3.5/5 → alerte rouge
  │       → MAJ scorecard indicateur 31
  │     → Calculer NPS global
  │       - Si NPS < 20 → alerte
  │
  ├─► [CELERY TASK] check_abandon_rate
  │     → Calculer taux d'abandon global et par formation
  │       - Si > 10% → alerte orange
  │       - Si > 15% → alerte rouge (non conforme Qualiopi)
  │       → MAJ scorecard indicateur 14
  │
  ├─► [CELERY TASK] check_content_freshness
  │     → Pour chaque cours actif dans OpenEdX :
  │       - Derniere modification > 18 mois ? → alerte orange
  │       - Derniere modification > 24 mois ? → alerte rouge
  │       → MAJ scorecard indicateur 15
  │
  ├─► [CELERY TASK] check_encadrement_ratio
  │     → Pour chaque cours actif :
  │       - Nb inscrits / nb formateurs
  │       - Si ratio > 15 (presentiel) ou > 20 (distanciel) → alerte
  │       → MAJ scorecard indicateur 17
  │
  ├─► [CELERY TASK] check_annual_documents
  │     → PlanAmelioration de l'annee en cours existe ? → sinon alerte
  │     → RevueDirection de l'annee en cours existe ? → sinon alerte (apres le 30 sept)
  │     → MAJ scorecard indicateur 30
  │
  ├─► [CELERY TASK] check_partenariats
  │     → Au moins 1 Partenariat avec convention signee ? → sinon alerte
  │     → MAJ scorecard indicateur 27
  │
  ├─► [CELERY TASK] check_rgpd_compliance
  │     → QualiopiConfig.dpo_name rempli ? → sinon alerte rouge
  │     → QualiopiConfig.politique_rgpd_url remplie ? → sinon alerte rouge
  │     → MAJ scorecard indicateur 16
  │
  ├─► [CELERY TASK] check_handicap_referent
  │     → QualiopiConfig.referent_handicap rempli ? → sinon alerte rouge
  │     → MAJ scorecard indicateur 4
  │
  ├─► [CELERY TASK] generate_daily_scorecard
  │     → Recalculer les 32 indicateurs
  │     → Stocker le snapshot dans QualiopiScorecard(date=today, scores_json={...})
  │     → Si un indicateur passe de VERT a ROUGE → email admin immediat
  │
  └─► [LOG] AutomationLog(event="daily_quality_check", alerts=N, scorecard={...})
```

---

### WORKFLOW 9 : Fin de session / bilan formation

**Declencheur** : Celery beat quotidien — detecte les sessions terminees

```
Celery beat quotidien :
  │
  ├─► [CELERY TASK] detect_ended_sessions
  │     → Pour chaque cours dont la date de fin = hier :
  │
  │     ├─► [CELERY TASK] generate_session_report
  │     │     → Generer DOC-13 (rapport de suivi pedagogique) avec stats finales
  │     │     → Generer DOC-06 (feuille d'emargement complete)
  │     │     → Pour chaque apprenant :
  │     │       → Generer DOC-07 si pas encore fait (attestation)
  │     │       → Generer DOC-08 si pas encore fait (certificat realisation)
  │     │       → Generer DOC-16 (attestation assiduite)
  │     │
  │     ├─► [CELERY TASK] generate_satisfaction_synthesis
  │     │     → Agreger toutes les EnqueteSatisfaction de cette session
  │     │     → Generer la synthese PDF (moyennes, NPS, graphiques)
  │     │
  │     ├─► [CELERY TASK] generate_training_report (DOC-14 ZIP)
  │     │     → Assembler le ZIP complet :
  │     │       - DOC-01 (programme)
  │     │       - DOC-02/03 (conventions/contrats)
  │     │       - DOC-06 (emargement)
  │     │       - DOC-07 × N (attestations)
  │     │       - DOC-08 × N (certificats realisation)
  │     │       - DOC-09 × N (evals pre)
  │     │       - DOC-10 × N (evals post)
  │     │       - DOC-11 synthese (satisfaction)
  │     │       - DOC-13 (rapport suivi)
  │     │       - DOC-16 × N (assiduite)
  │     │       - Liste des stagiaires (CSV)
  │     │       - Bilan financier (depuis Odoo)
  │     │     → Stocker le ZIP sur S3
  │     │     → Creer DocumentQualiopi(type="DOC-14")
  │     │
  │     ├─► [CELERY TASK] notify_financeur
  │     │     → Si formation financee par OPCO :
  │     │       → Creer BilanFinanceur(statut="a_envoyer")
  │     │       → Notification admin "Bilan a envoyer a [OPCO] pour la formation X"
  │     │       → MAJ scorecard indicateur 29
  │     │
  │     └─► [SCHEDULE] schedule_cold_surveys
  │           → Pour chaque apprenant de la session :
  │             → Planifier enquete satisfaction a froid a J+90
  │             → Planifier enquete insertion a J+180
  │
  └─► [LOG] AutomationLog(event="session_ended", course=..., documents=N)
```

---

### WORKFLOW 10 : Enquete remplie (formulaire soumis)

**Declencheur** : POST depuis le formulaire apprenant (dashboard ou email)

```
Apprenant soumet un formulaire
  │
  ├─► TYPE "recueil_besoins" :
  │     → MAJ RecueilBesoin(statut="rempli", reponses_json=...)
  │     → Annuler les relances planifiees
  │     → MAJ scorecard indicateur 5
  │     → Notification formateur "Besoins de X : [resume]"
  │
  ├─► TYPE "eval_pre" :
  │     → MAJ EvaluationPrePost(type="pre", statut="remplie", score=...)
  │     → Annuler les relances
  │     → MAJ scorecard indicateur 6
  │     → Notification formateur "Positionnement de X : score Y/10"
  │
  ├─► TYPE "eval_post" :
  │     → MAJ EvaluationPrePost(type="post", statut="remplie", score=...)
  │     → Annuler les relances
  │     → Calculer la progression (score post - score pre)
  │     → Generer le comparatif pre/post (graphique radar)
  │     → MAJ scorecard indicateur 11
  │
  ├─► TYPE "satisfaction_chaud" :
  │     → MAJ EnqueteSatisfaction(type="chaud", statut="remplie", ...)
  │     → Annuler les relances
  │     → Recalculer le taux de retour pour cette formation
  │     → Si taux de retour >= 80% → generer synthese PDF auto
  │     → MAJ scorecard indicateurs 12, 31
  │     → Si NPS < 6 → alerte admin "Detracteur detecte"
  │
  ├─► TYPE "satisfaction_froid" :
  │     → MAJ EnqueteSatisfaction(type="froid", statut="remplie", ...)
  │     → Annuler les relances
  │     → MAJ scorecard indicateur 13
  │
  ├─► TYPE "insertion" :
  │     → MAJ EnqueteInsertion(statut="remplie", situation_pro=...)
  │     → Annuler les relances
  │     → Recalculer le taux d'insertion
  │     → MAJ scorecard indicateur 28
  │
  └─► [LOG] AutomationLog(event="form_submitted", type=..., user=...)
```

---

### WORKFLOW 11 : Reclamation recue

**Declencheur** : Formulaire admin OU webhook Crisp/Chatwoot (tag "reclamation")

```
Reclamation recue
  │
  ├─► [IMMEDIATE] Creer Reclamation(
  │     numero=auto_increment,
  │     date_reception=now(),
  │     statut="en_cours",
  │     deadline=now()+30j
  │   )
  │
  ├─► [CELERY TASK] generate_receipt
  │     → Generer DOC-20 (recepisse de reclamation)
  │     → Email au reclamant avec le recepisse en PJ
  │     → Confirmer : "Votre reclamation #X a ete enregistree. Reponse sous 30 jours."
  │
  ├─► [IMMEDIATE] Notification admin
  │     → "Nouvelle reclamation #X de [nom] — objet : [objet]"
  │     → Assigner au responsable qualite
  │
  ├─► [SCHEDULE] Planifier alertes SLA
  │     → J+20 : alerte "10 jours restants"
  │     → J+25 : alerte urgente "5 jours restants"
  │     → J+29 : alerte critique "DERNIER JOUR"
  │
  └─► [LOG] AutomationLog(event="reclamation_created", numero=X)
```

---

### WORKFLOW 12 : Nouvelle conversation chat → lead Odoo

**Declencheur** : Webhook Chatwoot/WeWill

```
Nouvelle conversation dans WeWill
  │
  ├─► [CELERY TASK] create_odoo_lead
  │     → Extraire : nom, email, message initial
  │     → Appeler API Odoo CRM : creer lead
  │     → Tags : source="chat_wewill"
  │
  ├─► [CELERY TASK] identify_user
  │     → Si l'email correspond a un apprenant OpenEdX :
  │       → Enrichir le lead avec : formations en cours, progression
  │       → Taguer la conversation dans WeWill
  │
  └─► [LOG] AutomationLog(event="chat_lead_created", email=...)
```

---

## MODELES DJANGO POUR L'AUTOMATISATION

### Nouveaux modeles (en plus des 20 Qualiopi)

```python
# automation/models.py

class AutomationRule(models.Model):
    """Regle d'automatisation configurable"""
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=100, choices=[
        ('payment_received', 'Paiement recu'),
        ('certificate_created', 'Certificat delivre'),
        ('enrollment_created', 'Inscription creee'),
        ('course_published', 'Cours publie'),
        ('form_submitted', 'Formulaire soumis'),
        ('chat_conversation', 'Conversation chat'),
        ('scheduled', 'Tache planifiee'),
    ])
    actions_json = models.JSONField()  # liste des actions a executer
    is_active = models.BooleanField(default=True)
    conditions_json = models.JSONField(null=True)  # conditions optionnelles
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qualiopi_automation_rule'


class AutomationLog(models.Model):
    """Historique de chaque action automatique executee"""
    rule = models.ForeignKey(AutomationRule, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    actions_executed = models.JSONField()  # liste des actions et leur resultat
    status = models.CharField(max_length=20, choices=[
        ('success', 'Succes'),
        ('partial', 'Partiel'),
        ('failed', 'Echec'),
    ])
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True)  # temps d'execution

    class Meta:
        db_table = 'qualiopi_automation_log'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]


class EmailTemplate(models.Model):
    """Templates d'emails personnalisables"""
    slug = models.SlugField(unique=True)  # ex: "welcome", "relance_satisfaction"
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)  # supporte les variables {{prenom}}
    body_html = models.TextField()  # HTML avec variables Jinja2
    body_text = models.TextField()  # Version texte
    attachments_config = models.JSONField(null=True)  # PDFs a joindre auto
    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qualiopi_email_template'


class ScheduledTask(models.Model):
    """Taches planifiees (relances, enquetes differees)"""
    task_type = models.CharField(max_length=100, choices=[
        ('relance_besoins', 'Relance questionnaire besoins'),
        ('relance_eval_pre', 'Relance eval pre-formation'),
        ('relance_eval_post', 'Relance eval post-formation'),
        ('relance_satisfaction_chaud', 'Relance satisfaction a chaud'),
        ('relance_satisfaction_froid', 'Relance satisfaction a froid'),
        ('relance_convention', 'Relance signature convention'),
        ('enquete_froid', 'Envoi enquete satisfaction a froid'),
        ('enquete_insertion', 'Envoi enquete insertion'),
        ('relance_enquete_froid', 'Relance enquete a froid'),
        ('relance_enquete_insertion', 'Relance enquete insertion'),
    ])
    user_id = models.IntegerField()  # ID user OpenEdX
    course_id = models.CharField(max_length=255)
    scheduled_at = models.DateTimeField()  # quand executer
    executed_at = models.DateTimeField(null=True)  # quand executee (null = en attente)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'En attente'),
        ('executed', 'Executee'),
        ('cancelled', 'Annulee'),
        ('failed', 'Echouee'),
    ])
    related_model = models.CharField(max_length=100, null=True)  # ex: "RecueilBesoin"
    related_id = models.IntegerField(null=True)  # ex: ID du RecueilBesoin
    attempt_count = models.IntegerField(default=0)  # nb de relances deja envoyees
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qualiopi_scheduled_task'
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['task_type', 'user_id']),
        ]


class RSSSource(models.Model):
    """Sources de veille reglementaire (flux RSS)"""
    name = models.CharField(max_length=200)
    url = models.URLField()
    category = models.CharField(max_length=50, choices=[
        ('reglementaire', 'Reglementaire'),
        ('pedagogique', 'Pedagogique'),
        ('emploi_marche', 'Emploi / Marche'),
        ('prospective', 'Prospective'),
    ])
    keywords = models.JSONField(default=list)  # mots-cles pour filtrer
    is_active = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True)
    fetch_error_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qualiopi_rss_source'


class QualiopiScorecard(models.Model):
    """Snapshot quotidien des 32 indicateurs"""
    date = models.DateField(unique=True)
    scores_json = models.JSONField()  # {"ind_1": "vert", "ind_2": "orange", ...}
    total_vert = models.IntegerField()
    total_orange = models.IntegerField()
    total_rouge = models.IntegerField()
    conformity_rate = models.DecimalField(max_digits=5, decimal_places=2)  # % vert
    alerts_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qualiopi_scorecard'
        indexes = [
            models.Index(fields=['-date']),
        ]


class Notification(models.Model):
    """Notifications internes pour les admins"""
    title = models.CharField(max_length=300)
    message = models.TextField()
    urgency = models.CharField(max_length=20, choices=[
        ('info', 'Information'),
        ('warning', 'Attention'),
        ('high', 'Urgente'),
        ('critical', 'Critique'),
    ])
    category = models.CharField(max_length=50, choices=[
        ('reclamation', 'Reclamation'),
        ('abandon', 'Abandon'),
        ('formateur', 'Formateur'),
        ('satisfaction', 'Satisfaction'),
        ('veille', 'Veille'),
        ('document', 'Document'),
        ('conformite', 'Conformite'),
        ('system', 'Systeme'),
    ])
    related_indicator = models.IntegerField(null=True)  # ind. Qualiopi 1-32
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qualiopi_notification'
        indexes = [
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['urgency', '-created_at']),
        ]
```

---

## EMAILS TEMPLATES A CREER

| Slug | Sujet | Declencheur | PJ auto |
|------|-------|-------------|---------|
| `welcome` | Bienvenue chez Mission Formations — Votre formation {{formation}} | Paiement confirme | DOC-04, DOC-15, DOC-01, DOC-05 |
| `pre_assessment` | Evaluez votre niveau avant la formation | Paiement confirme | — |
| `relance_besoins` | N'oubliez pas votre questionnaire de besoins | J+3 si non rempli | — |
| `relance_eval_pre` | Completez votre evaluation de positionnement | J+3 si non rempli | — |
| `relance_convention` | Convention en attente de signature | J+7 si non signee | — |
| `inactivity_warning` | Nous avons remarque votre absence | 15 jours d'inactivite | — |
| `completion` | Felicitations ! Vous avez termine {{formation}} | Certificat delivre | DOC-07, DOC-08 |
| `post_assessment` | Evaluez vos acquis apres la formation | Certificat delivre | — |
| `satisfaction_chaud` | Donnez votre avis sur la formation {{formation}} | Certificat delivre | — |
| `relance_satisfaction` | Votre avis compte — dernier rappel | J+3 / J+7 si non rempli | — |
| `satisfaction_froid` | Comment allez-vous depuis votre formation ? | J+90 apres fin | — |
| `enquete_insertion` | Votre parcours professionnel depuis la formation | J+180 apres fin | — |
| `reclamation_receipt` | Reclamation #{{numero}} — Accuse de reception | Reclamation creee | DOC-20 |
| `reclamation_resolved` | Reclamation #{{numero}} — Reponse | Reclamation resolue | — |
| `veille_daily` | {{count}} nouveaux articles de veille | Quotidien si > 0 | — |
| `admin_alert` | [{{urgence}}] {{titre}} | Alerte qualite detectee | — |
| `session_ended` | Bilan de la session {{formation}} disponible | Fin de session | DOC-14 (ZIP) |

---

## CELERY BEAT SCHEDULE

```python
# qualiopi/celery_config.py

CELERY_BEAT_SCHEDULE = {
    # Toutes les heures
    'process-reminders': {
        'task': 'qualiopi.tasks.process_scheduled_reminders',
        'schedule': crontab(minute=0),  # chaque heure pile
    },

    # Quotidien 6h00 — Veille reglementaire
    'regulatory-watch': {
        'task': 'qualiopi.tasks.scrape_regulatory_watch',
        'schedule': crontab(hour=6, minute=0),
    },

    # Quotidien 7h00 — Alertes qualite
    'quality-alerts': {
        'task': 'qualiopi.tasks.daily_quality_check',
        'schedule': crontab(hour=7, minute=0),
    },

    # Quotidien minuit — Assiduite
    'daily-attendance': {
        'task': 'qualiopi.tasks.calculate_daily_attendance',
        'schedule': crontab(hour=0, minute=0),
    },

    # Quotidien 0h30 — Detection inactivite
    'inactivity-detection': {
        'task': 'qualiopi.tasks.detect_inactivity',
        'schedule': crontab(hour=0, minute=30),
    },

    # Quotidien 1h00 — Detection sessions terminees
    'session-end-detection': {
        'task': 'qualiopi.tasks.detect_ended_sessions',
        'schedule': crontab(hour=1, minute=0),
    },

    # Quotidien 7h30 — Scorecard
    'daily-scorecard': {
        'task': 'qualiopi.tasks.generate_daily_scorecard',
        'schedule': crontab(hour=7, minute=30),
    },

    # Hebdomadaire (lundi 8h) — Rapport hebdo admin
    'weekly-report': {
        'task': 'qualiopi.tasks.send_weekly_admin_report',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },

    # Mensuel (1er du mois, 2h) — Nettoyage logs
    'monthly-cleanup': {
        'task': 'qualiopi.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
    },
}
```

---

## TOTAL MODELES MIS A JOUR

| Groupe | Nombre |
|--------|--------|
| Qualiopi (registres, formulaires) | 20 |
| Automatisation (rules, logs, schedules, templates) | 7 |
| OpenEdX read-only (unmanaged) | 6 |
| API / infrastructure (webhooks, storage, audit) | 5 |
| Chat custom (si on le fait) | 5 |
| **TOTAL** | **~43 modeles** |

---

## IMPACT SUR LA ROADMAP

| Sprint | Ajout automatisation | Effort supplementaire |
|--------|---------------------|----------------------|
| **S1** | Modeles automatisation (7) + signal forwarder dans le LMS | +4h |
| **S2** | Workflows 1-5 (publication, paiement, convention, assiduite, completion) | +12h |
| **S2** | 17 email templates | +6h |
| **S2** | Celery beat schedule | +2h |
| **S2** | Workflows 6-8 (relances, veille RSS, alertes qualite) | +8h |
| **S4** | Workflows 9-12 (fin session, formulaires, reclamations, chat) | +6h |
| **TOTAL** | | **+38h** |

**Nouvelle estimation totale : ~265h (au lieu de 227h)**
