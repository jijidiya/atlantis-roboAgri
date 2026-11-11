"""Logique métier des missions (changements de statut, mission pour le robot).

Les transitions sont centralisées ici (architecture.pdf §4.1).
"""
from django.utils import timezone

from apps.core.exceptions import RessourceIntrouvable, TransitionInterdite

from .models import Etape, Mission

# statut actuel -> statuts atteignables
TRANSITIONS_AUTORISEES = {
    "planifiee": {"en_cours"},
    "en_cours": {"terminee", "interrompue", "non_confirmee"},
}


def changer_statut(mission, nouveau, maintenant=None):
    """Fait passer la mission au statut `nouveau`, ou lève TransitionInterdite.

    Demander le statut déjà atteint ne fait rien (le robot peut répéter un état).
    """
    if mission.statut == nouveau:
        return mission
    if nouveau not in TRANSITIONS_AUTORISEES.get(mission.statut, set()):
        raise TransitionInterdite(
            f"Impossible de passer la mission de « {mission.statut} » à « {nouveau} ».",
            {"statut_actuel": mission.statut, "statut_demande": nouveau},
        )
    maintenant = maintenant or timezone.now()
    champ_date = "date_debut" if nouveau == "en_cours" else "date_fin"
    mission.statut = nouveau
    setattr(mission, champ_date, maintenant)
    mission.save(update_fields=["statut", champ_date])
    return mission


def appliquer_etat_robot(mission, etat, maintenant=None):
    """Applique un état annoncé par le robot (en_cours, terminee, interrompue)."""
    return changer_statut(mission, etat, maintenant)


def mission_suivante():
    """Plus ancienne mission planifiée, ou None : c'est ce que le robot vient chercher."""
    return (
        Mission.objects.filter(statut="planifiee")
        .prefetch_related("etapes")
        .order_by("date_creation")
        .first()
    )


def trouver_etape(mission, numero_ordre):
    """Étape de la mission portant ce numéro d'ordre (404 sinon)."""
    etape = (
        Etape.objects.select_related("zone", "mission")
        .filter(mission=mission, numero_ordre=numero_ordre)
        .first()
    )
    if etape is None:
        raise RessourceIntrouvable(
            f"La mission {mission.pk} n'a pas d'étape numéro {numero_ordre}.",
            {"etape": numero_ordre},
        )
    return etape


def terminer_etape(etape, maintenant=None):
    """Marque l'étape comme terminée (ses 9 mesures sont arrivées)."""
    maintenant = maintenant or timezone.now()
    if etape.date_debut is None:
        etape.date_debut = maintenant
    etape.date_fin = maintenant
    etape.statut = "terminee"
    etape.save(update_fields=["statut", "date_debut", "date_fin"])
    return etape