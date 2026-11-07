"""Module PUR : sans Django, sans DRF, sans base, sans horloge cachée."""

from dataclasses import dataclass
from math import isnan


@dataclass(frozen=True)
class ResultatValidation:
    valide: bool
    motif: str = ""


def valider_humidite(valeur, precedente=None, ecart_max=40.0):
    """Contrôle de plausibilité d'un pourcentage d'humidité."""
    if valeur is None or (isinstance(valeur, float) and isnan(valeur)):
        return ResultatValidation(False, "valeur_manquante")
    if not 0 <= valeur <= 100:
        return ResultatValidation(False, "hors_plage")
    if precedente is not None and abs(valeur - precedente) > ecart_max:
        return ResultatValidation(False, "saut_incoherent")
    return ResultatValidation(True)
