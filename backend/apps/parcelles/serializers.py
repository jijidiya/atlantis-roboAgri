from rest_framework import serializers

from .models import Culture, Cultiver, Parcelle, Zone


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ["id", "parcelle", "nom", "ordre", "seuil_humidite"]


class ParcelleSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)

    class Meta:
        model = Parcelle
        fields = ["id", "nom", "localisation", "superficie_m2", "cree_le", "zones"]
        read_only_fields = ["cree_le"]


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ["id", "nom"]


class CultiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cultiver
        fields = ["id", "zone", "culture", "date_debut", "date_fin"]

    def validate(self, data):
        fin = data.get("date_fin")
        if fin and fin < data["date_debut"]:
            raise serializers.ValidationError("date_fin doit suivre date_debut.")
        return data
