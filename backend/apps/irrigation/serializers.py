"""Sérialiseurs de l'API « irrigation »."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.parcelles.models import Zone

from .models import Decision, Irrigation


class DecisionSerializer(serializers.ModelSerializer):
    # Déduits de l'analyse à l'origine de la décision.
    zone = serializers.IntegerField(source="analyse.zone_id", read_only=True)
    humidite_moyenne = serializers.DecimalField(
        source="analyse.humidite_moyenne", max_digits=5, decimal_places=2,
        read_only=True, allow_null=True,
    )

    class Meta:
        model = Decision
        fields = [
            "decision_id", "zone", "type_decision", "action", "justification",
            "humidite_moyenne", "seuil_min_applique", "seuil_max_applique",
            "statut", "date_decision", "analyse",
        ]
        read_only_fields = fields


class IrrigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Irrigation
        fields = [
            "irrigation_id", "zone", "automatique", "statut", "duree_secondes",
            "volume_ml", "date_debut", "date_fin", "decision", "utilisateur",
        ]
        read_only_fields = fields


class IrrigationManuelleSerializer(serializers.Serializer):
    """Données d'une intervention saisie par l'utilisateur (POST /irrigations/)."""

    zone = serializers.PrimaryKeyRelatedField(queryset=Zone.objects.all())
    duree_secondes = serializers.IntegerField(min_value=1)
    volume_ml = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, allow_null=True
    )
    date_debut = serializers.DateTimeField(required=False, allow_null=True)
    # Facultatif si l'utilisateur est connecté (jeton JWT) : on prend alors request.user.
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False
    )

    def validate(self, donnees):
        requete = self.context.get("request")
        if requete is not None and requete.user and requete.user.is_authenticated:
            donnees["utilisateur"] = requete.user
        elif "utilisateur" not in donnees:
            raise serializers.ValidationError(
                {"utilisateur": "Obligatoire si vous n'êtes pas connecté."}
            )
        return donnees


class ZoneSeuilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = [
            "zone_id", "nom", "parcelle", "humidite_minimum",
            "humidite_maximum", "irrigation_auto_active",
        ]
        read_only_fields = fields