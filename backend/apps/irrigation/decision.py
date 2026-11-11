"""Règle de décision d'irrigation (architecture.pdf §6).

Module PUR : aucun import Django, aucun accès à la base. Les seuils sont reçus
en paramètre (ils viennent de la zone, saisis dans l'application).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    etat: str                   # "suffisante" | "insuffisante" | "invalide"
    arrosage_recommande: bool
    motif: str                  # texte lisible, affiché dans l'application
    incident: bool              # True si un incident doit être signalé (RG17)


def decider(humidite_pct, valide, seuil_min, age_mesure_s, age_max_s) -> Decision:
    """Décide s'il faut recommander un arrosage.

    1. Mesure invalide d'abord : valeur absente, marquée invalide par
       validation.py, ou trop ancienne. Elle ne produit jamais de recommandation.
    2. Sinon, humidité strictement sous le seuil minimum : insuffisante.
    3. Sinon (y compris à égalité avec le seuil) : suffisante.
    """
    if not valide:
        return Decision("invalide", False, "Mesure invalide : aucune recommandation.", True)
    if humidite_pct is None:
        return Decision("invalide", False, "Humidité absente : aucune recommandation.", True)
    if age_mesure_s is None or age_mesure_s > age_max_s:
        return Decision("invalide", False, "Mesure trop ancienne : aucune recommandation.", True)
    if humidite_pct < seuil_min:
        return Decision(
            "insuffisante", True,
            f"Humidité {humidite_pct} % sous le seuil minimum de {seuil_min} %.", False,
        )
    return Decision(
        "suffisante", False,
        f"Humidité {humidite_pct} % au moins égale au seuil minimum de {seuil_min} %.", False,
    )