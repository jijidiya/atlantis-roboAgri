"""Modèles des missions du robot (statuts : docs/protocole.md, section 3.2)."""

from django.db import models

from apps.parcelles.models import Zone


class StatutMission(models.TextChoices):
    """Statuts d'une mission, du plus ancien au plus récent."""

    EN_ATTENTE = "en_attente"
    ENVOYEE = "envoyee"
    RECUE = "recue"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ECHOUEE = "echouee"
    NON_CONFIRMEE = "non_confirmee"


class Mission(models.Model):
    """Ordre de mission confié au robot : une liste d'étapes (zones) à visiter."""

    statut = models.CharField(
        max_length=20, choices=StatutMission.choices, default=StatutMission.EN_ATTENTE
    )
    duree_prevue_secondes = models.PositiveIntegerField(default=600)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_recue = models.DateTimeField(null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "mission"
        verbose_name_plural = "missions"

    def __str__(self):
        return f"Mission {self.pk} ({self.statut})"


class EtapeMission(models.Model):
    """Étape d'une mission : une zone à visiter, à une position donnée."""

    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name="etapes"
    )
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="etapes")
    ordre = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["mission", "ordre"]
        verbose_name = "étape de mission"
        verbose_name_plural = "étapes de mission"
        constraints = [
            models.UniqueConstraint(
                fields=["mission", "ordre"], name="etape_ordre_unique"
            ),
        ]

    def __str__(self):
        return f"Mission {self.mission_id}, étape {self.ordre} : {self.zone}"
