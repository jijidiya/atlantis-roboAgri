"""Module PUR : conditions de sécurité avant d'autoriser la pompe."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultatSecurite:
    autorise: bool
    motif: str = ""


def verifier(mesure_valide, obstacle_detecte, batterie_pct, batterie_min=20):
    if not mesure_valide:
        return ResultatSecurite(False, "mesure_invalide")
    if obstacle_detecte:
        return ResultatSecurite(False, "obstacle")
    if batterie_pct is not None and batterie_pct < batterie_min:
        return ResultatSecurite(False, "batterie_faible")
    return ResultatSecurite(True)
