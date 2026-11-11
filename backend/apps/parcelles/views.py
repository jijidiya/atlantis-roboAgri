"""Vues de l'API « parcelles » : lister, créer, consulter, modifier (RF01)."""
from rest_framework import viewsets

from .models import Culture, Parcelle, Zone
from .serializers import CultureSerializer, ParcelleSerializer, ZoneSerializer


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.prefetch_related("zones__cultures")
    serializer_class = ParcelleSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer

    def get_queryset(self):
        """Permet de filtrer : /api/zones/?parcelle=1"""
        requete = Zone.objects.prefetch_related("cultures")
        parcelle = self.request.query_params.get("parcelle")
        return requete.filter(parcelle_id=parcelle) if parcelle else requete


class CultureViewSet(viewsets.ModelViewSet):
    queryset = Culture.objects.all()
    serializer_class = CultureSerializer