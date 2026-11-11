"""Sérialiseur des mesures (lecture seule : elles sont créées par le robot)."""
from rest_framework import serializers

from .models import Mesure


class MesureSerializer(serializers.ModelSerializer):
    # Pratiques pour le frontend : on les déduit de l'étape.
    zone = serializers.IntegerField(source="etape.zone_id", read_only=True)
    mission = serializers.IntegerField(source="etape.mission_id", read_only=True)

    class Meta:
        model = Mesure
        fields = [
            "mesure_id", "mission", "zone", "etape", "numero_point",
            "numero_lecture", "valeur_brute", "valeur_humidite",
            "date_heure_mesure", "statut", "message", "incident", "analyse",
        ]
        read_only_fields = fields