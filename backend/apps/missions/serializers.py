"""Validation et format JSON des missions."""

from rest_framework import serializers

from apps.parcelles.models import Zone

from .models import EtapeMission, Mission, StatutMission


class EtapeMissionSerializer(serializers.ModelSerializer):
    """Étape d'une mission."""

    class Meta:
        model = EtapeMission
        fields = ["id", "zone", "ordre"]


class MissionSerializer(serializers.ModelSerializer):
    """Mission avec ses étapes. En création, `zones` donne l'ordre des étapes."""

    etapes = EtapeMissionSerializer(many=True, read_only=True)
    zones = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Zone.objects.all(), write_only=True
    )

    class Meta:
        model = Mission
        fields = [
            "id",
            "statut",
            "duree_prevue_secondes",
            "date_creation",
            "date_recue",
            "date_debut",
            "date_fin",
            "etapes",
            "zones",
        ]
        read_only_fields = [
            "statut",
            "date_creation",
            "date_recue",
            "date_debut",
            "date_fin",
        ]


class ChangementStatutSerializer(serializers.Serializer):
    """Demande de changement de statut."""

    statut = serializers.ChoiceField(choices=StatutMission.choices)
