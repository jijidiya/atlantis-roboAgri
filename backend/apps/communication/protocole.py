"""Format des messages du robot : vérification de la structure et des types.

Module PUR : aucun import Django, aucun accès à la base. Il ne vérifie que la
FORME du message. La validité des valeurs mesurées est jugée par
mesures/validation.py, et une mesure douteuse est enregistrée, pas rejetée.

À ALIGNER avec docs/protocole-communication.md : si les noms de champs y
diffèrent, c'est le seul fichier à modifier.

Exemple de message « mesure » (une étape = jusqu'à 9 lectures, RG7) :
    {
      "type": "mesure", "message_id": "9f3a1c7e5b2d4a60", "num_sequence": 12,
      "mission": 5, "etape": 1, "horodatage": "2026-11-11T08:15:00Z",
      "lectures": [
        {"numero_point": 1, "numero_lecture": 1, "valeur_brute": 2150, "humidite_pct": 41.2},
        ...
      ]
    }
Message « etat » :     {"type": "etat", ..., "etat": "en_cours"}
Message « incident » : {"type": "incident", ..., "type_incident": "obstacle"}
"""
import math
import re
from dataclasses import dataclass
from datetime import datetime

TYPES_MESSAGE = ("mesure", "etat", "incident")
ETATS_ROBOT = ("en_cours", "terminee", "interrompue")
INCIDENTS_ROBOT = ("obstacle", "capteur_defaillant", "perte_communication")
MOTIF_MESSAGE_ID = re.compile(r"^[0-9a-fA-F]{16}$")


class ProtocoleInvalide(Exception):
    """Message mal formé ; `champ` désigne le champ fautif."""

    def __init__(self, champ, message):
        super().__init__(f"{champ} : {message}")
        self.champ = champ
        self.message = message


@dataclass(frozen=True)
class Lecture:
    numero_point: int
    numero_lecture: int
    valeur_brute: int | None
    humidite_pct: float | None
    horodatage: datetime


@dataclass(frozen=True)
class MessageValide:
    type: str
    message_id: str
    num_sequence: int | None
    mission: int
    horodatage: datetime
    etape: int | None = None              # numéro d'ordre de l'étape (type « mesure »)
    lectures: tuple = ()                  # type « mesure »
    etat: str | None = None               # type « etat »
    type_incident: str | None = None      # type « incident »


def _entier(donnees, champ, obligatoire=True, minimum=None, maximum=None):
    valeur = donnees.get(champ)
    if valeur is None:
        if obligatoire:
            raise ProtocoleInvalide(champ, "champ obligatoire.")
        return None
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        raise ProtocoleInvalide(champ, "un entier est attendu.")
    if minimum is not None and valeur < minimum:
        raise ProtocoleInvalide(champ, f"doit être au moins {minimum}.")
    if maximum is not None and valeur > maximum:
        raise ProtocoleInvalide(champ, f"doit être au plus {maximum}.")
    return valeur


def _nombre_ou_none(donnees, champ):
    valeur = donnees.get(champ)
    if valeur is None:
        return None
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not math.isfinite(valeur):
        raise ProtocoleInvalide(champ, "un nombre ou null est attendu.")
    return float(valeur)


def _horodatage(donnees, champ):
    texte = donnees.get(champ)
    if not isinstance(texte, str):
        raise ProtocoleInvalide(champ, "date ISO 8601 obligatoire (ex. 2026-11-11T08:15:00Z).")
    try:
        moment = datetime.fromisoformat(texte)
    except ValueError:
        raise ProtocoleInvalide(champ, "date ISO 8601 invalide.")
    if moment.tzinfo is None:
        raise ProtocoleInvalide(champ, "le fuseau horaire est obligatoire (ex. Z ou +00:00).")
    return moment


def _lectures(donnees, horodatage_message):
    brutes = donnees.get("lectures")
    if not isinstance(brutes, list) or not 1 <= len(brutes) <= 9:
        raise ProtocoleInvalide("lectures", "une liste de 1 à 9 lectures est attendue.")
    lectures, vues = [], set()
    for position, brute in enumerate(brutes):
        if not isinstance(brute, dict):
            raise ProtocoleInvalide(f"lectures[{position}]", "un objet est attendu.")
        point = _entier(brute, "numero_point", minimum=1, maximum=3)
        numero = _entier(brute, "numero_lecture", minimum=1, maximum=3)
        if (point, numero) in vues:
            raise ProtocoleInvalide(f"lectures[{position}]", "point et lecture en double.")
        vues.add((point, numero))
        lectures.append(Lecture(
            numero_point=point,
            numero_lecture=numero,
            valeur_brute=_entier(brute, "valeur_brute", obligatoire=False),
            humidite_pct=_nombre_ou_none(brute, "humidite_pct"),
            horodatage=_horodatage(brute, "horodatage") if "horodatage" in brute else horodatage_message,
        ))
    return tuple(lectures)


def valider(donnees) -> MessageValide:
    """Vérifie un message du robot ou lève ProtocoleInvalide."""
    if not isinstance(donnees, dict):
        raise ProtocoleInvalide("corps", "un objet JSON est attendu.")
    type_message = donnees.get("type")
    if type_message not in TYPES_MESSAGE:
        raise ProtocoleInvalide("type", f"valeurs possibles : {', '.join(TYPES_MESSAGE)}.")
    message_id = donnees.get("message_id")
    if not isinstance(message_id, str) or not MOTIF_MESSAGE_ID.match(message_id):
        raise ProtocoleInvalide("message_id", "16 caractères hexadécimaux attendus.")

    horodatage = _horodatage(donnees, "horodatage")
    commun = dict(
        type=type_message,
        message_id=message_id.lower(),
        num_sequence=_entier(donnees, "num_sequence", obligatoire=False),
        mission=_entier(donnees, "mission", minimum=1),
        horodatage=horodatage,
    )
    if type_message == "mesure":
        return MessageValide(
            **commun,
            etape=_entier(donnees, "etape", minimum=1),
            lectures=_lectures(donnees, horodatage),
        )
    if type_message == "etat":
        etat = donnees.get("etat")
        if etat not in ETATS_ROBOT:
            raise ProtocoleInvalide("etat", f"valeurs possibles : {', '.join(ETATS_ROBOT)}.")
        return MessageValide(**commun, etat=etat)
    type_incident = donnees.get("type_incident")
    if type_incident not in INCIDENTS_ROBOT:
        raise ProtocoleInvalide("type_incident", f"valeurs possibles : {', '.join(INCIDENTS_ROBOT)}.")
    return MessageValide(**commun, type_incident=type_incident)