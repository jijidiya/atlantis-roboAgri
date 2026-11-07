import pytest
from django.utils import timezone

from apps.irrigation import services
from apps.irrigation.models import Incident
from apps.mesures.services import enregistrer_mesure
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


@pytest.fixture
def zone():
    return Zone.objects.create(parcelle=Parcelle.objects.create(nom="P"), nom="Z1", seuil_humidite=40)


def test_recommandation_insuffisante(zone):
    mesure = enregistrer_mesure(zone, 1, 20.0, timezone.now())
    assert services.evaluer_mesure(mesure).decision == "insuffisante"


def test_mesure_invalide_cree_un_incident(zone):
    mesure = enregistrer_mesure(zone, 1, 300.0, timezone.now())
    services.evaluer_mesure(mesure)
    assert Incident.objects.filter(type="mesure_invalide").count() == 1


def test_arrosage_refuse_si_obstacle(zone):
    mesure = enregistrer_mesure(zone, 1, 20.0, timezone.now())
    assert services.declencher_arrosage(mesure, True, 80, 30) is None
    assert Incident.objects.filter(type="arrosage_refuse").exists()
