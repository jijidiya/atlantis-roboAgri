"""Format JSON des irrigations et des incidents."""

from rest_framework import serializers

from .models import Incident, Irrigation


class IrrigationSerializer(serializers.ModelSerializer):
    """Irrigation (lecture seule)."""

    class Meta:
        model = Irrigation
        fields = [
            "id",
            "zone",
            "mesure",
            "type",
            "decision",
            "date_declenchement",
            "duree_secondes",
            "volume_litres",
        ]


class IncidentSerializer(serializers.ModelSerializer):
    """Incident (lecture seule)."""

    class Meta:
        model = Incident
        fields = [
            "id",
            "code",
            "gravite",
            "description",
            "zone",
            "mission",
            "nb_perdus",
            "date_incident",
            "date_creation",
        ]
