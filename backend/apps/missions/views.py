"""Vues minces des missions : toute la logique est dans services.py."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Mission
from .serializers import ChangementStatutSerializer, MissionSerializer


class MissionViewSet(viewsets.ModelViewSet):
    """CRUD des missions, plus l'action de changement de statut."""

    queryset = Mission.objects.prefetch_related("etapes")
    serializer_class = MissionSerializer

    def perform_create(self, serializer):
        """Crée la mission et ses étapes par le service."""
        serializer.instance = services.creer_mission(
            duree_prevue_secondes=serializer.validated_data.get(
                "duree_prevue_secondes", 600
            ),
            zones_ordonnees=serializer.validated_data["zones"],
        )

    @action(detail=True, methods=["post"])
    def statut(self, request, pk=None):
        """Change le statut d'une mission (ex. relancer une mission non confirmée)."""
        entree = ChangementStatutSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        mission = services.changer_statut(
            self.get_object(), entree.validated_data["statut"]
        )
        return Response(MissionSerializer(mission).data)
