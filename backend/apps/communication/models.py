"""Modèles de la communication avec le robot."""

from django.db import models


class NomEtatRobot(models.TextChoices):
    """États du robot (docs/protocole.md, section 3.3)."""

    REPOS = "repos"
    EN_DEPLACEMENT = "en_deplacement"
    EN_MESURE = "en_mesure"
    ARRET = "arret"
    ERREUR = "erreur"
    HORS_LIGNE = "hors_ligne"


class MessageRecu(models.Model):
    """Trace de chaque message du robot.

    `message_id` est la seule clé anti-doublon : l'unicité est garantie par la base.
    `num_sequence` ne sert qu'à l'ordre et à la détection des trous.
    """

    message_id = models.CharField(max_length=16, unique=True)
    num_sequence = models.BigIntegerField(null=True, blank=True)
    type = models.CharField(max_length=30)
    contenu = models.JSONField()
    reponse = models.JSONField(default=dict)
    a_trou_sequence = models.BooleanField(
        default=False,
        help_text="Des numéros manquent avant ce message (peut-être en retard).",
    )
    date_reception = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_reception"]
        verbose_name = "message reçu"
        verbose_name_plural = "messages reçus"

    def __str__(self):
        return f"{self.type} {self.message_id}"


class EtatRobot(models.Model):
    """État courant du robot (une seule ligne : il n'y a qu'un robot)."""

    etat = models.CharField(max_length=20, choices=NomEtatRobot.choices)
    date_mise_a_jour = models.DateTimeField()

    class Meta:
        verbose_name = "état du robot"
        verbose_name_plural = "états du robot"

    def __str__(self):
        return self.etat
