from rest_framework import serializers

from .models import EtapeMission, Mission, StatutMission


class EtapeMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapeMission
        fields = ["id", "zone", "ordre"]


class MissionSerializer(serializers.ModelSerializer):
    etapes = EtapeMissionSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ["id", "statut", "prevue_le", "debutee_le", "terminee_le", "etapes"]
        read_only_fields = ["statut", "debutee_le", "terminee_le"]


class ChangementStatutSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=StatutMission.choices)
