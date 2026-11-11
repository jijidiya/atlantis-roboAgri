"""API réservée au robot (clé secrète dans l'en-tête X-Cle-Robot).

Ces vues ne font qu'appeler `handlers.traiter_message` : HTTP aujourd'hui,
MQTT demain, le traitement reste le même.
"""
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import EstRobot
from apps.missions import services as missions_services
from apps.missions.serializers import MissionSerializer

from . import handlers


class _VueRobot(APIView):
    authentication_classes = []        # le robot n'a pas de jeton JWT
    permission_classes = [EstRobot]
    parser_classes = [JSONParser]


class MessageRobotView(_VueRobot):
    """POST /robot/messages/ : tous les types de messages (mesure, etat, incident).

    201 : message traité. 200 avec "deja_recu": true : message déjà connu.
    Une mesure invalide donne aussi 201 (avec "valide": false et un incident).
    """

    def post(self, request):
        resultat = handlers.traiter_message(request.data)
        return Response(resultat.en_dict(), status=200 if resultat.deja_recu else 201)


class MissionSuivanteView(_VueRobot):
    """GET /robot/mission-suivante/ : mission à exécuter, ou 204 s'il n'y en a pas."""

    def get(self, request):
        mission = missions_services.mission_suivante()
        if mission is None:
            return Response(status=204)
        return Response(MissionSerializer(mission).data)