"""Validation et format JSON des parcelles, zones et cultures."""

from rest_framework import serializers

from .models import Cultiver, Culture, Parcelle, Zone


class ZoneSerializer(serializers.ModelSerializer):
    """Zone d'une parcelle."""

    class Meta:
        model = Zone
        fields = ["id", "parcelle", "nom", "ordre", "seuil_humidite_pourcent"]


class ParcelleSerializer(serializers.ModelSerializer):
    """Parcelle avec ses zones en lecture seule."""

    zones = ZoneSerializer(many=True, read_only=True)

    class Meta:
        model = Parcelle
        fields = [
            "id",
            "nom",
            "localisation",
            "superficie_m2",
            "date_creation",
            "zones",
        ]
        read_only_fields = ["date_creation"]


class CultureSerializer(serializers.ModelSerializer):
    """Culture."""

    class Meta:
        model = Culture
        fields = ["id", "nom"]


class CultiverSerializer(serializers.ModelSerializer):
    """Association zone-culture, avec contrôle des dates."""

    class Meta:
        model = Cultiver
        fields = ["id", "zone", "culture", "date_debut", "date_fin"]

    def validate(self, donnees):
        """Vérifie que date_fin ne précède pas date_debut."""
        date_fin = donnees.get("date_fin")
        if date_fin and date_fin < donnees["date_debut"]:
            raise serializers.ValidationError("date_fin doit suivre date_debut.")
        return donnees
