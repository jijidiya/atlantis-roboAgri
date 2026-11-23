"""Sérialiseurs de l'API « communication ».

Validation du payload envoyé par le robot avant traitement métier.
Le format exact est défini dans `protocole_communication.md` (document E).

Note : la lecture d'un message déjà reçu (`MessageRecu`) n'est pas couverte
ici — le modèle n'existe pas encore dans `models.py`. Quand il sera créé,
ajouter `MessageRecuSerializer` en tête du fichier.
"""
import re

from rest_framework import serializers

from apps.missions.models import Mission
from apps.parcelles.models import Zone


# ---------------------------------------------------------------------------
# Validation d'un message entrant (payload du robot)
# ---------------------------------------------------------------------------

class PayloadMesureSerializer(serializers.Serializer):
    """Payload d'un message de type 'mesure'.

    ⚠️ Champs à confirmer avec protocole_communication.md (E).
    """

    zone = serializers.PrimaryKeyRelatedField(queryset=Zone.objects.all())
    humidite_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=0, max_value=100,
        help_text="Humidité étalonnée en pourcentage (0–100).",
    )
    valeur_brute = serializers.IntegerField(
        min_value=0,
        help_text="Valeur ADC brute, pour diagnostic et recalcul hors ligne.",
    )
    numero_point = serializers.IntegerField(
        min_value=1, max_value=3, required=False,
        help_text="Point de collecte (1 à 3), selon RG7.",
    )
    numero_lecture = serializers.IntegerField(
        min_value=1, max_value=3, required=False,
        help_text="Lecture du point (1 à 3), selon RG7.",
    )


class PayloadEtatSerializer(serializers.Serializer):
    """Payload d'un message de type 'etat'.

    ⚠️ Liste des états à confirmer avec protocole_communication.md (E).
    """

    etat = serializers.ChoiceField(choices=[
        "demarre",
        "en_cours",
        "termine",
        "interrompu",
        "obstacle",
        "batterie_faible",
    ])


class PayloadIncidentSerializer(serializers.Serializer):
    """Payload d'un message de type 'incident'."""

    type_incident = serializers.ChoiceField(choices=[
        "obstacle",
        "capteur_defaillant",
        "perte_communication",
        "mesure_invalide",
    ])


_PAYLOAD_PAR_TYPE = {
    "mesure": PayloadMesureSerializer,
    "etat": PayloadEtatSerializer,
    "incident": PayloadIncidentSerializer,
}


class MessageRobotEntrantSerializer(serializers.Serializer):
    """Validation d'un message entrant du robot.

    Le champ `type` détermine le serializer de payload appliqué. Les champs
    communs (`message_id`, `num_sequence`, `horodatage`) sont validés en premier,
    puis le payload est validé par le sous-serializer correspondant.

    Ce serializer ne fait que valider la **structure**. Une mesure invalide
    (valeur hors plage après contrôle de plausibilité) reste acceptée ici et
    sera marquée `valide=false` par `handlers.traiter_message`.
    """

    message_id = serializers.CharField(
        min_length=16, max_length=16,
        help_text="16 caractères hexadécimaux (anti-doublon, cf. RG10).",
    )
    num_sequence = serializers.IntegerField(
        min_value=1,
        help_text="Compteur d'ordre conservé en flash côté ESP32.",
    )
    type = serializers.ChoiceField(choices=list(_PAYLOAD_PAR_TYPE.keys()))
    horodatage = serializers.DateTimeField(
        help_text="Horodatage ISO 8601 envoyé par le robot.",
    )
    mission = serializers.PrimaryKeyRelatedField(
        queryset=Mission.objects.all(), required=False, allow_null=True,
    )
    payload = serializers.JSONField(
        help_text="Contenu spécifique au type (voir Payload*Serializer).",
    )

    def validate_message_id(self, valeur):
        if not re.fullmatch(r"[0-9a-fA-F]{16}", valeur):
            raise serializers.ValidationError(
                "message_id doit contenir exactement 16 caractères hexadécimaux "
                "(chiffres 0-9 et lettres a-f)."
            )
        return valeur.lower()

    def validate(self, donnees):
        type_message = donnees["type"]
        payload_brut = donnees.get("payload", {})

        serializer_cls = _PAYLOAD_PAR_TYPE[type_message]
        sous = serializer_cls(data=payload_brut)
        sous.is_valid(raise_exception=True)

        donnees["payload"] = sous.validated_data
        return donnees

class MessageRecuSerializer(serializers.ModelSerializer):
"""Représentation d'un message déjà enregistré (lecture seule)."""

mission = serializers.IntegerField(source="mission.mission_id", read_only=True)

class Meta:
    model = MessageRecu
    fields = [
        "message_id", "num_sequence", "type_message",
        "contenu", "date_heure", "mission",
    ]
    read_only_fields = fields