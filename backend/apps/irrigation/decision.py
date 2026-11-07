"""Module PUR : décision d'arrosage à partir d'une mesure et d'un seuil."""


def decider(humidite, seuil, mesure_valide):
    """Retourne 'suffisante', 'insuffisante' ou 'invalide'."""
    if not mesure_valide or humidite is None:
        return "invalide"
    return "insuffisante" if humidite < seuil else "suffisante"
