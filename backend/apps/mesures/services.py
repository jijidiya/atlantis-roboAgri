"""Enregistrement des mesures. Ne connaît pas irrigation et ne crée aucun incident."""

from .models import Mesure
from .validation import valider_humidite


def enregistrer_mesure(zone, sequence, humidite, mesuree_le, mission=None):
    """Valide puis enregistre. Une mesure invalide est conservée, marquée invalide."""
    precedente = (
        Mesure.objects.filter(zone=zone, valide=True).values_list("humidite", flat=True).first()
    )
    resultat = valider_humidite(humidite, precedente)
    return Mesure.objects.create(
        zone=zone,
        mission=mission,
        sequence=sequence,
        humidite=humidite,
        mesuree_le=mesuree_le,
        valide=resultat.valide,
        motif_invalidite=resultat.motif,
    )
