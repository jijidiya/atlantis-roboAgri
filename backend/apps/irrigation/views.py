"""Vues de l'API « irrigation » : recommandations, interventions, seuils."""
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.filtres import lire_booleen, lire_date, lire_entier
from apps.core.pagination import PaginationStandard
from apps.parcelles.models import Zone

from . import services
from .serializers import (
    DecisionSerializer,
    IrrigationManuelleSerializer,
    IrrigationSerializer,
    ZoneSeuilSerializer,
)


class IrrigationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Historique des interventions + saisie d'une intervention manuelle."""

    serializer_class = IrrigationSerializer
    pagination_class = PaginationStandard
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        p = self.request.query_params
        qs = services.lister_irrigations(
            zone=lire_entier(p, "zone"),
            automatique=lire_booleen(p, "automatique"),
            statut=p.get("statut"),
            du=lire_date(p, "du"),
            au=lire_date(p, "au", fin=True),
        )
        # Restriction par rôle : un proprietaire ne voit que ses irrigations.
        if self.request.user.role != "administrateur":
            qs = qs.filter(zone__parcelle__utilisateur=self.request.user)
        return qs

    def create(self, request):
        """POST /irrigations/ : intervention manuelle (403 ARROSAGE_INTERDIT si refusée)."""
        entree = IrrigationManuelleSerializer(data=request.data, context={"request": request})
        entree.is_valid(raise_exception=True)
        irrigation = services.creer_irrigation_manuelle(**entree.validated_data)
        return Response(IrrigationSerializer(irrigation).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def seuils(self, request):
        """GET /irrigations/seuils/ : seuils d'humidité de chaque zone du user."""
        qs = Zone.objects.all()
        if request.user.role != "administrateur":
            qs = qs.filter(parcelle__utilisateur=request.user)
        return Response(ZoneSeuilSerializer(qs, many=True).data)


class DecisionViewSet(viewsets.ReadOnlyModelViewSet):
    """Décisions d'irrigation. Filtres : ?zone=3&statut=recommandee&du=...&au=..."""

    serializer_class = DecisionSerializer
    pagination_class = PaginationStandard
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        p = self.request.query_params
        qs = services.lister_decisions(
            zone=lire_entier(p, "zone"),
            statut=p.get("statut"),
            du=lire_date(p, "du"),
            au=lire_date(p, "au", fin=True),
        )
        if self.request.user.role != "administrateur":
            qs = qs.filter(analyse__zone__parcelle__utilisateur=self.request.user)
        return qs


class DecisionZoneView(APIView):
    """GET /zones/{id}/decision/ : décision actuelle d'une zone."""

    permission_classes = [IsAuthenticated]

    def get(self, request, zone_id):
        # Vérifie d'abord que la zone appartient au user (sinon 404, pas 403).
        qs_zones = Zone.objects.filter(zone_id=zone_id)
        if request.user.role != "administrateur":
            qs_zones = qs_zones.filter(parcelle__utilisateur=request.user)
        if not qs_zones.exists():
            return Response({"detail": "Zone introuvable."}, status=404)

        return Response(DecisionSerializer(services.derniere_decision(zone_id)).data)