"""Exceptions métier et gestionnaire d'erreurs unique de l'API.

Les services lèvent ces exceptions ; les vues n'ont aucun try/except :
`gestionnaire_exceptions` transforme TOUTE erreur en une seule forme JSON
(architecture.pdf §8.3) :

    {"erreur": {"code": "...", "message": "...", "details": {...}}}
"""
import logging

from rest_framework import exceptions as erreurs_drf
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback

journal = logging.getLogger(__name__)


class ErreurMetier(Exception):
    """Erreur prévue par les règles de gestion (classe de base)."""

    code = "ERREUR_METIER"
    statut_http = 400

    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DonneesInvalides(ErreurMetier):
    code = "DONNEES_INVALIDES"
    statut_http = 400


class NonAuthentifie(ErreurMetier):
    code = "NON_AUTHENTIFIE"
    statut_http = 401


class IdentifiantsInvalides(ErreurMetier):
    """Connexion refusée : le frontend ne doit pas tenter de rafraîchir le jeton."""

    code = "IDENTIFIANTS_INVALIDES"
    statut_http = 401


class AccesRefuse(ErreurMetier):
    code = "ACCES_REFUSE"
    statut_http = 403


class ArrosageInterdit(ErreurMetier):
    code = "ARROSAGE_INTERDIT"
    statut_http = 403


class RessourceIntrouvable(ErreurMetier):
    code = "RESSOURCE_INTROUVABLE"
    statut_http = 404


class TransitionInterdite(ErreurMetier):
    code = "TRANSITION_INTERDITE"
    statut_http = 409


class Conflit(ErreurMetier):
    code = "CONFLIT"
    statut_http = 409


def _enveloppe(code, message, details, statut):
    return Response(
        {"erreur": {"code": code, "message": message, "details": details}},
        status=statut,
    )


# statut HTTP -> (code, message) pour les erreurs levées par DRF lui-même.
_ERREURS_DRF = {
    400: ("DONNEES_INVALIDES", "Requête invalide."),
    401: ("NON_AUTHENTIFIE", "Authentification requise ou jeton invalide."),
    403: ("ACCES_REFUSE", "Action non autorisée."),
    404: ("RESSOURCE_INTROUVABLE", "Élément introuvable."),
    405: ("METHODE_NON_AUTORISEE", "Méthode non autorisée sur cette adresse."),
}


def gestionnaire_exceptions(exception, contexte):
    """À brancher dans REST_FRAMEWORK["EXCEPTION_HANDLER"]."""
    if isinstance(exception, ErreurMetier):
        return _enveloppe(
            exception.code, exception.message, exception.details, exception.statut_http
        )

    reponse = exception_handler(exception, contexte)  # gère aussi Http404 et PermissionDenied
    if reponse is None:
        # Erreur imprévue : on journalise, on ne renvoie aucun détail technique.
        journal.exception("Erreur inattendue dans l'API", exc_info=exception)
        set_rollback()
        return _enveloppe("ERREUR_INTERNE", "Erreur interne du serveur.", {}, 500)

    code, message = _ERREURS_DRF.get(
        reponse.status_code, ("ERREUR_REQUETE", "La requête n'a pas pu être traitée.")
    )
    details = {}
    if isinstance(exception, erreurs_drf.ValidationError):
        message = "Certains champs sont invalides."
        donnees = reponse.data
        details = donnees if isinstance(donnees, dict) else {"non_field_errors": donnees}
    elif isinstance(exception, erreurs_drf.ParseError):
        message = "Le corps de la requête n'est pas un JSON valide."
    return _enveloppe(code, message, details, reponse.status_code)