"""Vues de l'API « incidents » : consultation seule."""
from rest_framework import viewsets

from apps.core.filtres import lire_date, lire_entier
from apps.core.pagination import PaginationStandard

from . import services
from .serializers import IncidentSerializer


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """Filtres : /api/v1/incidents/?mission=12&type_incident=obstacle&du=2026-11-01&au=2026-11-08"""

    serializer_class = IncidentSerializer
    pagination_class = PaginationStandard

    def get_queryset(self):
        p = self.request.query_params
        return services.lister_incidents(
            mission=lire_entier(p, "mission"),
            type_incident=p.get("type_incident"),
            du=lire_date(p, "du"),
            au=lire_date(p, "au", fin=True),
        )