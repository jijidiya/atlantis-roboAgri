"""Permissions communes."""
import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission

from .exceptions import NonAuthentifie


class EstRobot(BasePermission):
    """Autorise uniquement les requêtes portant la clé secrète du robot.

    Le robot envoie l'en-tête `X-Cle-Robot`. La clé attendue vient de
    settings.CLE_ROBOT (variable d'environnement, jamais dans Git). Si elle
    n'est pas définie, tout est refusé.
    """

    def has_permission(self, request, view):
        attendue = getattr(settings, "CLE_ROBOT", "") or ""
        fournie = request.headers.get("X-Cle-Robot", "")
        if attendue and hmac.compare_digest(fournie.encode(), attendue.encode()):
            return True
        raise NonAuthentifie("Clé du robot absente ou invalide.")