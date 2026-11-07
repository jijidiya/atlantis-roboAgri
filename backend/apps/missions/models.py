from django.db import models

from apps.parcelles.models import Zone


class StatutMission(models.TextChoices):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    INTERROMPUE = "interrompue"
    NON_CONFIRMEE = "non_confirmee"


class Mission(models.Model):
    statut = models.CharField(
        max_length=20, choices=StatutMission.choices, default=StatutMission.PLANIFIEE
    )
    prevue_le = models.DateTimeField()
    debutee_le = models.DateTimeField(null=True, blank=True)
    terminee_le = models.DateTimeField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-prevue_le"]


class EtapeMission(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="etapes")
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="etapes")
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["mission", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["mission", "ordre"], name="etape_ordre_unique"),
        ]
