from rest_framework import viewsets

from .models import Cultiver, Culture, Parcelle, Zone
from .serializers import (
    CultiverSerializer,
    CultureSerializer,
    ParcelleSerializer,
    ZoneSerializer,
)


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.prefetch_related("zones")
    serializer_class = ParcelleSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.select_related("parcelle")
    serializer_class = ZoneSerializer
    filterset_fields = ["parcelle"]


class CultureViewSet(viewsets.ModelViewSet):
    queryset = Culture.objects.all()
    serializer_class = CultureSerializer


class CultiverViewSet(viewsets.ModelViewSet):
    queryset = Cultiver.objects.select_related("zone", "culture")
    serializer_class = CultiverSerializer
