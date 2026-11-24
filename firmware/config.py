"""Configuration du firmware ESP32 - RoboAgri-Kin.

Les secrets (Wi-Fi, IP, jeton) sont importes depuis `secrets.py`.
Ce fichier peut etre versionne sur Git sans risque.
"""
import secrets

# --- Secrets importes (pour que le reste du code utilise config.XXX) ---
WIFI_SSID = secrets.WIFI_SSID
WIFI_PASSWORD = secrets.WIFI_PASSWORD
ADRESSE_API = secrets.ADRESSE_API
JETON_ROBOT = secrets.JETON_ROBOT

# --- API Chemins ---
CHEMIN_MISSION = "/api/v1/robot/mission-suivante/"
CHEMIN_MESSAGES = "/api/v1/robot/messages/"

# --- Delais (secondes) ---
DELAI_ATTENTE = 20
DELAI_POLLING = 3
DELAI_MESURE = 0.1

# --- Capteur d'humidite ---
PIN_CAPTEUR = 34
PIN_ALIMENTATION = 25
DELAI_STABILISATION_MS = 300
NOMBRE_ECHANTILLONS = 10
DELAI_ECHANTILLON_MS = 30

# --- Etalonnage ---
VALEUR_SEC = 3500
VALEUR_HUMIDE = 1200

# --- Collecte (RG7) ---
NOMBRE_POINTS = 3
NOMBRE_LECTURES = 3