"""Conditions de sécurité d'une intervention d'irrigation (architecture.pdf §6.4).

Module PUR. Il n'y a pas de pompe sur le robot : l'intervention est saisie par
l'utilisateur, mais le serveur applique quand même la durée maximale (RG18) et
refuse après une mesure invalide (RG17).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Verification:
    autorisee: bool
    code: str | None     # "duree_trop_longue" | "derniere_mesure_invalide" | None
    motif: str | None


def verifier_intervention(duree_secondes, duree_max_secondes, derniere_mesure_valide) -> Verification:
    """`derniere_mesure_valide` : True, False, ou None s'il n'existe aucune mesure."""
    if duree_secondes > duree_max_secondes:
        return Verification(
            False, "duree_trop_longue",
            f"La durée ({duree_secondes} s) dépasse le maximum autorisé ({duree_max_secondes} s).",
        )
    if derniere_mesure_valide is False:
        return Verification(
            False, "derniere_mesure_invalide",
            "Dernière mesure invalide : arrosage impossible.",
        )
    return Verification(True, None, None)