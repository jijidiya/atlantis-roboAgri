from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Mission
from .serializers import ChangementStatutSerializer, MissionSerializer


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.prefetch_related("etapes")
    serializer_class = MissionSerializer

    @action(detail=True, methods=["post"])
    def statut(self, request, pk=None):
        entree = ChangementStatutSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        mission = services.changer_statut(self.get_object(), entree.validated_data["statut"])
        return Response(MissionSerializer(mission).data)
