from rest_framework import viewsets

from .models import Incident, Irrigation
from .serializers import IncidentSerializer, IrrigationSerializer


class IrrigationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Irrigation.objects.select_related("zone")
    serializer_class = IrrigationSerializer
    filterset_fields = ["zone", "type", "decision"]


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    filterset_fields = ["zone", "mission", "type"]
