"""Logique métier des missions. Toutes les transitions passent ici (section 8.4)."""

from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import TransitionInterdite

from .models import EtapeMission, Mission, StatutMission

TRANSITIONS = {
    StatutMission.PLANIFIEE: {StatutMission.EN_COURS},
    StatutMission.EN_COURS: {
        StatutMission.TERMINEE,
        StatutMission.INTERROMPUE,
        StatutMission.NON_CONFIRMEE,
    },
    StatutMission.INTERROMPUE: {StatutMission.PLANIFIEE},
    StatutMission.NON_CONFIRMEE: {StatutMission.PLANIFIEE},
    StatutMission.TERMINEE: set(),
}


@transaction.atomic
def planifier_mission(prevue_le, zones_ordonnees):
    mission = Mission.objects.create(prevue_le=prevue_le)
    EtapeMission.objects.bulk_create(
        [EtapeMission(mission=mission, zone=zone, ordre=i) for i, zone in enumerate(zones_ordonnees, 1)]
    )
    return mission


def changer_statut(mission, nouveau_statut):
    """Applique une transition, ou lève TransitionInterdite."""
    autorises = TRANSITIONS[StatutMission(mission.statut)]
    if nouveau_statut not in autorises:
        raise TransitionInterdite(f"{mission.statut} -> {nouveau_statut} est interdit.")
    mission.statut = nouveau_statut
    if nouveau_statut == StatutMission.EN_COURS:
        mission.debutee_le = timezone.now()
    elif nouveau_statut == StatutMission.TERMINEE:
        mission.terminee_le = timezone.now()
    mission.save()
    return mission
