
import network
import time
import config
import secrets

wlan = network.WLAN(network.STA_IF)


def connecter(delai_max_s=15):
    """Tente de se connecter au Wi-Fi. Retourne True si connecté."""
    wlan.active(True)
    if wlan.isconnected():
        return True
    print("Wi-Fi : connexion à", secrets.WIFI_SSID)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    debut = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), debut) > delai_max_s * 1000:
            print("Wi-Fi : échec, délai dépassé")
            return False
        time.sleep_ms(200)
    print("Wi-Fi : connecté, IP =", wlan.ifconfig()[0])
    return True


def est_connecte():
    return wlan.isconnected()


def assurer_connexion():
    """À appeler régulièrement dans la boucle : reconnecte si besoin."""
    if wlan.isconnected():
        return True
    print("Wi-Fi : connexion perdue, nouvel essai")
    return connecter()


def tester_serveur():
    """Test : contacte la route /api/ping/ du serveur. Retourne True si OK."""
    try:
        import urequests
        reponse = urequests.get(config.URL_SERVEUR + "/api/ping/")
        code = reponse.status_code
        reponse.close()
        print("Serveur : réponse", code)
        return code == 200
    except Exception as erreur:
        print("Serveur : injoignable,", erreur)
        return False
