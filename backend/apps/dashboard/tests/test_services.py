import pytest
from django.utils import timezone

from apps.dashboard import services
from apps.mesures.services import enregistrer_mesure
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


def test_evolution_vide():
    assert services.evolution_humidite(999) == []


def test_evolution_moyenne_par_jour():
    zone = Zone.objects.create(parcelle=Parcelle.objects.create(nom="P"), nom="Z1")
    enregistrer_mesure(zone, 1, 40.0, timezone.now())
    enregistrer_mesure(zone, 2, 50.0, timezone.now())
    assert services.evolution_humidite(zone.id)[0]["humidite"] == 45.0


def test_resume_global_contient_les_cles():
    assert {"missions", "incidents", "irrigations", "volume_litres"} <= services.resume_global().keys()
