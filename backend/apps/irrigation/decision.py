"""Module PUR : décision d'irrigation à partir d'une mesure et d'un seuil."""

SUFFISANTE = "suffisante"
INSUFFISANTE = "insuffisante"
INVALIDE = "invalide"


def decider(humidite_pourcent, seuil_humidite_pourcent, est_valide):
    """Décide si l'humidité d'une zone est suffisante.

    Args:
        humidite_pourcent: humidité étalonnée, ou None.
        seuil_humidite_pourcent: seuil propre à la zone.
        est_valide: False si la mesure est invalide.

    Returns:
        "suffisante", "insuffisante" ou "invalide".
    """
    if not est_valide or humidite_pourcent is None:
        return INVALIDE
    if humidite_pourcent < seuil_humidite_pourcent:
        return INSUFFISANTE
    return SUFFISANTE
