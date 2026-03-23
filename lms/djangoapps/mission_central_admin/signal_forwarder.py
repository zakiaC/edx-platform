"""
Signal Forwarder — Forward les signaux OpenEdX vers l'app Qualiopi.

Ce module tourne dans le process LMS (pas dans l'app Qualiopi).
Il ecoute les signaux Django et envoie des webhooks internes
vers l'app Qualiopi via HTTP POST.

Signaux ecoutes :
- CERTIFICATE_CREATED → attestation + certificat + satisfaction
- COURSE_ENROLLMENT_CREATED → recueil besoin + eval pre
- COURSE_GRADE_CHANGED → suivi progression
- SESSION_LOGIN_COMPLETED → tracking assiduite
"""
import logging
import json
import threading

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

QUALIOPI_BASE_URL = getattr(settings, 'QUALIOPI_WEBHOOK_URL', 'http://qualiopi-app:8080')
QUALIOPI_SECRET = getattr(settings, 'OPENEDX_INTERNAL_SECRET', '')
TIMEOUT = 5  # secondes


def _send_webhook(endpoint, data):
    """Envoie un webhook async vers l'app Qualiopi (non-bloquant)."""
    def _post():
        url = f"{QUALIOPI_BASE_URL}/qualiopi/api/v1/webhooks/openedx/{endpoint}/"
        try:
            resp = requests.post(
                url,
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Secret': QUALIOPI_SECRET,
                },
                timeout=TIMEOUT,
            )
            if resp.status_code < 300:
                logger.info("[MF-WEBHOOK] %s → %s (status=%s)", endpoint, url, resp.status_code)
            else:
                logger.warning("[MF-WEBHOOK] %s → %s FAILED (status=%s body=%s)",
                               endpoint, url, resp.status_code, resp.text[:200])
        except requests.RequestException as exc:
            logger.warning("[MF-WEBHOOK] %s → %s ERROR: %s", endpoint, url, exc)

    # Envoyer en thread pour ne pas bloquer le worker uWSGI
    thread = threading.Thread(target=_post, daemon=True)
    thread.start()


def on_certificate_created(sender, **kwargs):
    """Signal : un certificat a ete cree pour un apprenant."""
    try:
        cert = kwargs.get('certificate')
        if cert is None:
            return
        _send_webhook('certificate-created', {
            'event': 'certificate_created',
            'data': {
                'user_id': cert.user.id if hasattr(cert, 'user') else None,
                'username': cert.user.pii.username if hasattr(cert, 'user') and hasattr(cert.user, 'pii') else '',
                'email': cert.user.pii.email if hasattr(cert, 'user') and hasattr(cert.user, 'pii') else '',
                'course_id': str(cert.course.course_key) if hasattr(cert, 'course') else '',
                'status': cert.status if hasattr(cert, 'status') else '',
                'grade': str(cert.grade) if hasattr(cert, 'grade') else '',
            }
        })
    except Exception as exc:
        logger.warning("[MF-WEBHOOK] certificate_created error: %s", exc)


def on_enrollment_created(sender, **kwargs):
    """Signal : un apprenant s'est inscrit a un cours."""
    try:
        enrollment = kwargs.get('enrollment')
        if enrollment is None:
            return
        _send_webhook('enrollment-created', {
            'event': 'enrollment_created',
            'data': {
                'user_id': enrollment.user.id if hasattr(enrollment, 'user') else None,
                'username': enrollment.user.pii.username if hasattr(enrollment, 'user') and hasattr(enrollment.user, 'pii') else '',
                'email': enrollment.user.pii.email if hasattr(enrollment, 'user') and hasattr(enrollment.user, 'pii') else '',
                'course_id': str(enrollment.course.course_key) if hasattr(enrollment, 'course') else '',
                'mode': enrollment.mode if hasattr(enrollment, 'mode') else '',
                'is_active': enrollment.is_active if hasattr(enrollment, 'is_active') else True,
            }
        })
    except Exception as exc:
        logger.warning("[MF-WEBHOOK] enrollment_created error: %s", exc)


def on_grade_changed(sender, **kwargs):
    """Signal : la note d'un apprenant a change."""
    try:
        user = kwargs.get('user')
        course_grade = kwargs.get('course_grade')
        course_key = kwargs.get('course_key')
        if not user or not course_key:
            return
        _send_webhook('grade-changed', {
            'event': 'grade_changed',
            'data': {
                'user_id': user.id,
                'course_id': str(course_key),
                'percent_grade': float(course_grade.percent) if course_grade else 0,
                'letter_grade': str(course_grade.letter_grade) if course_grade else '',
                'passed': bool(course_grade.passed) if course_grade else False,
            }
        })
    except Exception as exc:
        logger.warning("[MF-WEBHOOK] grade_changed error: %s", exc)


def connect_signals():
    """Connecte les signals OpenEdX au forwarder. Appele dans apps.py ready()."""
    try:
        from openedx_events.learning.signals import (
            CERTIFICATE_CREATED,
            COURSE_ENROLLMENT_CREATED,
        )
        CERTIFICATE_CREATED.connect(on_certificate_created)
        COURSE_ENROLLMENT_CREATED.connect(on_enrollment_created)
        logger.info("[MF-WEBHOOK] Signal forwarder connecte (CERTIFICATE_CREATED, COURSE_ENROLLMENT_CREATED)")
    except ImportError:
        logger.warning("[MF-WEBHOOK] openedx_events non disponible — signals non connectes")

    try:
        from openedx.core.djangoapps.signals.signals import COURSE_GRADE_CHANGED
        COURSE_GRADE_CHANGED.connect(on_grade_changed)
        logger.info("[MF-WEBHOOK] Signal forwarder connecte (COURSE_GRADE_CHANGED)")
    except ImportError:
        logger.warning("[MF-WEBHOOK] COURSE_GRADE_CHANGED non disponible")
