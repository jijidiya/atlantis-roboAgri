import pytest
from django.utils import timezone

from apps.mesures.services import enregistrer_mesure

pytestmark = pytest.mark.django_db


def enregistrer(zone, mission, humidite_pourcent, est_valide_capteur=True):
    return enregistrer_mesure(
        zone=zone,
        mission=mission,
        num_sequence=1,
        humidite_pourcent=humidite_pourcent,
        valeur_brute=2310,
        est_valide_capteur=est_valide_capteur,
        date_mesure=timezone.now(),
    )


def test_mesure_valide(zone, mission):
    mesure = enregistrer(zone, mission, 42.0)
    assert mesure.est_valide and mesure.humidite_pourcent == 42.0


def test_capteur_invalide_conserve_la_valeur_brute(zone, mission):
    mesure = enregistrer(zone, mission, None, est_valide_capteur=False)
    assert not mesure.est_valide
    assert mesure.humidite_pourcent is None and mesure.valeur_brute == 2310


def test_valeur_hors_plage_jamais_stockee_comme_humidite(zone, mission):
    mesure = enregistrer(zone, mission, 250.0)
    assert not mesure.est_valide and mesure.motif_invalidite == "hors_plage"
    assert mesure.humidite_pourcent is None
