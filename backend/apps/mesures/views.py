"""Vues de l'API « mesures » : consultation seule (GET /mesures/)."""
from rest_framework import viewsets

from apps.core.filtres import lire_date, lire_entier
from apps.core.pagination import PaginationStandard

from . import services
from .serializers import MesureSerializer


class MesureViewSet(viewsets.ReadOnlyModelViewSet):
    """Filtres : /api/v1/mesures/?zone=3&mission=12&statut=valide&du=2026-11-01&au=2026-11-08"""

    serializer_class = MesureSerializer
    pagination_class = PaginationStandard

    def get_queryset(self):
        p = self.request.query_params
        return services.lister_mesures(
            zone=lire_entier(p, "zone"),
            mission=lire_entier(p, "mission"),
            statut=p.get("statut"),
            du=lire_date(p, "du"),
            au=lire_date(p, "au", fin=True),
        )