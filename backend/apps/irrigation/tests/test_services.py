import pytest
from django.utils import timezone

from apps.irrigation import services
from apps.irrigation.models import CodeIncident, Incident, TypeIrrigation
from apps.mesures.services import enregistrer_mesure

pytestmark = pytest.mark.django_db


def faire_mesure(zone, mission, humidite_pourcent, est_valide_capteur=True):
    return enregistrer_mesure(
        zone=zone,
        mission=mission,
        num_sequence=1,
        humidite_pourcent=humidite_pourcent,
        valeur_brute=2000,
        est_valide_capteur=est_valide_capteur,
        date_mesure=timezone.now(),
    )


def test_recommandation_insuffisante(zone, mission):
    irrigation = services.evaluer_mesure(faire_mesure(zone, mission, 20.0))
    assert irrigation.decision == "insuffisante"
    assert irrigation.type == TypeIrrigation.RECOMMANDATION


def test_recommandation_suffisante(zone, mission):
    assert (
        services.evaluer_mesure(faire_mesure(zone, mission, 80.0)).decision
        == "suffisante"
    )


def test_mesure_invalide_cree_un_incident(zone, mission):
    mesure = faire_mesure(zone, mission, None, est_valide_capteur=False)
    assert services.evaluer_mesure(mesure).decision == "invalide"
    assert Incident.objects.filter(code=CodeIncident.CAPTEUR_INVALIDE).count() == 1


def test_irrigation_refusee_si_obstacle(zone, mission):
    mesure = faire_mesure(zone, mission, 20.0)
    assert services.declencher_irrigation(mesure, True, 80, 30) is None


def test_irrigation_autorisee(zone, mission):
    mesure = faire_mesure(zone, mission, 20.0)
    intervention = services.declencher_irrigation(mesure, False, 80, 30)
    assert intervention.type == TypeIrrigation.INTERVENTION
    assert intervention.duree_secondes == 30
