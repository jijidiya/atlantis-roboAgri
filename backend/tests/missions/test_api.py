"""Tests de l'API des missions (RF02) : création, RG5, cycle de vie."""
from apps.parcelles.models import Parcelle, Zone


def corps(utilisateur, parcelle, *zones):
    return {
        "utilisateur": utilisateur.pk,
        "parcelle": parcelle.pk,
        "etapes": [{"numero_ordre": i + 1, "zone": z.pk} for i, z in enumerate(zones)],
    }


def test_creer_mission_avec_deux_etapes(api, utilisateur, parcelle, zone_a, zone_b):
    reponse = api.post("/api/v1/missions/", corps(utilisateur, parcelle, zone_a, zone_b), format="json")
    assert reponse.status_code == 201
    assert reponse.data["statut"] == "planifiee"
    assert len(reponse.data["etapes"]) == 2


def test_mission_sans_etape_refusee(api, utilisateur, parcelle):
    reponse = api.post("/api/v1/missions/", corps(utilisateur, parcelle), format="json")
    assert reponse.status_code == 400


def test_zone_d_une_autre_parcelle_refusee_rg5(api, utilisateur, parcelle, zone_a):
    autre = Parcelle.objects.create(nom="Autre", utilisateur=utilisateur)
    zone_etrangere = Zone.objects.create(
        nom="Z", humidite_minimum=30, humidite_maximum=70, parcelle=autre
    )
    reponse = api.post(
        "/api/v1/missions/", corps(utilisateur, parcelle, zone_a, zone_etrangere), format="json"
    )
    assert reponse.status_code == 400


def test_demarrer_puis_redemarrer_renvoie_409(api, utilisateur, parcelle, zone_a):
    mission = api.post("/api/v1/missions/", corps(utilisateur, parcelle, zone_a), format="json").data
    url = f"/api/v1/missions/{mission['mission_id']}/demarrer/"
    premiere = api.post(url)
    assert premiere.status_code == 200
    assert premiere.data["statut"] == "en_cours"
    assert api.post(url).status_code == 409