import pytest
from django.utils import timezone

from apps.core.exceptions import TransitionInterdite
from apps.missions import services
from apps.missions.models import StatutMission
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


@pytest.fixture
def mission():
    parcelle = Parcelle.objects.create(nom="P1")
    zones = [Zone.objects.create(parcelle=parcelle, nom=f"Z{i}", ordre=i) for i in (1, 2)]
    return services.planifier_mission(timezone.now(), zones)


def test_planifier_cree_les_etapes_dans_l_ordre(mission):
    assert [e.ordre for e in mission.etapes.all()] == [1, 2]
    assert mission.statut == StatutMission.PLANIFIEE


def test_cycle_normal(mission):
    services.changer_statut(mission, StatutMission.EN_COURS)
    services.changer_statut(mission, StatutMission.TERMINEE)
    assert mission.debutee_le and mission.terminee_le


def test_transition_interdite(mission):
    with pytest.raises(TransitionInterdite):
        services.changer_statut(mission, StatutMission.TERMINEE)
