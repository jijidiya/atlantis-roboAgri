"""Données de départ réutilisées par tous les tests."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.parcelles.models import Parcelle, Zone


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def utilisateur(db):
    return get_user_model().objects.create_user(
        email="test@exemple.cd", password="mdp-test", nom="Test", prenom="Un"
    )


@pytest.fixture
def parcelle(utilisateur):
    return Parcelle.objects.create(nom="Parcelle test", utilisateur=utilisateur)


@pytest.fixture
def zone_a(parcelle):
    return Zone.objects.create(
        nom="Zone A", humidite_minimum=30, humidite_maximum=70, parcelle=parcelle
    )


@pytest.fixture
def zone_b(parcelle):
    return Zone.objects.create(
        nom="Zone B", humidite_minimum=30, humidite_maximum=70, parcelle=parcelle
    )