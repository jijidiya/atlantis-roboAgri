"""Vues des mesures : lecture seule."""

from rest_framework import viewsets

from .models import MesureHumidite
from .serializers import MesureHumiditeSerializer


class MesureHumiditeViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture seule : les mesures arrivent par communication/handlers.py."""

    queryset = MesureHumidite.objects.select_related("zone")
    serializer_class = MesureHumiditeSerializer
    filterset_fields = ["zone", "mission", "est_valide"]
