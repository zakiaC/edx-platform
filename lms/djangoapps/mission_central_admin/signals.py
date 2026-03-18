# -*- coding: utf-8 -*-
"""
Signal handlers Mission Formations.

ActivationEmailSiteHandler:
Monkey-patch le task send_activation_email pour injecter automatiquement
le site_id courant. Cela garantit que l'email d'activation utilise le
bon theme (Mission) au lieu du theme par defaut OpenEdX.

Remplace la modification directe de management.py.
"""
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def patch_activation_email_with_site_id():
    """
    Wrappe send_activation_email.delay() pour ajouter site_id automatiquement.

    Le task OpenEdX natif accepte deja site_id comme parametre optionnel,
    mais le code appelant ne le passe pas. Ce patch intercepte l'appel
    et ajoute le site_id du site courant.
    """
    try:
        from openedx.core.djangoapps.user_authn.tasks import send_activation_email
        from openedx.core.djangoapps.theming.helpers import get_current_site

        original_delay = send_activation_email.delay

        @wraps(original_delay)
        def patched_delay(msg_string, from_address=None, site_id=None, **kwargs):
            if site_id is None:
                try:
                    current_site = get_current_site()
                    if current_site:
                        site_id = current_site.id
                except Exception:
                    pass
            return original_delay(msg_string, from_address, site_id=site_id, **kwargs)

        send_activation_email.delay = patched_delay
        logger.info("[MF-SIGNALS] Patched send_activation_email.delay with site_id injection")
    except ImportError:
        logger.warning("[MF-SIGNALS] Could not patch send_activation_email — module not found")
    except Exception as exc:
        logger.warning("[MF-SIGNALS] Could not patch send_activation_email: %s", exc)
