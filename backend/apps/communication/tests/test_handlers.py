from datetime import datetime, timedelta, timezone

import pytest
from django.core.management import call_command

from apps.communication import handlers
from apps.communication.models import MessageRecu
from apps.irrigation.models import CodeIncident, Incident
from apps.missions import services as services_missions
from apps.missions.models import StatutMission

from .conftest import construire_message

pytestmark = pytest.mark.django_db

T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=timezone.utc)


def test_message_mal_forme_donne_400():
    resultat = handlers.traiter_message({"n_importe": "quoi"})
    assert resultat.code_http == 400
    assert resultat.corps["code"] == "MESSAGE_INVALIDE"


def test_mission_inconnue_donne_422_et_rien_n_est_enregistre():
    message = construire_message("mission_recue", 1, "a41c09e2d7f3b856", mission_id=999)
    resultat = handlers.traiter_message(message)
    assert resultat.code_http == 422
    assert MessageRecu.objects.count() == 0


def test_sans_horodatage_la_date_de_reception_est_utilisee(zone, mission):
    message = construire_message(
        "mesure",
        1,
        "c7d81a4f02e9b365",
        mission_id=mission.id,
        zone_id=zone.id,
        humidite_pct=30.0,
        valeur_brute=2000,
        valide=True,
    )
    message["horodatage"] = None
    handlers.traiter_message(message, maintenant=T0)
    mesure = zone.mesures.get()
    assert mesure.date_mesure == T0 and mesure.est_date_approximative


def test_silence_du_robot_rend_la_mission_non_confirmee(mission):
    services_missions.marquer_recue(mission, T0)
    assert handlers.detecter_missions_non_confirmees(T0 + timedelta(seconds=29)) == []
    changements = handlers.detecter_missions_non_confirmees(T0 + timedelta(seconds=30))
    assert [(m.id, cause) for m, cause in changements] == [(mission.id, "silence")]
    mission.refresh_from_db()
    assert mission.statut == StatutMission.NON_CONFIRMEE
    incident = Incident.objects.get(code=CodeIncident.MISSION_NON_CONFIRMEE)
    assert incident.description == "cause : silence"


def test_plafond_global_rend_la_mission_non_confirmee(mission):
    services_missions.marquer_recue(mission, T0)
    MessageRecu.objects.create(message_id="a41c09e2d7f3b856", type="mesure", contenu={})
    MessageRecu.objects.update(date_reception=T0 + timedelta(seconds=1795))
    changements = handlers.detecter_missions_non_confirmees(
        T0 + timedelta(seconds=1801)
    )
    assert [cause for _, cause in changements] == ["plafond"]


def test_une_mission_deja_terminee_n_est_pas_touchee(mission):
    services_missions.marquer_recue(mission, T0)
    services_missions.terminer(mission, T0)
    assert handlers.detecter_missions_non_confirmees(T0 + timedelta(hours=2)) == []


def test_commande_detecter_missions_non_confirmees(capsys):
    call_command("detecter_missions_non_confirmees")
    assert "0 mission(s)" in capsys.readouterr().out
