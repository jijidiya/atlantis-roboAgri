"""Modèles de l'application « analyse » (module 5).

Table du MPD : analyse.

Une analyse résume les mesures d'une zone sur une période. Les mesures qu'elle
exploite portent la clé étrangère (`Mesure.analyse`) : il n'y a pas de table
d'association (RG12).
"""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.contraintes import entre_0_et_100


class Analyse(models.Model):
    """Statistiques d'humidité d'une zone sur une période."""

    analyse_id = models.AutoField(primary_key=True)
    date_analyse = models.DateTimeField(default=timezone.now)
    periode_debut = models.DateTimeField()
    periode_fin = models.DateTimeField()
    humidite_moyenne = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # en %
    humidite_minimum = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # en %
    humidite_maximum = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # en %
    nombre_mesures = models.PositiveIntegerField()
    resultat_analyse = models.TextField(blank=True, null=True)
    zone = models.ForeignKey(
        "parcelles.Zone", on_delete=models.PROTECT, related_name="analyses"
    )  # RG12 : une analyse concerne une seule zone

    class Meta:
        db_table = "analyse"
        ordering = ["-date_analyse"]
        constraints = [
            models.CheckConstraint(
                condition=Q(periode_fin__gte=F("periode_debut")),
                name="analyse_periode_coherente",
            ),
            entre_0_et_100("humidite_moyenne", "analyse_humidite_moyenne_valide"),
            entre_0_et_100("humidite_minimum", "analyse_humidite_minimum_valide"),
            entre_0_et_100("humidite_maximum", "analyse_humidite_maximum_valide"),
        ]

    def __str__(self):
        return f"Analyse {self.analyse_id} (zone {self.zone_id})"