"""Vues de l'API « incidents » : consultation seule."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.filtres import lire_date, lire_entier
from apps.core.pagination import PaginationStandard

from . import services
from .serializers import IncidentSerializer


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """Filtres : /api/v1/incidents/?mission=12&type_incident=obstacle&du=...&au=..."""

    serializer_class = IncidentSerializer
    pagination_class = PaginationStandard
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        p = self.request.query_params
        qs = services.lister_incidents(
            mission=lire_entier(p, "mission"),
            type_incident=p.get("type_incident"),
            du=lire_date(p, "du"),
            au=lire_date(p, "au", fin=True),
        )
        # Restriction par rôle : un proprietaire ne voit que ses incidents.
        if self.request.user.role != "administrateur":
            qs = qs.filter(mission__utilisateur=self.request.user)
        return qs