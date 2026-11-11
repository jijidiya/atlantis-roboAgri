"""Modèles de l'application « irrigation » (module 7).

Tables du MPD : decision, irrigation.

Une décision est issue d'une analyse (RG13). Une irrigation arrose une zone
(RG14) : soit automatiquement sur la base d'une décision (RG15), soit
manuellement à la demande d'un utilisateur, sans décision (RG16).

Règles appliquées dans le code, pas en base : durée maximale d'une irrigation
(RG18) et interdiction d'arroser après une mesure invalide (RG17).
"""
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.contraintes import entre_0_et_100


class Decision(models.Model):
    """Conclusion tirée d'une analyse : faut-il arroser la zone ?

    Les seuils appliqués sont copiés depuis la zone au moment de la décision
    (RG13) : si la zone est modifiée plus tard, la décision garde les seuils
    qui ont servi à la prendre.
    """

    TYPES = [
        ("humidite_suffisante", "Humidité suffisante"),
        ("humidite_insuffisante", "Humidité insuffisante"),
        ("mesure_invalide", "Mesure invalide"),
    ]
    STATUTS = [
        ("recommandee", "Recommandée"),
        ("autorisee", "Autorisée"),
        ("refusee", "Refusée"),
    ]

    decision_id = models.AutoField(primary_key=True)
    type_decision = models.CharField(max_length=30, choices=TYPES)
    action = models.CharField(max_length=50)  # ex. « arroser », « ne rien faire »
    justification = models.TextField(blank=True, null=True)
    seuil_min_applique = models.DecimalField(max_digits=5, decimal_places=2)  # en %
    seuil_max_applique = models.DecimalField(max_digits=5, decimal_places=2)  # en %
    statut = models.CharField(max_length=20, choices=STATUTS)
    date_decision = models.DateTimeField(default=timezone.now)
    analyse = models.ForeignKey(
        "analyse.Analyse", on_delete=models.PROTECT, related_name="decisions"
    )  # RG13 : une décision est issue d'une analyse

    class Meta:
        db_table = "decision"
        ordering = ["-date_decision"]
        constraints = [
            entre_0_et_100("seuil_min_applique", "decision_seuil_min_valide"),
            entre_0_et_100("seuil_max_applique", "decision_seuil_max_valide"),
        ]

    def __str__(self):
        return f"Décision {self.decision_id} ({self.type_decision})"


class Irrigation(models.Model):
    """Arrosage d'une zone, automatique ou manuel."""

    STATUTS = [
        ("planifiee", "Planifiée"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
        ("interrompue", "Interrompue"),
    ]

    irrigation_id = models.AutoField(primary_key=True)
    volume_ml = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # volume d'eau, connu une fois l'arrosage fini
    duree_secondes = models.PositiveIntegerField()  # doit rester sous le maximum (RG18)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="planifiee")
    automatique = models.BooleanField()  # vrai : décision du système ; faux : demande manuelle
    zone = models.ForeignKey(
        "parcelles.Zone", on_delete=models.PROTECT, related_name="irrigations"
    )  # RG14 : une irrigation concerne une zone
    # Renseignée seulement si l'irrigation est automatique (RG15).
    decision = models.ForeignKey(
        Decision,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="irrigations",
    )
    # Renseigné seulement si l'irrigation est manuelle (RG16).
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="irrigations",
    )

    class Meta:
        db_table = "irrigation"
        ordering = ["-date_debut"]
        # MPD : historique d'irrigation d'une zone.
        indexes = [models.Index(fields=["zone", "date_debut"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(volume_ml__gte=0), name="irrigation_volume_positif"
            ),
            models.CheckConstraint(
                condition=Q(duree_secondes__gt=0), name="irrigation_duree_positive"
            ),
            # RG15 et RG16 : automatique <=> décision sans utilisateur ;
            # manuelle <=> utilisateur sans décision.
            models.CheckConstraint(
                condition=(
                    Q(automatique=True, decision__isnull=False, utilisateur__isnull=True)
                    | Q(automatique=False, utilisateur__isnull=False, decision__isnull=True)
                ),
                name="irrigation_auto_ou_manuelle",
            ),
        ]

    def __str__(self):
        mode = "auto" if self.automatique else "manuelle"
        return f"Irrigation {self.irrigation_id} ({mode}, zone {self.zone_id})"