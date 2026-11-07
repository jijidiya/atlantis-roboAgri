"""Logique métier des missions : création et transitions de statut."""

from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import TransitionInterdite

from .models import EtapeMission, Mission, StatutMission

TRANSITIONS = {
    StatutMission.EN_ATTENTE: {StatutMission.ENVOYEE},
    StatutMission.ENVOYEE: {StatutMission.RECUE, StatutMission.ECHOUEE},
    StatutMission.RECUE: {
        StatutMission.EN_COURS,
        StatutMission.TERMINEE,
        StatutMission.ECHOUEE,
        StatutMission.NON_CONFIRMEE,
    },
    StatutMission.EN_COURS: {
        StatutMission.TERMINEE,
        StatutMission.ECHOUEE,
        StatutMission.NON_CONFIRMEE,
    },
    StatutMission.TERMINEE: set(),
    StatutMission.ECHOUEE: set(),
    # L'utilisateur décide de relancer une mission non confirmée (protocole 9.5).
    StatutMission.NON_CONFIRMEE: {StatutMission.EN_ATTENTE},
}


@transaction.atomic
def creer_mission(duree_prevue_secondes, zones_ordonnees):
    """Crée une mission en attente avec ses étapes dans l'ordre donné.

    Args:
        duree_prevue_secondes: durée prévue de la mission.
        zones_ordonnees: zones à visiter, dans l'ordre.

    Returns:
        La mission créée.
    """
    mission = Mission.objects.create(duree_prevue_secondes=duree_prevue_secondes)
    EtapeMission.objects.bulk_create(
        [
            EtapeMission(mission=mission, zone=zone, ordre=ordre)
            for ordre, zone in enumerate(zones_ordonnees, start=1)
        ]
    )
    return mission


def changer_statut(mission, nouveau_statut, maintenant=None):
    """Applique une transition de statut, ou lève TransitionInterdite.

    Args:
        mission: la mission à modifier.
        nouveau_statut: le statut visé.
        maintenant: date de la transition (par défaut : l'heure actuelle).

    Returns:
        La mission mise à jour.
    """
    maintenant = maintenant or timezone.now()
    nouveau_statut = StatutMission(nouveau_statut)
    autorises = TRANSITIONS[StatutMission(mission.statut)]
    if nouveau_statut not in autorises:
        raise TransitionInterdite(f"{mission.statut} -> {nouveau_statut} est interdit.")
    mission.statut = nouveau_statut
    if nouveau_statut == StatutMission.RECUE:
        mission.date_recue = maintenant
    elif nouveau_statut == StatutMission.EN_COURS:
        mission.date_debut = maintenant
    elif nouveau_statut == StatutMission.TERMINEE:
        mission.date_fin = maintenant
    mission.save()
    return mission


def prendre_mission_pour_robot():
    """Retourne la mission à remettre au robot (la plus ancienne), ou None.

    Tant que la mission n'est pas confirmée reçue, elle est renvoyée à chaque appel :
    une réponse perdue ne fait jamais perdre la mission (protocole 5.3).
    """
    mission = (
        Mission.objects.filter(
            statut__in=[StatutMission.EN_ATTENTE, StatutMission.ENVOYEE]
        )
        .order_by("date_creation", "id")
        .first()
    )
    if mission is not None and mission.statut == StatutMission.EN_ATTENTE:
        changer_statut(mission, StatutMission.ENVOYEE)
    return mission


def marquer_recue(mission, maintenant=None):
    """Passe la mission à « recue » ; ne fait rien si elle l'est déjà."""
    if mission.statut == StatutMission.EN_ATTENTE:
        changer_statut(mission, StatutMission.ENVOYEE, maintenant)
    if mission.statut == StatutMission.ENVOYEE:
        changer_statut(mission, StatutMission.RECUE, maintenant)


def marquer_etape_atteinte(mission, maintenant=None):
    """Passe la mission à « en_cours » au premier message d'étape."""
    if mission.statut == StatutMission.RECUE:
        changer_statut(mission, StatutMission.EN_COURS, maintenant)


def terminer(mission, maintenant=None):
    """Passe la mission à « terminee » si elle était reçue ou en cours."""
    if mission.statut in (StatutMission.RECUE, StatutMission.EN_COURS):
        changer_statut(mission, StatutMission.TERMINEE, maintenant)


def faire_echouer(mission, maintenant=None):
    """Passe la mission à « echouee » (arrêt définitif signalé par le robot)."""
    if mission.statut in (
        StatutMission.ENVOYEE,
        StatutMission.RECUE,
        StatutMission.EN_COURS,
    ):
        changer_statut(mission, StatutMission.ECHOUEE, maintenant)


def marquer_non_confirmee(mission, maintenant=None):
    """Passe la mission à « non_confirmee » si elle était reçue ou en cours."""
    if mission.statut in (StatutMission.RECUE, StatutMission.EN_COURS):
        changer_statut(mission, StatutMission.NON_CONFIRMEE, maintenant)
