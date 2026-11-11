"""Contrôle d'une mesure reçue du robot.

Module PUR : aucun import Django, aucun accès à la base, pas d'horloge cachée
(l'heure actuelle est passée en paramètre). Il se teste sans base de données.

Une mesure douteuse n'est jamais rejetée : elle est enregistrée avec le statut
« invalide » (traçabilité) et ne peut jamais produire de recommandation.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

# À ajuster avec les relevés d'étalonnage (docs/experimentation/etalonnage/).
VALEUR_BRUTE_MIN = 0
VALEUR_BRUTE_MAX = 4095          # convertisseur 12 bits de l'ESP32
MARGE_EXTREME = 10               # brut collé à une borne : capteur débranché ou en court-circuit
TOLERANCE_FUTUR = timedelta(minutes=5)   # horloge du robot légèrement en avance


@dataclass(frozen=True)
class ResultatValidation:
    statut: str                          # "valide" | "invalide" | "manquante"
    raison: str                          # texte lisible
    humidite_a_stocker: Decimal | None   # None si le pourcentage est absent ou hors 0-100


def valider_mesure(
    humidite_pct: float | None,
    valeur_brute: int | None,
    horodatage: datetime,
    maintenant: datetime,
) -> ResultatValidation:
    """Renvoie le statut d'une lecture (RG8)."""
    pourcentage_ok = humidite_pct is not None and 0 <= humidite_pct <= 100
    stocke = Decimal(str(round(humidite_pct, 2))) if pourcentage_ok else None

    if humidite_pct is None and valeur_brute is None:
        return ResultatValidation("manquante", "Aucune valeur reçue.", None)
    if humidite_pct is None:
        return ResultatValidation("invalide", "Pourcentage d'humidité absent.", None)
    if not pourcentage_ok:
        return ResultatValidation("invalide", "Pourcentage hors de l'intervalle 0 à 100.", None)

    if valeur_brute is not None:
        if not VALEUR_BRUTE_MIN <= valeur_brute <= VALEUR_BRUTE_MAX:
            return ResultatValidation("invalide", "Valeur brute hors de la plage du capteur.", stocke)
        if (valeur_brute <= VALEUR_BRUTE_MIN + MARGE_EXTREME
                or valeur_brute >= VALEUR_BRUTE_MAX - MARGE_EXTREME):
            return ResultatValidation(
                "invalide", "Valeur brute extrême : capteur débranché ou en court-circuit.", stocke
            )

    if horodatage > maintenant + TOLERANCE_FUTUR:
        return ResultatValidation("invalide", "Horodatage dans le futur.", stocke)

    return ResultatValidation("valide", "Mesure valide.", stocke)