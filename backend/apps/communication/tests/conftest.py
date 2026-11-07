import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

MISSION = "/api/robot/mission"
MESSAGES = "/api/robot/messages"
ETAT = "/api/robot/etat"
SYNC = "/api/robot/messages/sync"


@pytest.fixture
def client_robot(db):
    """Client authentifié par le jeton du robot (en-tête Authorization: Token)."""
    utilisateur = get_user_model().objects.create_user("robot", password="motdepasse")
    jeton = Token.objects.create(user=utilisateur)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {jeton.key}")
    return client


def construire_message(type_message, numero, identifiant, **champs):
    """Message du robot avec les cinq champs communs (docs/protocole.md, 4.1)."""
    return {
        "message_id": identifiant,
        "num_sequence": numero,
        "type": type_message,
        "horodatage": "2026-11-03T10:01:14Z",
        "uptime_ms": 254800,
        **champs,
    }


def construire_mesure(
    zone, mission, numero=3, identifiant="c7d81a4f02e9b365", **champs
):
    base = {
        "mission_id": mission.id,
        "zone_id": zone.id,
        "humidite_pct": 34.5,
        "valeur_brute": 2310,
        "valide": True,
    }
    return construire_message("mesure", numero, identifiant, **{**base, **champs})
