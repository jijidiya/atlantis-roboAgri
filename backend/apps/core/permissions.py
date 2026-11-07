"""Pagination, permissions et gestion des erreurs partagées."""

from rest_framework.exceptions import APIException, ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import exception_handler

from .exceptions import ErreurMetier


class PaginationStandard(PageNumberPagination):
    """Pagination par défaut : 25 éléments, 200 au maximum."""

    page_size = 25
    page_size_query_param = "taille"
    max_page_size = 200


class EstAuthentifie(IsAuthenticated):
    """Point d'extension des permissions (rôles B, C, E plus tard)."""


class ErreurMetierAPI(APIException):
    """Version HTTP (400) d'une ErreurMetier."""

    status_code = 400
    default_code = "erreur_metier"


def gestionnaire_erreurs(exception, contexte):
    """Formate les erreurs selon docs/protocole.md (section 4.8).

    Args:
        exception: l'exception levée pendant le traitement de la requête.
        contexte: contexte DRF (vue, requête).

    Returns:
        La réponse DRF, ou None si l'exception n'est pas gérée.
    """
    if isinstance(exception, ErreurMetier):
        exception = ErreurMetierAPI(str(exception))
    reponse = exception_handler(exception, contexte)
    if reponse is None:
        return None
    if reponse.status_code == 401:
        reponse.data = {
            "statut": "erreur",
            "code": "JETON_INVALIDE",
            "detail": "jeton absent ou invalide",
        }
    elif isinstance(exception, ParseError):
        reponse.data = {
            "statut": "erreur",
            "code": "MESSAGE_INVALIDE",
            "detail": "JSON invalide",
        }
    return reponse
