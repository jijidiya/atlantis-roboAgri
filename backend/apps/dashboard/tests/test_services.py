import pytest
from django.utils import timezone

from apps.dashboard import services
from apps.mesures.services import enregistrer_mesure

pytestmark = pytest.mark.django_db


def test_evolution_vide():
    assert services.obtenir_evolution_humidite(999) == []


def test_evolution_moyenne_par_jour(zone, mission):
    for numero, humidite in enumerate((40.0, 50.0), start=1):
        enregistrer_mesure(
            zone=zone,
            mission=mission,
            num_sequence=numero,
            humidite_pourcent=humidite,
            valeur_brute=2000,
            est_valide_capteur=True,
            date_mesure=timezone.now(),
        )
    assert services.obtenir_evolution_humidite(zone.id)[0]["humidite_pourcent"] == 45.0


def test_resume_global_contient_les_cles():
    cles = services.obtenir_resume_global().keys()
    assert {"missions", "incidents", "irrigations", "volume_litres"} <= cles
