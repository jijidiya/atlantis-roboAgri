"""Sérialiseur des incidents (lecture seule)."""
from rest_framework import serializers

from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    # Identifiants des mesures liées à l'incident (RG11).
    mesures = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Incident
        fields = ["incident_id", "type_incident", "date_incident", "mission", "mesures"]
        read_only_fields = fields
#Sabin est passé par là