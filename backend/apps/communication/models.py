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


class MessageRecu(models.Model):
    """Message envoyé par le robot, identifié par son message_id unique."""

    message_id = models.CharField(
        max_length=16,
        primary_key=True,
        help_text="16 caractères hexadécimaux, générés par l'ESP32.",
    )
    num_sequence = models.IntegerField(
        null=True, blank=True,
        help_text="Ordre du message dans la session (peut manquer sur un Last Will).",
    )
    type_message = models.CharField(
        max_length=30,
        help_text="Type du message : mesure, etat, incident.",
    )
    contenu = models.JSONField(
        help_text="Contenu brut du message (JSON), tel que reçu du robot.",
    )
    date_heure = models.DateTimeField(
        auto_now_add=True,
        help_text="Heure de réception côté serveur.",
    )
    mission = models.ForeignKey(
        "missions.Mission",
        on_delete=models.RESTRICT,
        related_name="messages_recus",
        help_text="Mission concernée par le message.",
    )

    class Meta:
        verbose_name = "message reçu"
        verbose_name_plural = "messages reçus"
        ordering = ["-date_heure"]
        indexes = [
            models.Index(fields=["mission", "date_heure"]),
            models.Index(fields=["type_message", "date_heure"]),
        ]

    def __str__(self):
        return f"{self.message_id} ({self.type_message})"