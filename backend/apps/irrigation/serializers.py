from rest_framework import serializers

from .models import Incident, Irrigation


class IrrigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Irrigation
        fields = [
            "id", "zone", "mesure", "type", "decision",
            "declenchee_le", "duree_secondes", "volume_litres",
        ]


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ["id", "zone", "mission", "type", "description", "cree_le"]
