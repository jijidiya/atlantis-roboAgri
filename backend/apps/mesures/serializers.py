"""Format JSON des mesures d'humidité."""

from rest_framework import serializers

from .models import MesureHumidite


class MesureHumiditeSerializer(serializers.ModelSerializer):
    """Mesure d'humidité (lecture seule)."""

    class Meta:
        model = MesureHumidite
        fields = [
            "id",
            "zone",
            "mission",
            "num_sequence",
            "humidite_pourcent",
            "valeur_brute",
            "est_valide",
            "motif_invalidite",
            "date_mesure",
            "est_date_approximative",
            "uptime_ms",
        ]
