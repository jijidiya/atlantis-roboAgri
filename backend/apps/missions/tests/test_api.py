import pytest
from rest_framework.test import APIClient

from apps.missions.models import Mission

pytestmark = pytest.mark.django_db


def test_creer_une_mission_avec_ses_etapes(zone):
    reponse = APIClient().post(
        "/api/missions/",
        {"duree_prevue_secondes": 300, "zones": [zone.id, zone.id]},
        format="json",
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut"] == "en_attente"
    assert [etape["ordre"] for etape in corps["etapes"]] == [1, 2]


def test_changer_le_statut_d_une_mission(mission):
    client_api = APIClient()
    url = f"/api/missions/{mission.id}/statut/"
    assert client_api.post(url, {"statut": "envoyee"}, format="json").status_code == 200
    assert Mission.objects.get().statut == "envoyee"


def test_transition_interdite_renvoie_400(mission):
    reponse = APIClient().post(
        f"/api/missions/{mission.id}/statut/", {"statut": "terminee"}, format="json"
    )
    assert reponse.status_code == 400
