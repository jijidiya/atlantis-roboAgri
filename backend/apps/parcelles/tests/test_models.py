import pytest
from django.db import IntegrityError, transaction

from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


def test_creer_parcelle_et_zone():
    parcelle = Parcelle.objects.create(nom="Parcelle A")
    zone = Zone.objects.create(parcelle=parcelle, nom="Zone 1", seuil_humidite=35)
    assert zone in parcelle.zones.all()
    assert str(zone) == "Parcelle A / Zone 1"


def test_nom_de_zone_unique_par_parcelle():
    parcelle = Parcelle.objects.create(nom="Parcelle A")
    Zone.objects.create(parcelle=parcelle, nom="Zone 1")
    with pytest.raises(IntegrityError), transaction.atomic():
        Zone.objects.create(parcelle=parcelle, nom="Zone 1")


def test_seuil_hors_limites_refuse_par_la_base():
    parcelle = Parcelle.objects.create(nom="Parcelle B")
    with pytest.raises(IntegrityError), transaction.atomic():
        Zone.objects.create(parcelle=parcelle, nom="Zone X", seuil_humidite=150)
