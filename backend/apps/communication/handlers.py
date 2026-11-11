"""Orchestrateur : point d'entrée UNIQUE pour tout message venant du robot.

La vue HTTP (api.py) et, plus tard, l'abonné MQTT appellent la même fonction :
le transport change, pas le traitement (architecture.pdf §4.3).
"""
from dataclasses import asdict, dataclass, field

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.exceptions import DonneesInvalides, RessourceIntrouvable
from apps.incidents import services as incidents_services
from apps.irrigation import services as irrigation_services
from apps.irrigation.models import Decision
from apps.mesures import services as mesures_services
from apps.mesures.models import Mesure
from apps.missions import services as missions_services
from apps.missions.models import Mission

from . import protocole
from .models import Message


@dataclass
class ResultatTraitement:
    deja_recu: bool
    message_id: str
    mesures: list = field(default_factory=list)     # identifiants des mesures créées
    incidents: list = field(default_factory=list)   # identifiants des incidents créés
    decisions: list = field(default_factory=list)   # identifiants des décisions créées
    valide: bool | None = None                      # None si le message ne porte pas de mesure

    def en_dict(self):
        return asdict(self)


def traiter_message(donnees, maintenant=None) -> ResultatTraitement:
    """Traite un message du robot. Idempotent : un même message_id n'agit qu'une fois (RG10)."""
    maintenant = maintenant or timezone.now()
    try:
        message = protocole.valider(donnees)
    except protocole.ProtocoleInvalide as erreur:
        raise DonneesInvalides("Message du robot invalide.", {erreur.champ: [erreur.message]})

    mission = Mission.objects.filter(pk=message.mission).first()
    if mission is None:
        raise RessourceIntrouvable(f"La mission {message.mission} n'existe pas.", {"mission": message.mission})

    with transaction.atomic():
        # L'unicité est garantie par la clé primaire en base, pas par un test préalable :
        # deux envois simultanés du même message ne peuvent pas passer tous les deux.
        try:
            with transaction.atomic():
                enregistre = Message.objects.create(
                    message_id=message.message_id,
                    num_sequence=message.num_sequence,
                    type_message=message.type,
                    contenu=donnees,
                    date_heure=maintenant,   # heure de RÉCEPTION ; celle du robot est dans le contenu
                    mission=mission,
                )
        except IntegrityError:
            if Message.objects.filter(pk=message.message_id).exists():
                return _deja_recu(message.message_id)
            raise

        if message.type == "mesure":
            return _traiter_mesure(message, enregistre, mission, maintenant)
        if message.type == "etat":
            missions_services.appliquer_etat_robot(mission, message.etat, maintenant)
            return ResultatTraitement(False, message.message_id)
        incident = incidents_services.signaler_incident(
            message.type_incident, mission=mission, date_incident=message.horodatage
        )
        return ResultatTraitement(False, message.message_id, incidents=[incident.pk])


def _traiter_mesure(message, enregistre, mission, maintenant):
    """Enregistrer les mesures (validation) puis évaluer la zone (décision, incident)."""
    etape = missions_services.trouver_etape(mission, message.etape)
    mesures = mesures_services.enregistrer_mesures(enregistre, etape, message.lectures, maintenant)
    missions_services.terminer_etape(etape, maintenant)
    decision, incident = irrigation_services.evaluer_zone(etape, mesures, maintenant)
    return ResultatTraitement(
        deja_recu=False,
        message_id=message.message_id,
        mesures=[m.pk for m in mesures],
        incidents=[incident.pk] if incident else [],
        decisions=[decision.pk],
        valide=all(m.statut == "valide" for m in mesures),
    )


def _deja_recu(message_id):
    """Message déjà connu : on renvoie les identifiants créés la première fois."""
    mesures = list(Mesure.objects.filter(message_id=message_id).order_by("mesure_id"))
    return ResultatTraitement(
        deja_recu=True,
        message_id=message_id,
        mesures=[m.pk for m in mesures],
        incidents=sorted({m.incident_id for m in mesures if m.incident_id}),
        decisions=list(
            Decision.objects.filter(analyse__mesures__message_id=message_id)
            .distinct().values_list("decision_id", flat=True)
        ),
        valide=all(m.statut == "valide" for m in mesures) if mesures else None,
    )