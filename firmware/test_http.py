import network
import time
import urequests
import config
import gc

print("--- 1. CONNEXION WI-FI ---")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    for i in range(30):
        if wlan.isconnected():
            break

        print("Connexion en cours...", i + 1)
        time.sleep(1)

if not wlan.isconnected():
    print("[ECHEC] Connexion Wi-Fi impossible")
    print("Statut :", wlan.status())
else:
    print("[OK] Wi-Fi connecté")
    print("Configuration :", wlan.ifconfig())

    print("\n--- 2. TEST DJANGO ---")

    url = config.ADRESSE_API + "/api/docs/"

    try:
        gc.collect()
        response = urequests.get(url)

        print("[OK] Requête envoyée")
        print("Code HTTP :", response.status_code)

        response.close()

    except Exception as e:
        print("[ERREUR HTTP]", repr(e))

    gc.collect()
