"""Module PUR : structure et types des messages du robot. Sans Django."""

from dataclasses import dataclass
from datetime import datetime


class MessageInvalide(ValueError):
    pass


@dataclass(frozen=True)
class Message:
    identifiant: str
    zone_id: int
    sequence: int
    humidite: float | None
    mesuree_le: datetime
    mission_id: int | None = None


def valider(donnees):
    """Transforme un dict brut en Message, ou lève MessageInvalide."""
    try:
        return Message(
            identifiant=str(donnees["id_message"]),
            zone_id=int(donnees["zone_id"]),
            sequence=int(donnees["sequence"]),
            humidite=None if donnees.get("humidite") is None else float(donnees["humidite"]),
            mesuree_le=datetime.fromisoformat(donnees["mesure_le"]),
            mission_id=None if donnees.get("mission_id") is None else int(donnees["mission_id"]),
        )
    except (KeyError, TypeError, ValueError) as erreur:
        raise MessageInvalide(f"Message mal formé : {erreur}") from erreur
