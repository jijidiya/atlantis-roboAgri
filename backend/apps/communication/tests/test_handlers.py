import pytest

from apps.communication.handlers import traiter_message
from apps.irrigation.models import Incident, Irrigation
from apps.mesures.models import Mesure
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


@pytest.fixture
def zone():
    return Zone.objects.create(parcelle=Parcelle.objects.create(nom="P"), nom="Z1", seuil_humidite=40)


def donnees(zone, **changements):
    base = {
        "id_message": "m1", "zone_id": zone.id, "sequence": 1,
        "humidite": 20.0, "mesure_le": "2026-11-04T10:00:00+01:00",
    }
    return {**base, **changements}


def test_enchainement_complet(zone):
    assert traiter_message(donnees(zone)).statut == "traite"
    assert Mesure.objects.count() == 1
    assert Irrigation.objects.get().decision == "insuffisante"


def test_message_en_double(zone):
    traiter_message(donnees(zone))
    assert traiter_message(donnees(zone)).statut == "doublon"
    assert Mesure.objects.count() == 1


def test_message_mal_forme_cree_un_incident(zone):
    assert traiter_message({"n_importe": "quoi"}).statut == "rejete"
    assert Incident.objects.filter(type="message_invalide").exists()
