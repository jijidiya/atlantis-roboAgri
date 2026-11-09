"""Modèles de l'application « parcelles » (module 1).

Tables du MPD : parcelle, zone, culture, cultiver.

Hiérarchie : un utilisateur possède des parcelles, chaque parcelle contient
des zones, chaque zone peut accueillir plusieurs cultures. Les mesures
d'humidité sont toujours rattachées à une zone (via les étapes d'une mission),
et les seuils d'humidité sont définis par zone.

Suppressions : on utilise PROTECT (équivalent d'ON DELETE RESTRICT) pour
garder la traçabilité : on ne peut pas supprimer une parcelle qui a des
zones, ni une zone qui a des missions ou des irrigations.
"""
from django.conf import settings
from django.db import models
from django.db.models import F, Q

from apps.core.contraintes import entre_0_et_100


class Parcelle(models.Model):
    """Terrain agricole appartenant à un seul utilisateur (RG1)."""

    parcelle_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    superficie = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # en m², doit être > 0
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="parcelles"
    )  # propriétaire : obligatoire (RG1)

    class Meta:
        db_table = "parcelle"
        constraints = [
            models.CheckConstraint(
                condition=Q(longitude__gte=-180, longitude__lte=180),
                name="parcelle_longitude_valide",
            ),
            models.CheckConstraint(
                condition=Q(latitude__gte=-90, latitude__lte=90),
                name="parcelle_latitude_valide",
            ),
            models.CheckConstraint(
                condition=Q(superficie__gt=0), name="parcelle_superficie_positive"
            ),
        ]

    def __str__(self):
        return self.nom


class Culture(models.Model):
    """Plante cultivée (ex. tomate, variété « Roma »). Peut être présente dans plusieurs zones (RG3)."""

    culture_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    variete = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "culture"

    def __str__(self):
        return self.nom


class Zone(models.Model):
    """Sous-division d'une parcelle où le robot mesure l'humidité (RG2).

    La plage cible d'humidité de la zone est [humidite_minimum, humidite_maximum] :
    - sous le minimum : humidité insuffisante, arrosage recommandé ou autorisé ;
    - entre les deux : humidité suffisante ;
    - au-dessus du maximum : zone trop humide, pas d'arrosage.
    Les valeurs réelles viennent de l'étalonnage du capteur.

    `irrigation_auto_active` autorise l'irrigation automatique de cette zone
    (RG15). Elle est vraie ou fausse par zone ; l'état « automatique » d'une
    parcelle entière se déduit de ses zones.
    """

    zone_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    superficie = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    humidite_minimum = models.DecimalField(max_digits=5, decimal_places=2)  # en %
    humidite_maximum = models.DecimalField(max_digits=5, decimal_places=2)  # en %
    geometrie_zone = models.JSONField(null=True, blank=True)  # GeoJSON pour la carte Leaflet
    irrigation_auto_active = models.BooleanField(default=False)
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.PROTECT, related_name="zones"
    )
    # Relation plusieurs-à-plusieurs avec Culture, via la table intermédiaire `cultiver`.
    cultures = models.ManyToManyField(
        Culture, through="Cultiver", related_name="zones"
    )

    class Meta:
        db_table = "zone"
        constraints = [
            models.CheckConstraint(
                condition=Q(superficie__gt=0), name="zone_superficie_positive"
            ),
            entre_0_et_100("humidite_minimum", "zone_humidite_minimum_valide"),
            entre_0_et_100("humidite_maximum", "zone_humidite_maximum_valide"),
            # Le minimum doit rester strictement inférieur au maximum.
            models.CheckConstraint(
                condition=Q(humidite_minimum__lt=F("humidite_maximum")),
                name="zone_minimum_inferieur_maximum",
            ),
            models.UniqueConstraint(
                fields=["parcelle", "nom"], name="zone_nom_unique_par_parcelle"
            ),
        ]

    def __str__(self):
        return f"{self.parcelle} / {self.nom}"


class Cultiver(models.Model):
    """Association ZONE (0,N) — CULTURE (0,N) : quelle culture pousse dans quelle zone.

    Si une zone ou une culture est supprimée, ses liens disparaissent avec
    elle (CASCADE). Django ajoute un champ `id` : le MPD prévoit une clé
    primaire composée (zone_id, culture_id), remplacée ici par une contrainte
    d'unicité équivalente.
    """

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)

    class Meta:
        db_table = "cultiver"
        constraints = [
            # Une même culture ne peut pas être associée deux fois à la même zone.
            models.UniqueConstraint(
                fields=["zone", "culture"], name="cultiver_unique"
            ),
        ]