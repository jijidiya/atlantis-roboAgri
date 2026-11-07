from . import decision, securite
from .models import Incident, Irrigation, TypeIrrigation


def signaler_incident(type, description="", zone=None, mission=None):
    return Incident.objects.create(type=type, description=description, zone=zone, mission=mission)


def evaluer_mesure(mesure):
    """Recommandation d'irrigation à partir d'une mesure. Un cas invalide devient un incident."""
    etat = decision.decider(mesure.humidite, mesure.zone.seuil_humidite, mesure.valide)
    if etat == "invalide":
        signaler_incident(
            "mesure_invalide", mesure.motif_invalidite, zone=mesure.zone, mission=mesure.mission
        )
    return Irrigation.objects.create(
        zone=mesure.zone, mesure=mesure, type=TypeIrrigation.RECOMMANDATION, decision=etat
    )


def declencher_arrosage(mesure, obstacle_detecte, batterie_pct, duree_secondes):
    """Intervention réelle : bloquée si la sécurité ou la mesure l'interdit."""
    controle = securite.verifier(mesure.valide, obstacle_detecte, batterie_pct)
    if not controle.autorise:
        signaler_incident(
            "arrosage_refuse", controle.motif, zone=mesure.zone, mission=mesure.mission
        )
        return None
    return Irrigation.objects.create(
        zone=mesure.zone,
        mesure=mesure,
        type=TypeIrrigation.INTERVENTION,
        decision="insuffisante",
        duree_secondes=duree_secondes,
    )
