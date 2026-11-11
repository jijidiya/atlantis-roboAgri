"""Sérialiseurs de l'API d'authentification."""
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.core.exceptions import NonAuthentifie


class ConnexionSerializer(serializers.Serializer):
    # Le modèle Utilisateur utilise l'e-mail comme identifiant de connexion.
    email = serializers.EmailField(required=False)
    # Alias accepté : api-frontend-backend.pdf §3 nomme ce champ « nom_utilisateur ».
    nom_utilisateur = serializers.EmailField(required=False)
    mot_de_passe = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, donnees):
        email = donnees.get("email") or donnees.get("nom_utilisateur")
        if not email:
            raise serializers.ValidationError({"email": "L'adresse e-mail est obligatoire."})
        donnees["email"] = email
        return donnees


class RafraichissementSerializer(serializers.Serializer):
    rafraichissement = serializers.CharField()

    def validate(self, donnees):
        serializer = TokenRefreshSerializer(data={"refresh": donnees["rafraichissement"]})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            # Jeton falsifié, expiré ou mal formé : 401 (et non une erreur 500).
            raise NonAuthentifie("Jeton de rafraîchissement invalide ou expiré.")
        resultat = serializer.validated_data
        return {
            "acces": resultat["access"],
            "rafraichissement": resultat.get("refresh", donnees["rafraichissement"]),
        }


class UtilisateurConnecteSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="utilisateur_id")
    email = serializers.EmailField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    role = serializers.CharField()