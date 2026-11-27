"""Tests de l'API d'authentification : connexion, rafraîchissement, profil."""
import pytest
from rest_framework.test import APIClient

CONNEXION = "/api/v1/auth/connexion/"
RAFRAICHIR = "/api/v1/auth/rafraichir/"
MOI = "/api/v1/auth/moi/"


def identifiants(email="test@exemple.cd", mot_de_passe="mdp-test"):
    return {"email": email, "mot_de_passe": mot_de_passe}


def client_avec_jeton(acces):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {acces}")
    return client


def test_connexion_valide_renvoie_les_deux_jetons(api_anonyme, utilisateur):
    reponse = api_anonyme.post(CONNEXION, identifiants(), format="json")

    assert reponse.status_code == 200
    assert reponse.data["acces"]
    assert reponse.data["rafraichissement"]
    assert reponse.data["utilisateur"] == {
        "id": utilisateur.pk,
        "email": "test@exemple.cd",
        "nom": "Test",
        "prenom": "Un",
        "role": "proprietaire",
    }


def test_connexion_avec_mot_de_passe_faux_refusee(api_anonyme, utilisateur):
    reponse = api_anonyme.post(
        CONNEXION, identifiants(mot_de_passe="mauvais-mdp"), format="json"
    )

    assert reponse.status_code == 401
    assert reponse.data["erreur"]["code"] == "IDENTIFIANTS_INVALIDES"
    assert "acces" not in reponse.data


def test_connexion_avec_email_inconnu_refusee(api_anonyme, db):
    reponse = api_anonyme.post(
        CONNEXION, identifiants(email="inconnu@exemple.cd"), format="json"
    )

    assert reponse.status_code == 401
    assert reponse.data["erreur"]["code"] == "IDENTIFIANTS_INVALIDES"


def test_connexion_champs_manquants_renvoie_400(api_anonyme, db):
    reponse = api_anonyme.post(CONNEXION, {"email": "test@exemple.cd"}, format="json")

    assert reponse.status_code == 400


@pytest.mark.django_db
def test_rafraichissement_renvoie_un_jeton_utilisable(api_anonyme, utilisateur):
    jetons = api_anonyme.post(CONNEXION, identifiants(), format="json").data

    reponse = api_anonyme.post(
        RAFRAICHIR, {"rafraichissement": jetons["rafraichissement"]}, format="json"
    )

    assert reponse.status_code == 200
    assert reponse.data["acces"]

    profil = client_avec_jeton(reponse.data["acces"]).get(MOI)
    assert profil.status_code == 200
    assert profil.data["email"] == utilisateur.email


def test_rafraichissement_invalide_renvoie_401(api_anonyme, db):
    reponse = api_anonyme.post(
        RAFRAICHIR, {"rafraichissement": "pas-un-jeton"}, format="json"
    )

    assert reponse.status_code == 401
    assert reponse.data["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_rafraichissement_sans_jeton_renvoie_400(api_anonyme, db):
    reponse = api_anonyme.post(RAFRAICHIR, {}, format="json")

    assert reponse.status_code == 400


def test_moi_renvoie_le_profil_connecte(api, utilisateur):
    reponse = api.get(MOI)

    assert reponse.status_code == 200
    assert reponse.data == {
        "id": utilisateur.pk,
        "email": "test@exemple.cd",
        "nom": "Test",
        "prenom": "Un",
        "role": "proprietaire",
    }


def test_moi_sans_jeton_renvoie_401(api_anonyme, db):
    reponse = api_anonyme.get(MOI)

    assert reponse.status_code == 401
