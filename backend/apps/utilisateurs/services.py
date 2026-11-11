"""Logique métier de l'authentification."""
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import IdentifiantsInvalides


def connecter(requete, email, mot_de_passe):
    """Vérifie les identifiants et renvoie l'utilisateur et ses deux jetons.

    Le même message sert pour un e-mail inconnu, un mauvais mot de passe et un
    compte désactivé : on ne révèle pas quel cas s'applique.
    """
    utilisateur = authenticate(requete, email=email, password=mot_de_passe)
    if utilisateur is None or not utilisateur.actif:
        raise IdentifiantsInvalides("Adresse e-mail ou mot de passe incorrect.")
    rafraichissement = RefreshToken.for_user(utilisateur)
    return utilisateur, str(rafraichissement.access_token), str(rafraichissement)