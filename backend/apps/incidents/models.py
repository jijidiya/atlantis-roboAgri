"""Modèles de l'application « incidents » (module 4).

Table du MPD : incident.

Un incident signale un problème survenu pendant le fonctionnement du robot
(obstacle, capteur défaillant, perte de communication, mesure invalide).
Il est rattaché à une mission au maximum (RG11) et peut concerner plusieurs
mesures : le lien est porté par `Mesure.incident` (application « mesures »).
"""
from django.db import models
from django.utils import timezone


class Incident(models.Model):
    """Problème détecté pendant une mission, ou en dehors de toute mission."""

    TYPES = [
        ("obstacle", "Obstacle"),
        ("capteur_defaillant", "Capteur défaillant"),
        ("perte_communication", "Perte de communication"),
        ("mesure_invalide", "Mesure invalide"),
    ]

    incident_id = models.AutoField(primary_key=True)
    type_incident = models.CharField(max_length=30, choices=TYPES)
    date_incident = models.DateTimeField(default=timezone.now)
    # Facultatif (RG11) : une perte de communication peut survenir hors mission.
    mission = models.ForeignKey(
        "missions.Mission",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="incidents",
    )

    class Meta:
        db_table = "incident"
        ordering = ["-date_incident"]

    def __str__(self):
        return f"Incident {self.incident_id} ({self.type_incident})"