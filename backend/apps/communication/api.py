from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .handlers import traiter_message


class MessageRobotView(APIView):
    """Vue MINCE : aucune logique, tout passe par handlers.traiter_message."""

    def post(self, request):
        resultat = traiter_message(request.data)
        code = status.HTTP_400_BAD_REQUEST if resultat.statut == "rejete" else status.HTTP_200_OK
        return Response({"statut": resultat.statut, "detail": resultat.detail}, status=code)
