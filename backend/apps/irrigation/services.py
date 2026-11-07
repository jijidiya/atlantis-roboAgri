"""Logique métier de l'irrigation et création des incidents."""

from django.utils import timezone

from . import decision, securite
from .models import CodeIncident, GraviteIncident, Incident, Irrigation, TypeIrrigation


def signaler_incident(
    code,
    gravite=GraviteIncident.AVERTISSEMENT,
    description="",
    zone=None,
    mission=None,
    nb_perdus=None,
    date_incident=None,
):
    """Crée un incident. Seuls irrigation et communication appellent cette fonction.

    Args:
        code: un CodeIncident.
        gravite: une GraviteIncident.
        description: texte libre.
        zone: zone concernée, si connue.
        mission: mission concernée, si connue.
        nb_perdus: nombre de messages perdus (code FILE_PLEINE).
        date_incident: date de l'incident (par défaut : maintenant).

    Returns:
        L'incident créé.
    """
    return Incident.objects.create(
        code=code,
        gravite=gravite,
        description=description,
        zone=zone,
        mission=mission,
        nb_perdus=nb_perdus,
        date_incident=date_incident or timezone.now(),
    )


def evaluer_mesure(mesure):
    """Produit la recommandation d'irrigation d'une mesure.

    Une mesure invalide donne une décision « invalide » et un incident
    CAPTEUR_INVALIDE.

    Returns:
        L'Irrigation (type recommandation) créée.
    """
    etat = decision.decider(
        mesure.humidite_pourcent,
        mesure.zone.seuil_humidite_pourcent,
        mesure.est_valide,
    )
    if etat == decision.INVALIDE:
        signaler_incident(
            CodeIncident.CAPTEUR_INVALIDE,
            GraviteIncident.AVERTISSEMENT,
            description=mesure.motif_invalidite,
            zone=mesure.zone,
            mission=mesure.mission,
            date_incident=mesure.date_mesure,
        )
    return Irrigation.objects.create(
        zone=mesure.zone,
        mesure=mesure,
        type=TypeIrrigation.RECOMMANDATION,
        decision=etat,
    )


def declencher_irrigation(mesure, a_obstacle, batterie_pourcent, duree_secondes):
    """Enregistre une intervention d'irrigation si la sécurité l'autorise.

    Returns:
        L'Irrigation (type intervention) créée, ou None si la sécurité refuse.
    """
    controle = securite.verifier(mesure.est_valide, a_obstacle, batterie_pourcent)
    if not controle.est_autorise:
        return None
    return Irrigation.objects.create(
        zone=mesure.zone,
        mesure=mesure,
        type=TypeIrrigation.INTERVENTION,
        decision=decision.INSUFFISANTE,
        duree_secondes=duree_secondes,
    )
