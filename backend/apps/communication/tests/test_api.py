"""Scénarios de docs/protocole.md (section 9), de bout en bout par l'API."""

import pytest
from rest_framework.test import APIClient

from apps.communication.models import EtatRobot, MessageRecu
from apps.irrigation.models import CodeIncident, Incident
from apps.mesures.models import MesureHumidite
from apps.missions import services as services_missions
from apps.missions.models import StatutMission

from .conftest import (
    ETAT,
    MESSAGES,
    MISSION,
    SYNC,
    construire_message,
    construire_mesure,
)

pytestmark = pytest.mark.django_db

ID_RECUE = "a41c09e2d7f3b856"
ID_ETAPE = "5be2f0137a9c4d68"
ID_MESURE = "c7d81a4f02e9b365"
ID_ETAT = "0e6b93d1c5a7f284"


def envoyer(client, corps, chemin=MESSAGES):
    return client.post(chemin, corps, format="json")


def test_cas_nominal(client_robot, zone, mission):
    reponse = client_robot.get(MISSION)
    assert reponse.status_code == 200
    assert reponse.json()["mission_id"] == mission.id
    assert reponse.json()["etapes"] == [{"etape": 1, "zone_id": zone.id}]
    # Tant que mission_recue n'est pas enregistré, la même mission est renvoyée.
    assert client_robot.get(MISSION).json()["mission_id"] == mission.id

    reponse = envoyer(
        client_robot,
        construire_message("mission_recue", 1, ID_RECUE, mission_id=mission.id),
    )
    assert reponse.json() == {"statut": "ok", "message_id": ID_RECUE}
    assert client_robot.get(MISSION).status_code == 204

    envoyer(
        client_robot,
        construire_message(
            "etape_atteinte",
            2,
            ID_ETAPE,
            mission_id=mission.id,
            etape=1,
            zone_id=zone.id,
        ),
    )
    mission.refresh_from_db()
    assert mission.statut == StatutMission.EN_COURS

    reponse = envoyer(client_robot, construire_mesure(zone, mission))
    assert reponse.json()["recommandation_arrosage"] == "arroser"

    envoyer(
        client_robot,
        construire_message(
            "changement_etat",
            9,
            ID_ETAT,
            mission_id=mission.id,
            etat_precedent="en_mesure",
            etat_nouveau="repos",
            mission_terminee=True,
        ),
    )
    mission.refresh_from_db()
    assert mission.statut == StatutMission.TERMINEE
    assert EtatRobot.objects.get().etat == "repos"


def test_doublon_meme_contenu_meme_reponse(client_robot, zone, mission):
    message = construire_mesure(zone, mission)
    premiere = envoyer(client_robot, message)
    seconde = envoyer(client_robot, message)
    assert seconde.status_code == 200
    assert seconde.json() == premiere.json()
    assert MesureHumidite.objects.count() == 1
    assert MessageRecu.objects.count() == 1


def test_doublon_contenu_different_donne_409(client_robot, zone, mission):
    envoyer(client_robot, construire_mesure(zone, mission))
    reponse = envoyer(client_robot, construire_mesure(zone, mission, humidite_pct=12.0))
    assert reponse.status_code == 409
    assert reponse.json()["code"] == "MESSAGE_CONFLIT"
    assert MesureHumidite.objects.get().humidite_pourcent == 34.5
    assert Incident.objects.filter(code=CodeIncident.MESSAGE_CONFLIT).count() == 1


def test_coupure_puis_renvoi_groupe(client_robot, zone, mission):
    client_robot.get(MISSION)
    messages = [
        construire_message("mission_recue", 4, ID_RECUE, mission_id=mission.id),
        construire_message(
            "etape_atteinte",
            5,
            ID_ETAPE,
            mission_id=mission.id,
            etape=1,
            zone_id=zone.id,
        ),
        construire_mesure(zone, mission, numero=6),
    ]
    reponse = envoyer(client_robot, {"messages": messages}, SYNC)
    assert reponse.status_code == 200
    assert [r["statut"] for r in reponse.json()["resultats"]] == ["ok", "ok", "ok"]
    mission.refresh_from_db()
    assert mission.statut == StatutMission.EN_COURS


