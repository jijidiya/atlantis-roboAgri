"""Vues de l'API d'authentification : connexion, rafraîchissement, utilisateur courant."""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    ConnexionSerializer,
    ProfilModificationSerializer,
    RafraichissementSerializer,
    UtilisateurConnecteSerializer,
)


class ConnexionAPIView(APIView):
    """POST /auth/connexion/ -> jetons d'accès et de rafraîchissement."""

    permission_classes = [AllowAny]
    # Aucune authentification : un ancien jeton expiré dans l'en-tête ne doit pas
    # faire échouer la connexion (DRF le vérifierait avant d'entrer dans la vue).
    authentication_classes = []

    def post(self, request):
        entree = ConnexionSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        utilisateur, acces, rafraichissement = services.connecter(
            request, entree.validated_data["email"], entree.validated_data["mot_de_passe"]
        )
        return Response(
            {
                "acces": acces,
                "rafraichissement": rafraichissement,
                "utilisateur": UtilisateurConnecteSerializer(utilisateur).data,
            },
            status=status.HTTP_200_OK,
        )


class RafraichissementAPIView(APIView):
    """POST /auth/rafraichir/ -> nouveau jeton d'accès."""

    permission_classes = [AllowAny]
    # Le frontend envoie ici son jeton d'accès EXPIRÉ : il ne faut pas le contrôler,
    # sinon le rafraîchissement serait toujours refusé en 401.
    authentication_classes = []

    def post(self, request):
        entree = RafraichissementSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        return Response(entree.validated_data, status=status.HTTP_200_OK)

class MoiAPIView(APIView):
    """GET /auth/moi/ : profil courant. PATCH /auth/moi/ : modifier prenom/nom/email."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UtilisateurConnecteSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfilModificationSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UtilisateurConnecteSerializer(request.user).data)