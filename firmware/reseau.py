import urequests as requests
import config
entetes = {
    "X-Cle-Robot": config.jeton_robot,
    "Content-Type": "application/json",
}
def recuperer_mission():
    reponse = None
    try:
        reponse = requests.get(
            config.adresse_api + config.chemin_mission,
            headers=entetes,
            timeout=config.delai_attente,
        )
        if reponse.status_code == 200:
            return reponse.json()
        elif reponse.status_code == 204:
            print("[INFO] Aucune mission pour le moment")
        elif reponse.status_code == 401:
            print("[ERREUR] Jeton du robot refuse (401)")
        else:
            print("[ERREUR] Code HTTP inattendu :", reponse.status_code)
        return None
    except Exception as erreur:
        print("[ERREUR] Echec de communication :", erreur)
        return None
    finally:
        if reponse is not None:
            reponse.close()
def envoyer_message(message):
    reponse = None
    try:
        reponse = requests.post(
            config.adresse_api + config.chemin_messages,
            json=message,
            headers=entetes,
            timeout=config.delai_attente,
        )
        try:
            corps = reponse.json()
        except ValueError:
            corps = None
        return reponse.status_code, corps
    except Exception as erreur:
        print("[ERREUR] Echec de communication :", erreur)
        return None, None
    finally:
        if reponse is not None:
            reponse.close()