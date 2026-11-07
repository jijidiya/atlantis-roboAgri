import pytest
from rest_framework.test import APIClient

from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_api():
    return APIClient()


def test_creer_puis_lister_une_parcelle(client_api):
    reponse = client_api.post(
        "/api/parcelles/", {"nom": "Test", "localisation": "Bukavu"}, format="json"
    )
    assert reponse.status_code == 201
    assert reponse.json()["zones"] == []
    liste = client_api.get("/api/parcelles/").json()
    assert liste["count"] == 1 and liste["results"][0]["nom"] == "Test"


def test_modifier_et_supprimer_une_parcelle(client_api):
    parcelle = Parcelle.objects.create(nom="Ancien nom")
    reponse = client_api.patch(
        f"/api/parcelles/{parcelle.id}/", {"nom": "Nouveau nom"}, format="json"
    )
    assert reponse.status_code == 200
    assert client_api.delete(f"/api/parcelles/{parcelle.id}/").status_code == 204
    assert Parcelle.objects.count() == 0


def test_creer_une_zone_dans_une_parcelle(client_api):
    parcelle = Parcelle.objects.create(nom="P")
    reponse = client_api.post(
        "/api/zones/",
        {
            "parcelle": parcelle.id,
            "nom": "Zone 1",
            "ordre": 1,
            "seuil_humidite_pourcent": 45,
        },
        format="json",
    )
    assert reponse.status_code == 201
    assert Zone.objects.get().seuil_humidite_pourcent == 45


def test_seuil_superieur_a_100_refuse(client_api):
    parcelle = Parcelle.objects.create(nom="P")
    reponse = client_api.post(
        "/api/zones/",
        {"parcelle": parcelle.id, "nom": "Zone 1", "seuil_humidite_pourcent": 150},
        format="json",
    )
    assert reponse.status_code == 400


def test_filtrer_les_zones_par_parcelle(client_api):
    p1, p2 = Parcelle.objects.create(nom="P1"), Parcelle.objects.create(nom="P2")
    Zone.objects.create(parcelle=p1, nom="Z")
    Zone.objects.create(parcelle=p2, nom="Z")
    reponse = client_api.get(f"/api/zones/?parcelle={p1.id}").json()
    assert reponse["count"] == 1
