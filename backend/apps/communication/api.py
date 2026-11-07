"""Vues HTTP du robot (docs/protocole.md, section 5). Vues MINCES.

Toute la logique est dans handlers.py. L'authentification se fait par jeton
(en-tête `Authorization: Token <jeton>`) ; sans jeton valide, la réponse est 401.
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import handlers


class VueRobot(APIView):
    """Base des vues du robot : jeton obligatoire."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class MissionRobotView(VueRobot):
    """GET /api/robot/mission : le robot récupère la mission en attente."""

    def get(self, request):
        """Retourne la mission (200) ou rien (204)."""
        mission = handlers.obtenir_mission_pour_robot()
        if mission is None:
            return Response(status=204)
        return Response(mission)


class MessagesRobotView(VueRobot):
    """POST /api/robot/messages : un message de n'importe quel type."""

    types_acceptes = None

    def post(self, request):
        """Enregistre le message et renvoie la réponse du protocole."""
        resultat = handlers.traiter_message(
            request.data, types_acceptes=self.types_acceptes
        )
        return Response(resultat.corps, status=resultat.code_http)


class EtatRobotView(MessagesRobotView):
    """POST /api/robot/etat : uniquement des messages « changement_etat »."""

    types_acceptes = ("changement_etat",)


class SyncRobotView(VueRobot):
    """POST /api/robot/messages/sync : renvoi groupé de la file après une coupure."""

    def post(self, request):
        """Traite jusqu'à 20 messages, dans l'ordre."""
        resultat = handlers.traiter_lot(request.data)
        return Response(resultat.corps, status=resultat.code_http)
