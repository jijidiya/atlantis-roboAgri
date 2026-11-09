"""Vues de l'API « missions » (RF02) : créer, consulter, changer l'état."""
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Mission
from .serializers import MissionSerializer

# Transitions autorisées : nom -> (statuts de départ, nouveau statut, champ date à remplir)
TRANSITIONS = {
    "demarrer": ({"planifiee"}, "en_cours", "date_debut"),
    "terminer": ({"en_cours"}, "terminee", "date_fin"),
    "interrompre": ({"en_cours"}, "interrompue", "date_fin"),
}


class MissionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Pas de modification ni de suppression libre : le statut change seulement
    par les actions ci-dessous, pour éviter un état incohérent."""

    serializer_class = MissionSerializer

    def get_queryset(self):
        """Filtres : /api/missions/?parcelle=1&statut=en_cours"""
        requete = Mission.objects.prefetch_related("etapes").order_by("-date_creation")
        parcelle = self.request.query_params.get("parcelle")
        statut = self.request.query_params.get("statut")
        if parcelle:
            requete = requete.filter(parcelle_id=parcelle)
        if statut:
            requete = requete.filter(statut=statut)
        return requete

    def _transition(self, nom):
        """Applique une transition de statut, ou renvoie 409 si elle est interdite."""
        mission = self.get_object()
        autorises, nouveau, champ_date = TRANSITIONS[nom]
        if mission.statut not in autorises:
            return Response(
                {"detail": f"Impossible : la mission est « {mission.statut} »."},
                status=409,
            )
        mission.statut = nouveau
        setattr(mission, champ_date, timezone.now())
        mission.save(update_fields=["statut", champ_date])
        return Response(self.get_serializer(mission).data)

    @action(detail=True, methods=["post"])
    def demarrer(self, request, pk=None):
        return self._transition("demarrer")

    @action(detail=True, methods=["post"])
    def terminer(self, request, pk=None):
        return self._transition("terminer")

    @action(detail=True, methods=["post"])
    def interrompre(self, request, pk=None):
        return self._transition("interrompre")