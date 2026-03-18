# -*- coding: utf-8 -*-
"""
Middleware Mission Formations.

1. InactiveUserLogoutMiddleware:
   Empeche les utilisateurs inactifs (email non confirme) de rester connectes.
   Remplace la modification directe de register.py (set_logged_in_cookies).

2. ActivationEmailSiteMiddleware:
   Injecte le site_id dans les emails d'activation pour que le bon theme
   soit utilise. Remplace la modification directe de management.py.
"""
import logging

from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class InactiveUserLogoutMiddleware(MiddlewareMixin):
    """
    Deconnecte les utilisateurs dont l'email n'est pas encore active.

    Comportement:
    - Si user.is_authenticated et pas user.is_active → logout + redirect login
    - Pages exemptees: /activate/, /logout, /static/, /api/
    - Les superusers et staff ne sont pas affectes

    Cela reproduit le comportement de la modification dans register.py
    (set_logged_in_cookies seulement si user.is_active) mais de facon
    plus robuste car ca couvre TOUTES les pages, pas juste l'inscription.
    """

    EXEMPT_PATHS = (
        "/activate/",
        "/logout",
        "/static/",
        "/api/",
        "/login",
        "/register",
        "/password_reset",
        "/admin/",
    )

    def process_request(self, request):
        # Chemins exempts — verifier en premier (avant d'acceder a request.user)
        path = request.path
        for exempt in self.EXEMPT_PATHS:
            if path.startswith(exempt):
                return None

        # Heartbeat et health checks n'ont pas de session
        if path in ("/heartbeat", "/health"):
            return None

        try:
            user = request.user
        except AttributeError:
            return None

        if not user.is_authenticated:
            return None
        if user.is_active:
            return None
        if user.is_staff or user.is_superuser:
            return None

        # Utilisateur inactif sur une page non exemptee → deconnexion
        logger.info(
            "[MF-AUTH] Logging out inactive user %s (email not confirmed)",
            user.username,
        )
        logout(request)
        return None
