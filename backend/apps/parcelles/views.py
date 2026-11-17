"""Vues de l'API « parcelles » : lister, créer, consulter, modifier (RF01)."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Culture, Parcelle, Zone
from .serializers import CultureSerializer, ParcelleSerializer, ZoneSerializer


class ParcelleViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Un administrateur voit tout ; un proprietaire, seulement ses parcelles."""
        requete = Parcelle.objects.prefetch_related("zones__cultures")
        if self.request.user.role == "administrateur":
            return requete
        return requete.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        """Force utilisateur = utilisateur connecté (sauf admin qui peut cibler)."""
        if self.request.user.role == "administrateur" and "utilisateur" in serializer.validated_data:
            serializer.save()
        else:
            serializer.save(utilisateur=self.request.user)


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtre par parcelle (?parcelle=1) ET restreint aux zones accessibles."""
        requete = Zone.objects.prefetch_related("cultures")

        # Restriction par rôle : les zones d'un proprietaire sont celles de ses parcelles.
        if self.request.user.role != "administrateur":
            requete = requete.filter(parcelle__utilisateur=self.request.user)

        parcelle = self.request.query_params.get("parcelle")
        return requete.filter(parcelle_id=parcelle) if parcelle else requete


class CultureViewSet(viewsets.ModelViewSet):
    queryset = Culture.objects.all()
    serializer_class = CultureSerializer
    permission_classes = [IsAuthenticated]