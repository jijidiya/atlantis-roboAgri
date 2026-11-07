from django.db import models

from apps.missions.models import Mission
from apps.parcelles.models import Zone


class Mesure(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="mesures")
    mission = models.ForeignKey(
        Mission, null=True, blank=True, on_delete=models.SET_NULL, related_name="mesures"
    )
    sequence = models.PositiveIntegerField()
    humidite = models.FloatField(null=True, blank=True, help_text="Pourcentage 0-100")
    mesuree_le = models.DateTimeField()
    valide = models.BooleanField(default=True)
    motif_invalidite = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-mesuree_le"]
        constraints = [
            models.UniqueConstraint(
                fields=["mission", "sequence", "zone"], name="mesure_unique_par_mission_zone"
            ),
            # Sans mission, NULL n'est jamais égal à NULL : contrainte dédiée.
            models.UniqueConstraint(
                fields=["sequence", "zone"],
                condition=models.Q(mission__isnull=True),
                name="mesure_unique_sans_mission",
            ),
        ]
        indexes = [models.Index(fields=["zone", "-mesuree_le"])]
