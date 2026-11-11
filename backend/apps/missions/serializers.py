"""Sérialiseurs de l'application « missions » : conversion modèle <-> JSON."""
from django.db import transaction
from rest_framework import serializers

from .models import Etape, Mission


class EtapeSerializer(serializers.ModelSerializer):
    # Le numero_ordre >= 1 : on l'applique ici pour renvoyer
    # une erreur 400 lisible plutôt qu'une erreur de base de données (500).
    numero_ordre = serializers.IntegerField(min_value=1)

    class Meta:
        model = Etape
        fields = ["etape_id", "numero_ordre", "zone", "statut", "date_debut", "date_fin"]
        # Le statut et les dates sont gérés par le système, pas par le frontend.
        read_only_fields = ["etape_id", "statut", "date_debut", "date_fin"]


class MissionSerializer(serializers.ModelSerializer):
    etapes = EtapeSerializer(many=True)

    class Meta:
        model = Mission
        fields = [
            "mission_id", "statut", "date_creation", "date_debut", "date_fin",
            "utilisateur", "parcelle", "etapes",
        ]
        read_only_fields = ["mission_id", "statut", "date_creation", "date_debut", "date_fin"]

    def validate_etapes(self, etapes):
        """RG5 : au moins une étape, et des numéros d'ordre sans doublon."""
        if not etapes:
            raise serializers.ValidationError("Une mission doit comporter au moins une étape.")
        ordres = [etape["numero_ordre"] for etape in etapes]
        if len(ordres) != len(set(ordres)):
            raise serializers.ValidationError("Deux étapes ont le même numero_ordre.")
        return etapes

    def validate(self, donnees):
        """RG5 : chaque zone doit appartenir à la parcelle de la mission.

        La base ne peut pas contrôler cette règle (elle croise deux tables).
        """
        parcelle = donnees["parcelle"]
        for etape in donnees["etapes"]:
            if etape["zone"].parcelle_id != parcelle.pk:
                raise serializers.ValidationError(
                    f"La zone {etape['zone'].pk} n'appartient pas à la parcelle {parcelle.pk}."
                )
        return donnees

    @transaction.atomic
    def create(self, donnees):
        """Crée la mission et ses étapes ensemble : si une étape échoue, rien n'est créé."""
        etapes = donnees.pop("etapes")
        mission = Mission.objects.create(**donnees)
        Etape.objects.bulk_create(Etape(mission=mission, **etape) for etape in etapes)
        return mission