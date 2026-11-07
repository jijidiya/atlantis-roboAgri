"""L'orchestrateur : seul endroit qui connaît tout l'enchaînement.

Utilisé par les vues HTTP (api.py) ET par l'abonné MQTT (mqtt_client.py).
Les règles viennent de docs/protocole.md.
"""

from dataclasses import dataclass

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from apps.core.exceptions import DonneesInvalides, TransitionInterdite
from apps.irrigation import services as services_irrigation
from apps.irrigation.models import CodeIncident, GraviteIncident
from apps.mesures import services as services_mesures
from apps.mesures.validation import valider_humidite
from apps.missions import services as services_missions
from apps.missions.models import Mission, StatutMission
from apps.parcelles.models import Zone

from . import protocole
from .models import EtatRobot, MessageRecu


@dataclass
class ResultatTraitement:
    """Réponse à renvoyer au robot : code HTTP et corps JSON."""

    code_http: int
    corps: dict


def _erreur(code_http, code, detail):
    return ResultatTraitement(
        code_http, protocole.construire_reponse_erreur(code, detail)
    )


def obtenir_mission_pour_robot():
    """Retourne le message « mission » à remettre au robot, ou None (HTTP 204)."""
    mission = services_missions.prendre_mission_pour_robot()
    if mission is None:
        return None
    etapes = [(etape.ordre, etape.zone_id) for etape in mission.etapes.all()]
    return protocole.construire_mission(
        mission.id, mission.date_creation, mission.duree_prevue_secondes, etapes
    )


def traiter_message(donnees, types_acceptes=None, maintenant=None):
    """Point d'entrée UNIQUE pour tout message venant du robot (HTTP ou MQTT).

    Args:
        donnees: le corps JSON décodé.
        types_acceptes: types de message autorisés sur ce point d'entrée, ou None.
        maintenant: date de réception (par défaut : l'heure actuelle).

    Returns:
        Un ResultatTraitement (200, 400, 409 ou 422).
    """
    maintenant = maintenant or timezone.now()
    try:
        message = protocole.valider_message(donnees)
    except protocole.MessageInvalide as erreur:
        return _erreur(400, protocole.CODE_MESSAGE_INVALIDE, str(erreur))
    if types_acceptes is not None and message.type not in types_acceptes:
        return _erreur(
            422,
            protocole.CODE_TYPE_NON_ACCEPTE,
            f"type non accepté ici : {message.type}",
        )

    # L'unicité est garantie par la contrainte en base, pas par un test préalable :
    # deux envois simultanés du même message ne peuvent pas passer tous les deux.
    try:
        with transaction.atomic():
            enregistrement = _enregistrer_message(message)
            corps = _appliquer_message(message, maintenant)
            enregistrement.reponse = corps
            enregistrement.save(update_fields=["reponse"])
    except IntegrityError:
        existant = MessageRecu.objects.filter(message_id=message.message_id).first()
        if existant is None:
            raise
        return _traiter_doublon(existant, message, maintenant)
    except (DonneesInvalides, TransitionInterdite) as erreur:
        return _erreur(422, protocole.CODE_VALEUR_INCOHERENTE, str(erreur))
    return ResultatTraitement(200, corps)


def traiter_lot(donnees, maintenant=None):
    """Traite un renvoi groupé après une coupure (POST /api/robot/messages/sync).

    Chaque message est traité dans l'ordre, avec les règles du POST simple ;
    une erreur sur l'un n'empêche pas les suivants.
    """
    messages = donnees.get("messages") if isinstance(donnees, dict) else None
    if not isinstance(messages, list):
        return _erreur(400, protocole.CODE_MESSAGE_INVALIDE, "champ messages manquant")
    if len(messages) > protocole.TAILLE_MAX_LOT:
        return _erreur(
            400,
            protocole.CODE_MESSAGE_INVALIDE,
            f"{protocole.TAILLE_MAX_LOT} messages au maximum par appel",
        )
    resultats = []
    for message_brut in messages:
        resultat = traiter_message(message_brut, maintenant=maintenant)
        identifiant = (
            message_brut.get("message_id") if isinstance(message_brut, dict) else None
        )
        entree = {"message_id": identifiant}
        if resultat.code_http == 200:
            entree["statut"] = "ok"
        else:
            entree["statut"] = "erreur"
            entree["code"] = resultat.corps["code"]
        resultats.append(entree)
    return ResultatTraitement(200, {"resultats": resultats})


def detecter_missions_non_confirmees(maintenant=None):
    """Passe à « non_confirmee » les missions silencieuses ou trop longues (6.6).

    Returns:
        La liste des couples (mission, cause) qui viennent de changer de statut.
    """
    maintenant = maintenant or timezone.now()
    dernier_message = MessageRecu.objects.aggregate(date=Max("date_reception"))["date"]
    changements = []
    missions = Mission.objects.filter(
        statut__in=[StatutMission.RECUE, StatutMission.EN_COURS]
    )
    for mission in missions:
        dates = [d for d in (dernier_message, mission.date_recue) if d is not None]
        if not dates:
            continue
        cause = protocole.evaluer_non_confirmation(
            maintenant=maintenant,
            derniere_activite=max(dates),
            date_recue=mission.date_recue or max(dates),
            duree_prevue_secondes=mission.duree_prevue_secondes,
            duree_cycle_secondes=settings.ROBOT_DUREE_CYCLE_SECONDES,
            cycles_silence=settings.ROBOT_CYCLES_SILENCE,
            facteur_plafond=settings.ROBOT_FACTEUR_PLAFOND,
        )
        if cause is None:
            continue
        with transaction.atomic():
            services_missions.marquer_non_confirmee(mission, maintenant)
            services_irrigation.signaler_incident(
                CodeIncident.MISSION_NON_CONFIRMEE,
                GraviteIncident.AVERTISSEMENT,
                description=f"cause : {cause}",
                mission=mission,
                date_incident=maintenant,
            )
        changements.append((mission, cause))
    return changements


