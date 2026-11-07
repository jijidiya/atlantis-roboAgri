"""Exceptions métier partagées. Aucune logique ici, seulement des types."""


class ErreurMetier(Exception):
    """Erreur de règle métier, convertie en réponse 400 par l'API."""


class TransitionInterdite(ErreurMetier):
    """Changement de statut de mission non autorisé."""


class DonneesInvalides(ErreurMetier):
    """Valeur qui ne respecte pas une règle métier."""
