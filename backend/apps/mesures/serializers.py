from rest_framework import serializers

from .models import Mesure


class MesureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesure
        fields = [
            "id", "zone", "mission", "sequence", "humidite",
            "mesuree_le", "valide", "motif_invalidite",
        ]
        read_only_fields = ["valide", "motif_invalidite"]
