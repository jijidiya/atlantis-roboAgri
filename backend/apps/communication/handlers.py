"""L'orchestrateur : seul endroit qui connaît tout l'enchaînement.

Utilisé par la vue HTTP (api.py) ET par l'abonné MQTT (mqtt_client.py).
"""

from dataclasses import dataclass

from django.db import IntegrityError, transaction

from apps.irrigation import services as irrigation
from apps.irrigation.services import signaler_incident
from apps.mesures import services as mesures
from apps.missions.models import Mission
from apps.parcelles.models import Zone

from . import protocole
from .models import MessageRecu


@dataclass
class ResultatTraitement:
    statut: str  # "traite", "doublon" ou "rejete"
    detail: str = ""


def traiter_message(donnees: dict) -> ResultatTraitement:
    """Point d'entrée UNIQUE pour tout message venant du robot (HTTP ou MQTT)."""
    try:
        message = protocole.valider(donnees)
    except protocole.MessageInvalide as erreur:
        signaler_incident("message_invalide", str(erreur))
        return ResultatTraitement("rejete", str(erreur))

    # L'unicité est garantie par la contrainte en base, pas par un test préalable.
    try:
        with transaction.atomic():
            MessageRecu.objects.create(identifiant=message.identifiant, contenu=donnees)
            zone = Zone.objects.get(pk=message.zone_id)
            mission = Mission.objects.filter(pk=message.mission_id).first()
            mesure = mesures.enregistrer_mesure(
                zone, message.sequence, message.humidite, message.mesuree_le, mission
            )
            irrigation.evaluer_mesure(mesure)
    except IntegrityError:
        return ResultatTraitement("doublon", message.identifiant)
    except Zone.DoesNotExist:
        signaler_incident("zone_inconnue", f"zone_id={message.zone_id}")
        return ResultatTraitement("rejete", "zone_inconnue")
    return ResultatTraitement("traite", message.identifiant)
