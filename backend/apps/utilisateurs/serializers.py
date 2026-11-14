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


class ProfilModificationSerializer(serializers.ModelSerializer):
    """Modification du profil par l'utilisateur lui-même.

    Champs volontairement restreints : ni rôle, ni actif, ni mot de passe
    (le mot de passe a un endpoint dédié à venir).
    """
    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ["prenom", "nom", "email"]

    def validate_email(self, valeur):
        qs = self.Meta.model.objects.filter(email=valeur)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return valeur