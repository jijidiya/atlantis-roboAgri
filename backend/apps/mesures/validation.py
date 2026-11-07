"""Module PUR : sans Django, sans DRF, sans base, sans horloge cachée."""

from dataclasses import dataclass
from math import isnan


@dataclass(frozen=True)
class ResultatValidation:
    """Résultat du contrôle d'une mesure."""

    est_valide: bool
    motif: str = ""


def valider_humidite(humidite_pourcent, est_valide_capteur=True):
    """Contrôle la plausibilité d'une humidité en pourcentage.

    Args:
        humidite_pourcent: humidité étalonnée, ou None.
        est_valide_capteur: vaut False si le robot a jugé son capteur défaillant.

    Returns:
        Un ResultatValidation ; en cas d'invalidité, `motif` vaut
        "capteur_invalide", "valeur_manquante" ou "hors_plage".
    """
    if not est_valide_capteur:
        return ResultatValidation(False, "capteur_invalide")
    if humidite_pourcent is None or (
        isinstance(humidite_pourcent, float) and isnan(humidite_pourcent)
    ):
        return ResultatValidation(False, "valeur_manquante")
    if not 0 <= humidite_pourcent <= 100:
        return ResultatValidation(False, "hors_plage")
    return ResultatValidation(True)
