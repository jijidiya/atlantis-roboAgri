"""Lecture du capteur d'humidité du sol (module HW-103 V0.1.2, sonde HW-080).

Règle stricte : tant que l'étalonnage n'est pas renseigné dans config.py,
aucune lecture n'est déclarée valide ni convertie en pourcentage.
"""

import time
import config

try:
    from machine import ADC, Pin
except ImportError:
    ADC = None
    Pin = None


def _initialiser_materiel():
    """Prépare la broche d'alimentation (GPIO 32) et l'entrée ADC1 (GPIO 34)."""
    if ADC is None or Pin is None:
        return None, None

    alim = Pin(config.BROCHE_ALIMENTATION_CAPTEUR_HUMIDITE, Pin.OUT)
    alim.value(0)

    adc = ADC(Pin(config.BROCHE_CAPTEUR_HUMIDITE))
    if hasattr(adc, "atten") and hasattr(ADC, "ATTN_11DB"):
        adc.atten(ADC.ATTN_11DB)
    if hasattr(adc, "width") and hasattr(ADC, "WIDTH_12BIT"):
        adc.width(ADC.WIDTH_12BIT)
    return alim, adc


def lire_point(alim=None, adc=None, simulation_lectures=None):
    """Effectue un point de collecte (NOMBRE_LECTURES_PAR_POINT lectures).

    Alimente le capteur uniquement pendant la mesure, attend le délai de
    stabilisation, puis coupe l'alimentation après lecture.
    """
    if simulation_lectures is not None:
        if not simulation_lectures:
            raise ValueError("simulation_lectures ne peut pas être vide")
        moyenne = sum(simulation_lectures) / len(simulation_lectures)
        return {
            "lectures_brutes": list(simulation_lectures),
            "moyenne_brute": round(moyenne, 2),
        }

    possede_materiel = alim is None and adc is None
    if possede_materiel:
        alim, adc = _initialiser_materiel()

    if adc is None:
        raise RuntimeError(
            "Matériel capteur indisponible : exécutez sur l'ESP32 ou passez simulation_lectures."
        )

    lectures = []
    try:
        if alim is not None:
            alim.value(1)
        time.sleep_ms(config.DELAI_STABILISATION_MILLISECONDES)

        for index in range(config.NOMBRE_LECTURES_PAR_POINT):
            lectures.append(adc.read())
            if index < config.NOMBRE_LECTURES_PAR_POINT - 1:
                time.sleep_ms(config.DELAI_ENTRE_LECTURES_MILLISECONDES)
    finally:
        if alim is not None:
            alim.value(0)

    moyenne = sum(lectures) / len(lectures)
    return {
        "lectures_brutes": lectures,
        "moyenne_brute": round(moyenne, 2),
    }


def evaluer_lecture_brute(moyenne_brute):
    """Évalue une valeur brute selon l'étalonnage et la détection d'air libre.

    Retourne un dictionnaire :
    - valide (bool)
    - humidite_pct (float | None)
    - motif (str | None)
    """
    brute_int = int(round(moyenne_brute))

    # Extrêmes absolus : débranché / court-circuit / saturation
    if brute_int <= 0 or brute_int >= config.VALEUR_MAXIMALE_CONVERTISSEUR:
        return {
            "valide": False,
            "humidite_pct": None,
            "motif": "VALEUR_EXTREME_INVALIDE",
        }

    # Détection sonde non insérée si VALEUR_BRUTE_AIR est renseignée
    if config.DETECTION_SONDE_NON_INSEREE_ACTIVE and config.VALEUR_BRUTE_AIR is not None:
        ecart_air = abs(brute_int - config.VALEUR_BRUTE_AIR)
        if ecart_air < config.ECART_MINIMAL_AIR:
            return {
                "valide": False,
                "humidite_pct": None,
                "motif": config.CODE_SONDE_NON_INSEREE,
            }

    # Refus de convertir en % tant que l'étalonnage sec/eau n'est pas fait
    if not config.ETALONNAGE_DISPONIBLE:
        return {
            "valide": False,
            "humidite_pct": None,
            "motif": "ETALONNAGE_NON_RENSEIGNE",
        }

    if (
        brute_int < config.VALEUR_BRUTE_MINIMALE_VALIDE
        or brute_int > config.VALEUR_BRUTE_MAXIMALE_VALIDE
    ):
        return {
            "valide": False,
            "humidite_pct": None,
            "motif": "HORS_PLAGE_ETALONNAGE",
        }

    # Capteur résistif : valeur haute = sec, valeur basse = eau
    plage = config.VALEUR_BRUTE_SECHE - config.VALEUR_BRUTE_EAU
    ratio = (config.VALEUR_BRUTE_SECHE - brute_int) / plage
    if ratio < 0.0:
        ratio = 0.0
    elif ratio > 1.0:
        ratio = 1.0

    return {
        "valide": True,
        "humidite_pct": round(ratio * 100.0, 1),
        "motif": None,
    }


def mesurer_etape(alim=None, adc=None, simulation_points=None):
    """Exécute une étape complète (NOMBRE_POINTS_PAR_ETAPE points)."""
    points = []
    for idx in range(config.NOMBRE_POINTS_PAR_ETAPE):
        sim = simulation_points[idx] if simulation_points and idx < len(simulation_points) else None
        point_data = lire_point(alim=alim, adc=adc, simulation_lectures=sim)
        evaluation = evaluer_lecture_brute(point_data["moyenne_brute"])
        point_data.update(evaluation)
        point_data["point"] = idx + 1
        points.append(point_data)

    return {
        "type": "mesure",
        "date_etalonnage": config.DATE_ETALONNAGE,
        "etalonnage_disponible": config.ETALONNAGE_DISPONIBLE,
        "points": points,
    }


if __name__ == "__main__":
    if ADC is not None:
        print("Mesure étape ESP32 :", mesurer_etape())
    else:
        exemple_points = [[2400, 2410, 2395], [2420, 2405, 2415], [2390, 2400, 2408]]
        print("Simulation étape (sans étalonnage) :", mesurer_etape(simulation_points=exemple_points))