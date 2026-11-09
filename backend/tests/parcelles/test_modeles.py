"""Tests des contraintes de la base pour parcelles (RF01)."""
import pytest
from django.db import IntegrityError, transaction

from apps.parcelles.models import Zone


def test_zone_minimum_superieur_maximum_refuse_par_la_base(parcelle):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Zone.objects.create(
                nom="X", humidite_minimum=80, humidite_maximum=60, parcelle=parcelle
            )


def test_zone_humidite_hors_0_100_refusee_par_la_base(parcelle):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Zone.objects.create(
                nom="X", humidite_minimum=10, humidite_maximum=150, parcelle=parcelle
            )