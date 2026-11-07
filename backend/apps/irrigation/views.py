"""Vues de l'irrigation et des incidents : lecture seule."""

from rest_framework import viewsets

from .models import Incident, Irrigation
from .serializers import IncidentSerializer, IrrigationSerializer


class IrrigationViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des irrigations."""

    queryset = Irrigation.objects.select_related("zone")
    serializer_class = IrrigationSerializer
    filterset_fields = ["zone", "type", "decision"]


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des incidents."""

    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    filterset_fields = ["zone", "mission", "code", "gravite"]
