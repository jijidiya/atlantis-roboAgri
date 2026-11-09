"""Sérialiseurs de l'application « parcelles » : conversion modèle <-> JSON."""
from rest_framework import serializers

from .models import Culture, Parcelle, Zone


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ["culture_id", "nom", "variete"]


class ZoneSerializer(serializers.ModelSerializer):
    # Cultures de la zone, en lecture seule (le lien se gère via `cultiver`).
    cultures = CultureSerializer(many=True, read_only=True)

    class Meta:
        model = Zone
        fields = [
            "zone_id", "nom", "superficie", "humidite_minimum",
            "humidite_maximum", "geometrie_zone", "irrigation_auto_active",
            "parcelle", "cultures",
        ]

    def validate(self, donnees):
        """Renvoie une erreur 400 claire au lieu d'une erreur de base (500)."""
        minimum = donnees.get("humidite_minimum", getattr(self.instance, "humidite_minimum", None))
        maximum = donnees.get("humidite_maximum", getattr(self.instance, "humidite_maximum", None))
        if minimum is not None and maximum is not None and minimum >= maximum:
            raise serializers.ValidationError(
                "humidite_minimum doit être inférieure à humidite_maximum."
            )
        return donnees


class ParcelleSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)

    class Meta:
        model = Parcelle
        fields = [
            "parcelle_id", "nom", "longitude", "latitude",
            "superficie", "utilisateur", "zones",
        ]