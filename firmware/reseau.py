"""Client HTTP pour l'ESP32 — RoboAgri-Kin."""
import gc
import urequests
import config

entetes = {
    "X-Cle-Robot": config.JETON_ROBOT,
    "Content-Type": "application/json",
}


def _lire_extrait(reponse, taille=200):
    try:
        if getattr(reponse, "raw", None):
            return reponse.raw.read(taille) or b""
    except Exception as err:
        return str(err).encode()
    return b""


def recuperer_mission():
    """Retourne la mission (dict) ou None."""
    gc.collect()
    reponse = None
    try:
        reponse = urequests.get(
            config.ADRESSE_API + config.CHEMIN_MISSION,
            headers=entetes,
            timeout=config.DELAI_ATTENTE,
        )
        code = reponse.status_code
        if code == 200:
            try:
                return reponse.json()
            except MemoryError:
                print("[ERREUR] Réponse JSON trop volumineuse pour la RAM")
                return None
        elif code == 204:
            print("[INFO] Aucune mission pour le moment")
        elif code in (401, 403):
            print("[ERREUR] Jeton du robot refuse (", code, ")")
        else:
            print("[ERREUR] Code HTTP inattendu :", code, "extrait :", _lire_extrait(reponse))
        return None
    except Exception as erreur:
        print("[ERREUR] Echec de communication :", erreur)
        return None
    finally:
        if reponse is not None:
            try:
                reponse.close()
            except Exception:
                pass
        gc.collect()


def envoyer_message(message):
    """Envoie un message au backend. Retourne (code, corps)."""
    gc.collect()
    reponse = None
    try:
        reponse = urequests.post(
            config.ADRESSE_API + config.CHEMIN_MESSAGES,
            json=message,
            headers=entetes,
            timeout=config.DELAI_ATTENTE,
        )
        code = reponse.status_code
        try:
            corps = reponse.json()
        except Exception:
            corps = None
        return code, corps
    except Exception as erreur:
        print("[ERREUR] Echec de communication :", erreur)
        return None, None
    finally:
        if reponse is not None:
            try:
                reponse.close()
            except Exception:
                pass
        gc.collect()


def tester_connexion():
    """Vérifie que le backend est joignable et que le jeton est bon."""
    gc.collect()
    print("Backend :", config.ADRESSE_API)
    print("Jeton   :", "*" * (len(config.JETON_ROBOT) - 2) + config.JETON_ROBOT[-2:])
    print()

    url = config.ADRESSE_API + config.CHEMIN_MISSION
    print("Test GET", url)

    r = None
    try:
        r = urequests.get(url, headers=entetes, timeout=config.DELAI_ATTENTE)
    except Exception as e:
        print("  ECHEC :", e)
        print("  -> verifier IP, pare-feu Windows, Wi-Fi, runserver 0.0.0.0")
        gc.collect()
        return False

    try:
        if r.status_code in (200, 204):
            print("  OK :", r.status_code)
            return True
        if r.status_code in (401, 403):
            print("  ECHEC :", r.status_code, "-> jeton robot invalide")
            return False

        extrait = _lire_extrait(r, 200)
        print("  ECHEC :", r.status_code, "corps :", extrait)
        return False
    finally:
        if r is not None:
            try:
                r.close()
            except Exception:
                pass
        gc.collect()