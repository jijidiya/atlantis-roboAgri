"""Modèles de l'application « communication » (module 3).

Table du MPD : message.

Un message est un échange entre le robot et l'application pendant une mission
(RG9). Son contenu JSON regroupe toutes les mesures d'une étape. Le robot
fabrique lui-même l'identifiant du message : c'est ce qui empêche
d'enregistrer deux fois la même opération (RG10).
"""
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

# 16 caractères hexadécimaux, par exemple « 9f3a1c7e5b2d4a60 ».
MOTIF_MESSAGE_ID = r"^[0-9a-fA-F]{16}$"


class Message(models.Model):
    """Message reçu du robot (ou envoyé au robot) dans le cadre d'une mission."""

    # Identifiant fourni par le robot, pas auto-incrémenté (MPD : VARCHAR(16)).
    # Si le robot renvoie un message déjà reçu, la clé primaire bloque le doublon.
    message_id = models.CharField(
        max_length=16,
        primary_key=True,
        validators=[
            RegexValidator(
                MOTIF_MESSAGE_ID,
                "L'identifiant doit comporter exactement 16 caractères hexadécimaux.",
            )
        ],
    )
    # Peut être vide (message « Last Will ») et n'est pas unique : il sert à l'ordre.
    num_sequence = models.IntegerField(null=True, blank=True)
    # Les valeurs possibles seront fixées avec docs/protocole-communication.md.
    type_message = models.CharField(max_length=30)
    contenu = models.JSONField()  # mesures d'une étape, au format JSON
    date_heure = models.DateTimeField(default=timezone.now)
    mission = models.ForeignKey(
        "missions.Mission", on_delete=models.PROTECT, related_name="messages"
    )  # RG9 : un message appartient à une mission

    class Meta:
        db_table = "message"
        ordering = ["mission", "num_sequence", "date_heure"]
        constraints = [
            # Même règle que le validateur, mais appliquée par PostgreSQL.
            models.CheckConstraint(
                condition=Q(message_id__regex=MOTIF_MESSAGE_ID),
                name="message_id_hexadecimal_16",
            ),
        ]

    def __str__(self):
        return f"Message {self.message_id} (mission {self.mission_id})"