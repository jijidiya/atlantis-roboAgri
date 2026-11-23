"""Configuration du firmware ESP32 — capteur d'humidité RÉSISTIF.

⚠️ Contient des secrets (Wi-Fi, jeton robot). Ignoré par Git.
   Modèle versionné : `config.example.py`.
"""


import time
import network
import secrets

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep_ms(300)
wlan.active(True)
wlan.connect(secrets.WIFI_SSID,secrets.WIFI_PASSWORD)

for _ in range(20):
  if wlan.isconnected():
    break
  time.sleep_ms(500)

print("Connecte:", wlan.isconnected(), "Config:", wlan.ifconfig())


# --- API ---
# IP du PC trouvée avec `ipconfig` (section Wi-Fi, ligne « Adresse IPv4 »)
ADRESSE_API = secrets.API_URL

CHEMIN_MISSION = "/api/v1/robot/mission-suivante/"
CHEMIN_MESSAGES = "/api/v1/robot/messages/"

# Jeton robot (identique à CLE_ROBOT dans backend/.env)
JETON_ROBOT = secrets.ROBOT_API_TOKEN


DELAI_ATTENTE = 20     # timeout HTTP
DELAI_POLLING = 3      # entre deux GET mission au repos
PIN_CAPTEUR = 34
PIN_ALIMENTATION = 25

DELAI_STABILISATION_MS = 300
NOMBRE_ECHANTILLONS = 10


DELAI_ECHANTILLON_MS = 30

VALEUR_SEC = 3500      # ADC quand capteur à l'air (0 %)
VALEUR_HUMIDE = 1200   # ADC quand capteur dans l'eau (100 %)


NOMBRE_POINTS = 3
NOMBRE_LECTURES = 3