from rest_framework import viewsets

from .models import Mesure
from .serializers import MesureSerializer


class MesureViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture seule : les mesures arrivent par communication/handlers.py."""

    queryset = Mesure.objects.select_related("zone")
    serializer_class = MesureSerializer
    filterset_fields = ["zone", "mission", "valide"]
