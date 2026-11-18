"""Communication HTTP avec l'API Django (protocole v1.1)."""
import requests

import configuration

entetes = {
    "X-Cle-Robot": configuration.jeton_robot,
    "Content-Type": "application/json",
}


def recuperer_mission():
    """Retourne la mission (dictionnaire) ou None s'il n'y en a pas."""
    try:
        reponse = requests.get(
            configuration.adresse_api + configuration.chemin_mission,
            headers=entetes,
            timeout=configuration.delai_attente,
        )
    except requests.RequestException:
        return None
    if reponse.status_code == 200:
        return reponse.json()
    return None  # 204 : pas de mission ; 401 : jeton refusé


def envoyer_message(message):
    """Envoie un message. Retourne (code_http, corps), ou (None, None) si le réseau est coupé."""
    try:
        reponse = requests.post(
            configuration.adresse_api + configuration.chemin_messages,
            json=message,
            headers=entetes,
            timeout=configuration.delai_attente,
        )
    except requests.RequestException:
        return None, None
    try:
        corps = reponse.json()
    except ValueError:
        corps = None
    return reponse.status_code, corps          






    