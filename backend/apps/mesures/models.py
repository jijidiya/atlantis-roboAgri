"""Modèle des mesures d'humidité du sol."""

from django.db import models

from apps.missions.models import Mission
from apps.parcelles.models import Zone


class MesureHumidite(models.Model):
    """Mesure d'humidité du sol faite par le robot dans une zone.

    `humidite_pourcent` est la valeur étalonnée, utilisée par la règle d'irrigation.
    `valeur_brute` est la lecture du capteur, pour le diagnostic seulement.
    """

    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="mesures")
    mission = models.ForeignKey(
        Mission, on_delete=models.PROTECT, related_name="mesures"
    )
    num_sequence = models.PositiveIntegerField()
    humidite_pourcent = models.FloatField(null=True, blank=True)
    valeur_brute = models.IntegerField()
    est_valide = models.BooleanField(default=True)
    motif_invalidite = models.CharField(max_length=50, blank=True)
    date_mesure = models.DateTimeField()
    est_date_approximative = models.BooleanField(
        default=False,
        help_text="Vrai si le robot n'avait pas d'heure : date de réception utilisée.",
    )
    uptime_ms = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-date_mesure"]
        verbose_name = "mesure d'humidité"
        verbose_name_plural = "mesures d'humidité"
        indexes = [models.Index(fields=["zone", "-date_mesure"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(humidite_pourcent__isnull=True)
                | models.Q(humidite_pourcent__gte=0, humidite_pourcent__lte=100),
                name="mesure_humidite_entre_0_et_100",
            ),
        ]

    def __str__(self):
        valeur = (
            "invalide" if self.humidite_pourcent is None else self.humidite_pourcent
        )
        return f"{self.zone} : {valeur} ({self.date_mesure:%d/%m/%Y %H:%M})"
