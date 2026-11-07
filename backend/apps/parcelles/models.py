from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Parcelle(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    localisation = models.CharField(max_length=255, blank=True)
    superficie_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Zone(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name="zones")
    nom = models.CharField(max_length=100)
    ordre = models.PositiveSmallIntegerField(default=0)
    seuil_humidite = models.PositiveSmallIntegerField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage en dessous duquel la zone est jugée trop sèche.",
    )

    class Meta:
        ordering = ["parcelle", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["parcelle", "nom"], name="zone_nom_unique_par_parcelle"),
            models.CheckConstraint(
                condition=models.Q(seuil_humidite__gte=0, seuil_humidite__lte=100),
                name="zone_seuil_entre_0_et_100",
            ),
        ]

    def __str__(self):
        return f"{self.parcelle.nom} / {self.nom}"


class Culture(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Cultiver(models.Model):
    """Association : quelle culture est pratiquée dans quelle zone."""

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="cultures")
    culture = models.ForeignKey(Culture, on_delete=models.PROTECT, related_name="zones")
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["zone", "culture", "date_debut"], name="cultiver_unique"),
        ]
