"""Enregistrement des mesures. Ne connaît pas irrigation et ne crée aucun incident."""

from .models import MesureHumidite
from .validation import valider_humidite


def enregistrer_mesure(
    zone,
    mission,
    num_sequence,
    humidite_pourcent,
    valeur_brute,
    est_valide_capteur,
    date_mesure,
    est_date_approximative=False,
    uptime_ms=None,
):
    """Valide puis enregistre une mesure. Une mesure invalide est conservée.

    Args:
        zone: zone mesurée.
        mission: mission en cours.
        num_sequence: numéro d'ordre du message du robot.
        humidite_pourcent: humidité étalonnée, ou None.
        valeur_brute: lecture brute du capteur (diagnostic).
        est_valide_capteur: False si le robot a jugé son capteur défaillant.
        date_mesure: date de la mesure.
        est_date_approximative: True si la date est celle de la réception.
        uptime_ms: millisecondes écoulées depuis le démarrage du robot.

    Returns:
        La MesureHumidite enregistrée.
    """
    resultat = valider_humidite(humidite_pourcent, est_valide_capteur)
    return MesureHumidite.objects.create(
        zone=zone,
        mission=mission,
        num_sequence=num_sequence,
        humidite_pourcent=humidite_pourcent if resultat.est_valide else None,
        valeur_brute=valeur_brute,
        est_valide=resultat.est_valide,
        motif_invalidite=resultat.motif,
        date_mesure=date_mesure,
        est_date_approximative=est_date_approximative,
        uptime_ms=uptime_ms,
    )
