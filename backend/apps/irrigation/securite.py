"""Module PUR : conditions de sécurité avant d'autoriser la pompe."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultatSecurite:
    """Résultat du contrôle de sécurité."""

    est_autorise: bool
    motif: str = ""


def verifier(est_valide, a_obstacle, batterie_pourcent, batterie_min_pourcent=20):
    """Vérifie qu'une irrigation peut être déclenchée sans danger.

    Args:
        est_valide: la mesure sur laquelle repose la décision est valide.
        a_obstacle: un obstacle est détecté devant le robot.
        batterie_pourcent: niveau de batterie, ou None s'il est inconnu.
        batterie_min_pourcent: niveau minimal pour irriguer.

    Returns:
        Un ResultatSecurite avec le motif du refus le cas échéant.
    """
    if not est_valide:
        return ResultatSecurite(False, "mesure_invalide")
    if a_obstacle:
        return ResultatSecurite(False, "obstacle")
    if batterie_pourcent is not None and batterie_pourcent < batterie_min_pourcent:
        return ResultatSecurite(False, "batterie_faible")
    return ResultatSecurite(True)
