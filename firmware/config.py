"""Configuration du firmware ESP32 — capteur d'humidité RÉSISTIF.

⚠️ Contient des secrets (Wi-Fi, jeton robot). Ignoré par Git.
   Modèle versionné : `config.example.py`.
"""
WIFI_SSID = "MonHotspot"
WIFI_PASSWORD = "MotDePasseWifi"

ADRESSE_API = "http:// 192.168.1.244:8000"

CHEMIN_MISSION = "/api/v1/robot/mission-suivante/"
CHEMIN_MESSAGES = "/api/v1/robot/messages/"


JETON_ROBOT = "12340000"


DELAI_ATTENTE = 20   
DELAI_POLLING = 3      
PIN_CAPTEUR = 34
PIN_ALIMENTATION = 25

DELAI_STABILISATION_MS = 300
NOMBRE_ECHANTILLONS = 10


DELAI_ECHANTILLON_MS = 30

VALEUR_SEC = 3500      
VALEUR_HUMIDE = 1200   


NOMBRE_POINTS = 3
NOMBRE_LECTURES = 3