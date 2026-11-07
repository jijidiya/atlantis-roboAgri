from django.db import models

from apps.mesures.models import Mesure
from apps.missions.models import Mission
from apps.parcelles.models import Zone


class EtatDecision(models.TextChoices):
    SUFFISANTE = "suffisante"
    INSUFFISANTE = "insuffisante"
    INVALIDE = "invalide"


class TypeIrrigation(models.TextChoices):
    RECOMMANDATION = "recommandation"
    INTERVENTION = "intervention"


class Irrigation(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="irrigations")
    mesure = models.ForeignKey(Mesure, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TypeIrrigation.choices)
    decision = models.CharField(max_length=20, choices=EtatDecision.choices)
    declenchee_le = models.DateTimeField(auto_now_add=True)
    duree_secondes = models.PositiveIntegerField(null=True, blank=True)
    volume_litres = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-declenchee_le"]


class Incident(models.Model):
    """Créé uniquement par irrigation et communication, via services.signaler_incident."""

    zone = models.ForeignKey(Zone, null=True, blank=True, on_delete=models.SET_NULL)
    mission = models.ForeignKey(Mission, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
