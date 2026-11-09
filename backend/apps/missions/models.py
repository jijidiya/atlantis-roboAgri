"""Modèles de l'application « missions » (module 2).

Tables du MPD : mission, etape.

Une mission est créée par un utilisateur pour une parcelle (RG4). Elle se
décompose en étapes ordonnées, chacune visitant une zone de cette parcelle
(RG5). Pendant une étape, le robot effectue 9 mesures : 3 points de collecte
× 3 lectures (RG7), enregistrées par l'application « mesures ».
"""
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Mission(models.Model):
    """Parcours confié au robot sur une parcelle.

    Cycle de vie du statut (valeurs du MPD) :
    planifiee -> en_cours -> terminee, ou interrompue.
    `non_confirmee` signale une mission dont le résultat n'a pas pu être
    confirmé (perte de communication).
    """

    STATUTS = [
        ("planifiee", "Planifiée"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
        ("interrompue", "Interrompue"),
        ("non_confirmee", "Non confirmée"),
    ]

    mission_id = models.AutoField(primary_key=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="planifiee")
    date_creation = models.DateTimeField(default=timezone.now)
    date_debut = models.DateTimeField(null=True, blank=True)  # rempli au démarrage
    date_fin = models.DateTimeField(null=True, blank=True)    # rempli à la clôture
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="missions"
    )  # créateur de la mission (RG4)
    # Référence par chaîne « app.Modele » : évite les imports circulaires entre applications.
    parcelle = models.ForeignKey(
        "parcelles.Parcelle", on_delete=models.PROTECT, related_name="missions"
    )

    class Meta:
        db_table = "mission"
        # Accélère « les missions d'une parcelle par statut » (MPD, section index).
        indexes = [models.Index(fields=["parcelle", "statut"])]
        constraints = [
            # Une mission ne peut pas se terminer avant d'avoir commencé.
            models.CheckConstraint(
                condition=Q(date_fin__isnull=True) | Q(date_fin__gte=F("date_debut")),
                name="mission_dates_coherentes",
            ),
        ]

    def __str__(self):
        return f"Mission {self.mission_id} ({self.statut})"


class Etape(models.Model):
    """Visite d'une zone pendant une mission.

    Une zone peut être visitée plusieurs fois dans la même mission, sans
    prélèvement supplémentaire (RG6). La zone doit appartenir à la parcelle de
    la mission (RG5) : cette règle n'est pas exprimable en CHECK SQL, elle est
    donc à vérifier dans le code (méthode `clean` ou serializer).
    """

    STATUTS = [
        ("planifiee", "Planifiée"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
        ("interrompue", "Interrompue"),
    ]

    etape_id = models.AutoField(primary_key=True)
    numero_ordre = models.PositiveIntegerField()  # position dans la mission, à partir de 1
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="planifiee")
    mission = models.ForeignKey(
        Mission, on_delete=models.PROTECT, related_name="etapes"
    )
    zone = models.ForeignKey(
        "parcelles.Zone", on_delete=models.PROTECT, related_name="etapes"
    )

    class Meta:
        db_table = "etape"
        constraints = [
            models.CheckConstraint(
                condition=Q(numero_ordre__gte=1), name="etape_ordre_positif"
            ),
            # Deux étapes d'une même mission ne peuvent pas avoir le même numéro d'ordre.
            models.UniqueConstraint(
                fields=["mission", "numero_ordre"],
                name="etape_ordre_unique_par_mission",
            ),
        ]
        ordering = ["mission", "numero_ordre"]

    def __str__(self):
        return f"Étape {self.numero_ordre} de la mission {self.mission_id}"