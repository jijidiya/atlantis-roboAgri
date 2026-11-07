"""Module PUR : format des messages du robot (docs/protocole.md). Sans Django.

Les noms de champs JSON (``humidite_pct``, ``num_sequence``,
``recommandation_arrosage``) sont ceux du contrat robot-application :
ils ne se renomment pas.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

TYPES_ROBOT = (
    "mission_recue",
    "etape_atteinte",
    "mesure",
    "changement_etat",
    "incident",
)
ETATS_ROBOT = (
    "repos",
    "en_deplacement",
    "en_mesure",
    "arret",
    "erreur",
    "hors_ligne",
)
GRAVITES = ("info", "avertissement", "bloquant")
CODES_INCIDENT_ROBOT = ("OBSTACLE", "FILE_PLEINE", "NTP_ECHEC")
CHAMPS_COMMUNS = ("message_id", "num_sequence", "type", "horodatage", "uptime_ms")
TAILLE_MAX_LOT = 20

CODE_JETON_INVALIDE = "JETON_INVALIDE"
CODE_MESSAGE_INVALIDE = "MESSAGE_INVALIDE"
CODE_VALEUR_INCOHERENTE = "VALEUR_INCOHERENTE"
CODE_TYPE_NON_ACCEPTE = "TYPE_NON_ACCEPTE"
CODE_MESSAGE_CONFLIT = "MESSAGE_CONFLIT"

MODELE_MESSAGE_ID = re.compile(r"[0-9a-f]{16}")

RECOMMANDATIONS = {
    "insuffisante": "arroser",
    "suffisante": "ne_pas_arroser",
    "invalide": "interdite",
}


class MessageInvalide(ValueError):
    """Message mal formé : JSON invalide ou champ obligatoire manquant (HTTP 400)."""


@dataclass(frozen=True)
class Message:
    """Message du robot, validé. `donnees` garde le corps complet d'origine."""

    message_id: str
    num_sequence: int | None
    type: str
    date_horodatage: datetime | None
    uptime_ms: int | None
    donnees: dict


def _est_entier(valeur):
    return isinstance(valeur, int) and not isinstance(valeur, bool)


def _est_nombre(valeur):
    return isinstance(valeur, (int, float)) and not isinstance(valeur, bool)


def _exiger(donnees, champ):
    if champ not in donnees:
        raise MessageInvalide(f"champ obligatoire manquant : {champ}")
    return donnees[champ]


def _exiger_entier(donnees, champ, minimum=0):
    valeur = _exiger(donnees, champ)
    if not _est_entier(valeur) or valeur < minimum:
        raise MessageInvalide(f"{champ} doit être un entier >= {minimum}")
    return valeur


def _verifier_entier_optionnel(donnees, champ):
    valeur = donnees.get(champ)
    if valeur is not None and not _est_entier(valeur):
        raise MessageInvalide(f"{champ} doit être un entier")


def _verifier_choix(donnees, champ, choix, obligatoire=True):
    if obligatoire:
        valeur = _exiger(donnees, champ)
    else:
        valeur = donnees.get(champ)
        if valeur is None:
            return
    if valeur not in choix:
        raise MessageInvalide(f"{champ} doit valoir l'une de ces valeurs : {choix}")


def _lire_horodatage(valeur):
    """Convertit un horodatage ISO 8601 en date UTC ; None reste None."""
    if valeur is None:
        return None
    if not isinstance(valeur, str):
        raise MessageInvalide("horodatage doit être un texte ISO 8601 ou null")
    try:
        date = datetime.fromisoformat(valeur)
    except ValueError:
        raise MessageInvalide("horodatage n'est pas au format ISO 8601") from None
    if date.tzinfo is None:
        raise MessageInvalide("horodatage doit indiquer le fuseau (suffixe Z)")
    return date.astimezone(timezone.utc)


def _valider_champs_du_type(type_message, donnees):
    """Vérifie les champs propres à chaque type de message (section 4)."""
    if type_message == "mission_recue":
        _exiger_entier(donnees, "mission_id")
    elif type_message == "etape_atteinte":
        _exiger_entier(donnees, "mission_id")
        _exiger_entier(donnees, "etape", minimum=1)
        _exiger_entier(donnees, "zone_id")
    elif type_message == "mesure":
        _exiger_entier(donnees, "mission_id")
        _exiger_entier(donnees, "zone_id")
        _exiger_entier(donnees, "valeur_brute")
        if not isinstance(_exiger(donnees, "valide"), bool):
            raise MessageInvalide("valide doit valoir true ou false")
        humidite = _exiger(donnees, "humidite_pct")
        if humidite is not None and not _est_nombre(humidite):
            raise MessageInvalide("humidite_pct doit être un nombre ou null")
    elif type_message == "changement_etat":
        _verifier_choix(donnees, "etat_nouveau", ETATS_ROBOT)
        _verifier_choix(donnees, "etat_precedent", ETATS_ROBOT, obligatoire=False)
        _verifier_entier_optionnel(donnees, "mission_id")
        terminee = donnees.get("mission_terminee")
        if terminee is not None and not isinstance(terminee, bool):
            raise MessageInvalide("mission_terminee doit valoir true ou false")
    elif type_message == "incident":
        _verifier_choix(donnees, "code", CODES_INCIDENT_ROBOT)
        _verifier_choix(donnees, "gravite", GRAVITES)
        _verifier_entier_optionnel(donnees, "mission_id")
        _verifier_entier_optionnel(donnees, "zone_id")
        _verifier_entier_optionnel(donnees, "nb_perdus")
        description = donnees.get("description")
        if description is not None and not isinstance(description, str):
            raise MessageInvalide("description doit être un texte")


