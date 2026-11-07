"""Exceptions métier partagées. Aucune logique ici, seulement des types."""


class ErreurMetier(Exception):
    """Erreur de règle métier (convertie en réponse 400/409 par l'API)."""


class TransitionInterdite(ErreurMetier):
    """Changement d'état de mission non autorisé (section 8.4)."""


class DonneesInvalides(ErreurMetier):
    """Message ou valeur qui ne respecte pas le protocole."""
