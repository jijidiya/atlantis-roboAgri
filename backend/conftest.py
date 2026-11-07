"""Fixtures Pytest partagées par tous les tests du backend."""

import pytest

from apps.missions import services as services_missions
from apps.parcelles.models import Parcelle, Zone


@pytest.fixture
def zone(db):
    """Une zone avec un seuil d'humidité de 40 %."""
    parcelle = Parcelle.objects.create(nom="Parcelle test")
    return Zone.objects.create(
        parcelle=parcelle, nom="Zone 1", ordre=1, seuil_humidite_pourcent=40
    )


@pytest.fixture
def mission(zone):
    """Une mission en attente avec une étape sur la zone."""
    return services_missions.creer_mission(600, [zone])
