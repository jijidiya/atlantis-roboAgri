from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class ResumeView(APIView):
    def get(self, request):
        return Response(services.resume_global())


class EvolutionHumiditeView(APIView):
    def get(self, request, zone_id):
        return Response(services.evolution_humidite(zone_id))
