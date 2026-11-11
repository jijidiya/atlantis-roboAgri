"""Tests de l'API des zones (RF01)."""


def test_api_creer_zone_valide(api, parcelle):
    reponse = api.post("/api/v1/zones/", {
        "nom": "Zone C", "humidite_minimum": 30, "humidite_maximum": 70,
        "parcelle": parcelle.pk,
    }, format="json")
    assert reponse.status_code == 201


def test_api_zone_minimum_superieur_maximum_renvoie_400(api, parcelle):
    reponse = api.post("/api/v1/zones/", {
        "nom": "Zone C", "humidite_minimum": 80, "humidite_maximum": 60,
        "parcelle": parcelle.pk,
    }, format="json")
    assert reponse.status_code == 400