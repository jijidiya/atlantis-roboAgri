from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import exception_handler

from .exceptions import ErreurMetier


class PaginationStandard(PageNumberPagination):
    page_size = 25
    page_size_query_param = "taille"
    max_page_size = 200


class EstAuthentifie(IsAuthenticated):
    """Point d'extension des permissions (rôles B, C, E plus tard)."""


class _ErreurMetierAPI(APIException):
    status_code = 400
    default_code = "erreur_metier"


def gestionnaire_erreurs(exc, contexte):
    """Convertit les ErreurMetier en réponses JSON propres."""
    if isinstance(exc, ErreurMetier):
        exc = _ErreurMetierAPI(str(exc))
    return exception_handler(exc, contexte)
