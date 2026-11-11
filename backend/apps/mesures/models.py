"""Modèles de l'application « mesures » (module 6).

Table du MPD : mesure.

Une étape prévoit 3 points de collecte × 3 lectures = 9 mesures (RG7). Une
mesure est identifiée par son étape, son numéro de point et son numéro de
lecture. Elle est enregistrée avec son statut : valide, invalide ou
manquante (RG8).

TimescaleDB (prévu plus tard) : la table deviendra une hypertable partitionnée
sur `date_heure_mesure`. La clé primaire composée (mesure_id, date_heure_mesure)
sera alors posée par une migration dédiée (voir MPD, section TimescaleDB).
"""
from django.db import models
from django.db.models import Q

from apps.core.contraintes import entre_0_et_100


class Mesure(models.Model):
    """Une lecture d'humidité faite par le robot à un point de collecte."""

    STATUTS = [
        ("valide", "Valide"),
        ("invalide", "Invalide"),
        ("manquante", "Manquante"),
    ]

    mesure_id = models.AutoField(primary_key=True)
    numero_point = models.PositiveSmallIntegerField()    # point de collecte : 1 à 3
    numero_lecture = models.PositiveSmallIntegerField()  # lecture au point : 1 à 3
    valeur_brute = models.IntegerField(null=True, blank=True)  # valeur lue par le capteur
    valeur_humidite = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # en %, obligatoire si la mesure est valide
    date_heure_mesure = models.DateTimeField()  # horodatage fourni par le robot
    statut = models.CharField(max_length=20, choices=STATUTS)
    etape = models.ForeignKey(
        "missions.Etape", on_delete=models.PROTECT, related_name="mesures"
    )  # RG7 : produite par une étape
    message = models.ForeignKey(
        "communication.Message", on_delete=models.PROTECT, related_name="mesures"
    )  # RG9 : une mesure vient d'un seul message
    # Liens facultatifs : si l'incident ou l'analyse est supprimé, la mesure reste (SET NULL).
    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesures",
    )  # RG11 : une mesure est liée à un incident au maximum
    # Vide à la réception : la mesure est rattachée à une analyse plus tard (RG12).
    analyse = models.ForeignKey(
        "analyse.Analyse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesures",
    )

    class Meta:
        db_table = "mesure"
        ordering = ["-date_heure_mesure"]
        constraints = [
            models.CheckConstraint(
                condition=Q(numero_point__gte=1, numero_point__lte=3),
                name="mesure_numero_point_valide",
            ),
            models.CheckConstraint(
                condition=Q(numero_lecture__gte=1, numero_lecture__lte=3),
                name="mesure_numero_lecture_valide",
            ),
            entre_0_et_100("valeur_humidite", "mesure_valeur_humidite_valide"),
            # Une mesure valide doit avoir une valeur d'humidité (RG8).
            models.CheckConstraint(
                condition=~Q(statut="valide") | Q(valeur_humidite__isnull=False),
                name="mesure_valide_a_une_humidite",
            ),
            # Anti-doublon d'une lecture. Le vrai blocage se fait sur message_id (RG10).
            models.UniqueConstraint(
                fields=["etape", "numero_point", "numero_lecture", "date_heure_mesure"],
                name="mesure_unique_par_lecture",
            ),
        ]

    def __str__(self):
        return (
            f"Mesure {self.mesure_id} (étape {self.etape_id}, "
            f"point {self.numero_point}, lecture {self.numero_lecture})"
        )