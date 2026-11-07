"""Vues du tableau de bord : lecture seule."""

from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class ResumeView(APIView):
    """Indicateurs d'ensemble."""

    def get(self, request):
        """Retourne le résumé global."""
        return Response(services.obtenir_resume_global())


class EvolutionHumiditeView(APIView):
    """Évolution de l'humidité d'une zone."""

    def get(self, request, zone_id):
        """Retourne l'humidité moyenne par jour de la zone."""
        return Response(services.obtenir_evolution_humidite(zone_id))