def valider_message(donnees):
    """Valide la structure d'un message envoyé par le robot.

    Args:
        donnees: le corps JSON décodé.

    Returns:
        Le Message validé.

    Raises:
        MessageInvalide: champ manquant, mauvais type ou valeur hors liste.
    """
    if not isinstance(donnees, dict):
        raise MessageInvalide("le message doit être un objet JSON")
    for champ in CHAMPS_COMMUNS:
        _exiger(donnees, champ)

    message_id = donnees["message_id"]
    if not isinstance(message_id, str) or not MODELE_MESSAGE_ID.fullmatch(message_id):
        raise MessageInvalide("message_id : 16 caractères hexadécimaux en minuscules")

    type_message = donnees["type"]
    if type_message not in TYPES_ROBOT:
        raise MessageInvalide(
            f"type inconnu ou non envoyé par le robot : {type_message}"
        )

    # Le Last Will MQTT est préparé avant la panne : numéro et uptime valent null.
    est_dernier_voeu = (
        type_message == "changement_etat"
        and donnees.get("etat_nouveau") == "hors_ligne"
    )
    num_sequence = donnees["num_sequence"]
    if not (est_dernier_voeu and num_sequence is None):
        num_sequence = _exiger_entier(donnees, "num_sequence")
    uptime_ms = donnees["uptime_ms"]
    if not (est_dernier_voeu and uptime_ms is None):
        uptime_ms = _exiger_entier(donnees, "uptime_ms")

    date_horodatage = _lire_horodatage(donnees["horodatage"])
    _valider_champs_du_type(type_message, donnees)
    return Message(
        message_id=message_id,
        num_sequence=num_sequence,
        type=type_message,
        date_horodatage=date_horodatage,
        uptime_ms=uptime_ms,
        donnees=dict(donnees),
    )


def construire_reponse_ok(message_id, recommandation_arrosage=None):
    """Construit la réponse à un message accepté (section 4.8)."""
    reponse = {"statut": "ok", "message_id": message_id}
    if recommandation_arrosage is not None:
        reponse["recommandation_arrosage"] = recommandation_arrosage
    return reponse


def construire_reponse_erreur(code, detail):
    """Construit la réponse à une erreur (section 4.8)."""
    return {"statut": "erreur", "code": code, "detail": detail}


def convertir_decision_en_recommandation(decision):
    """Traduit une décision d'irrigation en valeur du contrat (section 4.8)."""
    return RECOMMANDATIONS[decision]


def formater_date_iso_utc(date):
    """Écrit une date au format du protocole : 2026-11-03T10:15:30Z."""
    return date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def construire_mission(mission_id, date_creation, duree_prevue_secondes, etapes):
    """Construit le message « mission » envoyé au robot (section 4.2).

    Args:
        mission_id: identifiant de la mission.
        date_creation: date de création.
        duree_prevue_secondes: durée prévue.
        etapes: couples (numéro d'étape, identifiant de zone), dans l'ordre.
    """
    return {
        "type": "mission",
        "mission_id": mission_id,
        "cree_le": formater_date_iso_utc(date_creation),
        "duree_prevue_s": duree_prevue_secondes,
        "etapes": [{"etape": etape, "zone_id": zone_id} for etape, zone_id in etapes],
    }


def evaluer_non_confirmation(
    maintenant,
    derniere_activite,
    date_recue,
    duree_prevue_secondes,
    duree_cycle_secondes=3,
    cycles_silence=10,
    facteur_plafond=3,
):
    """Applique la règle des missions non confirmées (section 6.6).

    Args:
        maintenant: date du contrôle.
        derniere_activite: date du dernier message reçu du robot.
        date_recue: date du message « mission_recue ».
        duree_prevue_secondes: durée prévue de la mission.
        duree_cycle_secondes: durée d'un cycle de polling.
        cycles_silence: nombre de cycles sans message avant alerte.
        facteur_plafond: multiple de la durée prévue qui borne la mission.

    Returns:
        "silence", "plafond", ou None si la mission reste confirmée.
    """
    if maintenant - derniere_activite >= timedelta(
        seconds=cycles_silence * duree_cycle_secondes
    ):
        return "silence"
    if maintenant - date_recue > timedelta(
        seconds=facteur_plafond * duree_prevue_secondes
    ):
        return "plafond"
    return None