def _enregistrer_message(message):
    """Crée la trace du message ; lève IntegrityError si message_id existe déjà."""
    a_trou = False
    if message.num_sequence is not None:
        precedent = MessageRecu.objects.aggregate(numero=Max("num_sequence"))["numero"]
        a_trou = precedent is not None and message.num_sequence > precedent + 1
    return MessageRecu.objects.create(
        message_id=message.message_id,
        num_sequence=message.num_sequence,
        type=message.type,
        contenu=message.donnees,
        a_trou_sequence=a_trou,
    )


def _traiter_doublon(existant, message, maintenant):
    """Même message_id : même contenu = même réponse, contenu différent = 409."""
    if existant.contenu == message.donnees:
        return ResultatTraitement(200, existant.reponse)
    services_irrigation.signaler_incident(
        CodeIncident.MESSAGE_CONFLIT,
        GraviteIncident.AVERTISSEMENT,
        description=f"message_id {message.message_id} reçu avec un contenu différent",
        date_incident=maintenant,
    )
    return _erreur(
        409,
        protocole.CODE_MESSAGE_CONFLIT,
        "message_id déjà reçu avec un contenu différent",
    )


def _obtenir_mission(mission_id):
    mission = Mission.objects.filter(pk=mission_id).first()
    if mission is None:
        raise DonneesInvalides(f"mission_id inconnu : {mission_id}")
    return mission


def _obtenir_zone(zone_id):
    zone = Zone.objects.filter(pk=zone_id).first()
    if zone is None:
        raise DonneesInvalides(f"zone_id inconnu : {zone_id}")
    return zone


def _appliquer_message(message, maintenant):
    """Enregistre les effets d'un message ; retourne le corps de la réponse."""
    donnees = message.donnees
    date = message.date_horodatage or maintenant
    if message.type == "mission_recue":
        services_missions.marquer_recue(_obtenir_mission(donnees["mission_id"]), date)
        return protocole.construire_reponse_ok(message.message_id)
    if message.type == "etape_atteinte":
        return _traiter_etape_atteinte(message, date)
    if message.type == "mesure":
        return _traiter_mesure(message, date, message.date_horodatage is None)
    if message.type == "changement_etat":
        return _traiter_changement_etat(message, date)
    return _traiter_incident(message, date)


def _traiter_etape_atteinte(message, date):
    donnees = message.donnees
    mission = _obtenir_mission(donnees["mission_id"])
    zone = _obtenir_zone(donnees["zone_id"])
    if not mission.etapes.filter(ordre=donnees["etape"], zone=zone).exists():
        raise DonneesInvalides(f"étape inconnue : {donnees['etape']} (zone {zone.id})")
    services_missions.marquer_etape_atteinte(mission, date)
    return protocole.construire_reponse_ok(message.message_id)


def _traiter_mesure(message, date, est_date_approximative):
    donnees = message.donnees
    mission = _obtenir_mission(donnees["mission_id"])
    zone = _obtenir_zone(donnees["zone_id"])
    controle = valider_humidite(donnees["humidite_pct"], donnees["valide"])
    if controle.motif == "hors_plage":
        raise DonneesInvalides(
            f"humidite_pct hors de 0 à 100 : {donnees['humidite_pct']}"
        )
    mesure = services_mesures.enregistrer_mesure(
        zone=zone,
        mission=mission,
        num_sequence=message.num_sequence,
        humidite_pourcent=donnees["humidite_pct"],
        valeur_brute=donnees["valeur_brute"],
        est_valide_capteur=donnees["valide"],
        date_mesure=date,
        est_date_approximative=est_date_approximative,
        uptime_ms=message.uptime_ms,
    )
    irrigation = services_irrigation.evaluer_mesure(mesure)
    recommandation = protocole.convertir_decision_en_recommandation(irrigation.decision)
    return protocole.construire_reponse_ok(message.message_id, recommandation)


def _traiter_changement_etat(message, date):
    donnees = message.donnees
    EtatRobot.objects.update_or_create(
        pk=1, defaults={"etat": donnees["etat_nouveau"], "date_mise_a_jour": date}
    )
    if donnees.get("mission_terminee") is True:
        if donnees.get("mission_id") is None:
            raise DonneesInvalides("mission_terminee exige un mission_id")
        services_missions.terminer(_obtenir_mission(donnees["mission_id"]), date)
    return protocole.construire_reponse_ok(message.message_id)


def _traiter_incident(message, date):
    donnees = message.donnees
    mission = None
    if donnees.get("mission_id") is not None:
        mission = _obtenir_mission(donnees["mission_id"])
    zone = None
    if donnees.get("zone_id") is not None:
        zone = _obtenir_zone(donnees["zone_id"])
    services_irrigation.signaler_incident(
        donnees["code"],
        donnees["gravite"],
        description=donnees.get("description", ""),
        zone=zone,
        mission=mission,
        nb_perdus=donnees.get("nb_perdus"),
        date_incident=date,
    )
    # Seul un incident bloquant fait passer la mission à « echouee ».
    if donnees["gravite"] == GraviteIncident.BLOQUANT and mission is not None:
        services_missions.faire_echouer(mission, date)
    return protocole.construire_reponse_ok(message.message_id)
