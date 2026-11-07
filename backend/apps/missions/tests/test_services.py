import pytest

from apps.core.exceptions import TransitionInterdite
from apps.missions import services
from apps.missions.models import StatutMission
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


def test_creer_mission_numerote_les_etapes_dans_l_ordre():
    parcelle = Parcelle.objects.create(nom="P")
    zones = [
        Zone.objects.create(parcelle=parcelle, nom=f"Z{i}", ordre=i) for i in (1, 2)
    ]
    mission = services.creer_mission(300, list(reversed(zones)))
    assert [(e.ordre, e.zone) for e in mission.etapes.all()] == [
        (1, zones[1]),
        (2, zones[0]),
    ]
    assert mission.statut == StatutMission.EN_ATTENTE


def test_la_mission_est_renvoyee_tant_qu_elle_n_est_pas_recue(mission):
    premiere = services.prendre_mission_pour_robot()
    assert premiere.statut == StatutMission.ENVOYEE
    assert services.prendre_mission_pour_robot().id == mission.id
    services.marquer_recue(mission)
    assert services.prendre_mission_pour_robot() is None


def test_cycle_normal(mission):
    services.marquer_recue(mission)
    services.marquer_etape_atteinte(mission)
    assert mission.statut == StatutMission.EN_COURS and mission.date_debut
    services.terminer(mission)
    assert mission.statut == StatutMission.TERMINEE and mission.date_fin


def test_transition_interdite(mission):
    with pytest.raises(TransitionInterdite):
        services.changer_statut(mission, StatutMission.TERMINEE)


def test_une_mission_non_confirmee_peut_etre_relancee(mission):
    services.marquer_recue(mission)
    services.marquer_non_confirmee(mission)
    services.changer_statut(mission, StatutMission.EN_ATTENTE)
    assert mission.statut == StatutMission.EN_ATTENTE


def test_faire_echouer_une_mission_en_cours(mission):
    services.marquer_recue(mission)
    services.marquer_etape_atteinte(mission)
    services.faire_echouer(mission)
    assert mission.statut == StatutMission.ECHOUEE