def test_renvoi_groupe_une_erreur_n_arrete_pas_les_suivants(
    client_robot, zone, mission
):
    envoyer(client_robot, construire_mesure(zone, mission))
    lot = [
        construire_mesure(zone, mission, humidite_pct=12.0),
        construire_mesure(zone, mission, numero=4, identifiant="b82e51f7d0a3c496"),
    ]
    resultats = envoyer(client_robot, {"messages": lot}, SYNC).json()["resultats"]
    assert resultats[0] == {
        "message_id": ID_MESURE,
        "statut": "erreur",
        "code": "MESSAGE_CONFLIT",
    }
    assert resultats[1]["statut"] == "ok"


def test_renvoi_groupe_limite_a_20_messages(client_robot):
    reponse = envoyer(client_robot, {"messages": [{}] * 21}, SYNC)
    assert reponse.status_code == 400


def test_jeton_absent_donne_401(zone, mission):
    reponse = APIClient().post(
        MESSAGES, construire_mesure(zone, mission), format="json"
    )
    assert reponse.status_code == 401
    assert reponse.json()["code"] == "JETON_INVALIDE"
    assert MessageRecu.objects.count() == 0


def test_mauvais_jeton_donne_401(zone, mission):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token mauvais_jeton")
    assert client.get(MISSION).status_code == 401


def test_capteur_invalide_interdit_l_arrosage(client_robot, zone, mission):
    message = construire_mesure(
        zone,
        mission,
        identifiant="b82e51f7d0a3c496",
        humidite_pct=None,
        valeur_brute=0,
        valide=False,
    )
    reponse = envoyer(client_robot, message)
    assert reponse.json()["recommandation_arrosage"] == "interdite"
    assert Incident.objects.filter(code=CodeIncident.CAPTEUR_INVALIDE).count() == 1
    assert not MesureHumidite.objects.get().est_valide


def test_humidite_hors_plage_donne_422(client_robot, zone, mission):
    reponse = envoyer(
        client_robot, construire_mesure(zone, mission, humidite_pct=120.0)
    )
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "VALEUR_INCOHERENTE"
    assert MesureHumidite.objects.count() == 0 and MessageRecu.objects.count() == 0


def test_champ_manquant_donne_400(client_robot, zone, mission):
    message = construire_mesure(zone, mission)
    del message["zone_id"]
    assert envoyer(client_robot, message).status_code == 400


def test_json_invalide_donne_400(client_robot):
    reponse = client_robot.post(
        MESSAGES, data="{pas du json", content_type="application/json"
    )
    assert reponse.status_code == 400
    assert reponse.json()["code"] == "MESSAGE_INVALIDE"


def test_endpoint_etat_refuse_les_autres_types(client_robot, zone, mission):
    reponse = envoyer(client_robot, construire_mesure(zone, mission), ETAT)
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "TYPE_NON_ACCEPTE"
    changement = construire_message("changement_etat", 4, ID_ETAT, etat_nouveau="arret")
    assert envoyer(client_robot, changement, ETAT).status_code == 200
    assert EtatRobot.objects.get().etat == "arret"


def test_incident_bloquant_fait_echouer_la_mission(client_robot, mission):
    services_missions.marquer_recue(mission)
    services_missions.marquer_etape_atteinte(mission)
    incident = construire_message(
        "incident",
        7,
        "7a30c5e19b4d2f68",
        mission_id=mission.id,
        code="OBSTACLE",
        gravite="bloquant",
        description="Obstacle",
    )
    envoyer(client_robot, incident)
    mission.refresh_from_db()
    assert mission.statut == StatutMission.ECHOUEE


def test_incident_avertissement_ne_fait_pas_echouer_la_mission(client_robot, mission):
    services_missions.marquer_recue(mission)
    incident = construire_message(
        "incident",
        7,
        "7a30c5e19b4d2f68",
        mission_id=mission.id,
        code="FILE_PLEINE",
        gravite="avertissement",
        nb_perdus=12,
    )
    envoyer(client_robot, incident)
    mission.refresh_from_db()
    assert mission.statut == StatutMission.RECUE
    assert Incident.objects.get().nb_perdus == 12


def test_un_trou_de_numero_de_sequence_est_note(client_robot, zone, mission):
    envoyer(
        client_robot, construire_mesure(zone, mission, numero=1, identifiant="a" * 16)
    )
    envoyer(
        client_robot, construire_mesure(zone, mission, numero=3, identifiant="b" * 16)
    )
    trous = dict(MessageRecu.objects.values_list("num_sequence", "a_trou_sequence"))
    assert trous == {1: False, 3: True}
