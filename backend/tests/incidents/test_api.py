"""Tests des incidents : API en lecture seule et service de signalement (RG11)."""
from apps.incidents import services
from apps.incidents.models import Incident
from apps.parcelles.models import Parcelle


def test_lister_les_incidents(api, mission):
    incident = Incident.objects.create(type_incident="obstacle", mission=mission)

    reponse = api.get("/api/v1/incidents/")

    assert reponse.status_code == 200
    assert reponse.data["count"] == 1
    assert reponse.data["results"][0]["incident_id"] == incident.pk


def test_detail_d_un_incident(api, mission):
    incident = Incident.objects.create(type_incident="obstacle", mission=mission)

    reponse = api.get(f"/api/v1/incidents/{incident.pk}/")

    assert reponse.status_code == 200
    assert reponse.data["type_incident"] == "obstacle"
    assert reponse.data["mission"] == mission.pk


def test_filtre_par_type_incident(api, mission):
    Incident.objects.create(type_incident="obstacle", mission=mission)
    Incident.objects.create(type_incident="capteur_defaillant", mission=mission)

    reponse = api.get("/api/v1/incidents/", {"type_incident": "obstacle"})

    assert reponse.data["count"] == 1
    assert reponse.data["results"][0]["type_incident"] == "obstacle"


def test_filtre_par_mission(api, utilisateur, parcelle, mission):
    autre_parcelle = Parcelle.objects.create(nom="Autre", utilisateur=utilisateur)
    autre_mission = mission.__class__.objects.create(
        utilisateur=utilisateur, parcelle=autre_parcelle
    )
    Incident.objects.create(type_incident="obstacle", mission=mission)
    Incident.objects.create(type_incident="obstacle", mission=autre_mission)

    reponse = api.get("/api/v1/incidents/", {"mission": autre_mission.pk})

    assert reponse.data["count"] == 1
    assert reponse.data["results"][0]["mission"] == autre_mission.pk


def test_filtre_par_date(api, mission):
    Incident.objects.create(type_incident="obstacle", mission=mission)

    assert api.get("/api/v1/incidents/", {"du": "2000-01-01"}).data["count"] == 1
    assert api.get("/api/v1/incidents/", {"au": "2000-01-01"}).data["count"] == 0


def test_liste_des_incidents_sans_jeton_renvoie_401(api_anonyme, db):
    assert api_anonyme.get("/api/v1/incidents/").status_code == 401


def test_signaler_incident_lie_les_mesures(mission, mesure):
    incident = services.signaler_incident(
        "mesure_invalide", mission=mission, mesures=[mesure]
    )

    mesure.refresh_from_db()
    assert mesure.incident_id == incident.pk
    assert list(incident.mesures.all()) == [mesure]


def test_signaler_incident_sans_mission(api_admin, mesure):
    """Une perte de communication peut survenir hors mission (RG11)."""
    incident = services.signaler_incident("perte_communication", mesures=[mesure])

    assert incident.mission is None
    assert api_admin.get(f"/api/v1/incidents/{incident.pk}/").status_code == 200
