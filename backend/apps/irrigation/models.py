"""Modèles de l'irrigation et des incidents."""

from django.db import models

from apps.mesures.models import MesureHumidite
from apps.missions.models import Mission
from apps.parcelles.models import Zone


class EtatDecision(models.TextChoices):
    """Résultat de la règle de décision d'irrigation."""

    SUFFISANTE = "suffisante"
    INSUFFISANTE = "insuffisante"
    INVALIDE = "invalide"


class TypeIrrigation(models.TextChoices):
    """Une recommandation seulement, ou une intervention réelle."""

    RECOMMANDATION = "recommandation"
    INTERVENTION = "intervention"


class CodeIncident(models.TextChoices):
    """Codes d'incident (docs/protocole.md, section 4.7)."""

    OBSTACLE = "OBSTACLE"
    FILE_PLEINE = "FILE_PLEINE"
    NTP_ECHEC = "NTP_ECHEC"
    CAPTEUR_INVALIDE = "CAPTEUR_INVALIDE"
    MESSAGE_CONFLIT = "MESSAGE_CONFLIT"
    MISSION_NON_CONFIRMEE = "MISSION_NON_CONFIRMEE"


class GraviteIncident(models.TextChoices):
    """Gravité d'un incident ; seul « bloquant » fait échouer la mission."""

    INFO = "info"
    AVERTISSEMENT = "avertissement"
    BLOQUANT = "bloquant"


class Irrigation(models.Model):
    """Recommandation ou intervention d'irrigation pour une zone."""

    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="irrigations")
    mesure = models.ForeignKey(
        MesureHumidite, null=True, blank=True, on_delete=models.SET_NULL
    )
    type = models.CharField(max_length=20, choices=TypeIrrigation.choices)
    decision = models.CharField(max_length=20, choices=EtatDecision.choices)
    date_declenchement = models.DateTimeField(auto_now_add=True)
    duree_secondes = models.PositiveIntegerField(null=True, blank=True)
    volume_litres = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-date_declenchement"]
        verbose_name = "irrigation"
        verbose_name_plural = "irrigations"

    def __str__(self):
        return f"{self.type} {self.decision} ({self.zone})"


class Incident(models.Model):
    """Incident signalé par le robot ou détecté par l'application.

    Créé uniquement par irrigation et communication, via
    `irrigation.services.signaler_incident`.
    """

    code = models.CharField(max_length=30, choices=CodeIncident.choices)
    gravite = models.CharField(
        max_length=20,
        choices=GraviteIncident.choices,
        default=GraviteIncident.AVERTISSEMENT,
    )
    description = models.TextField(blank=True)
    zone = models.ForeignKey(Zone, null=True, blank=True, on_delete=models.SET_NULL)
    mission = models.ForeignKey(
        Mission, null=True, blank=True, on_delete=models.SET_NULL
    )
    nb_perdus = models.PositiveIntegerField(null=True, blank=True)
    date_incident = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_incident"]
        verbose_name = "incident"
        verbose_name_plural = "incidents"

    def __str__(self):
        return f"{self.code} ({self.gravite})"
