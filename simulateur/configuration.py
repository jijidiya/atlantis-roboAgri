"""Réglages du simulateur du robot RoboAgri-Kin."""

# Adresse de l'API Django (en local pendant le développement)
adresse_api = "http://127.0.0.1:8000"

# Jeton d'authentification du robot (i.e CLE_ROBOT dans le backend)
jeton_robot = "12340000"   

# Adresses de l'API (protocole v1.1, sans slash final)
chemin_mission = "/api/v1/robot/mission-suivante/"
chemin_messages = "/api/v1/robot/messages/"

# Délai maximal d'attente d'une réponse, en secondes
delai_attente = 25

# Délai entre deux demandes de mission, en secondes
delai_polling = 3

# Durée simulée d'un déplacement entre deux zones, en secondes
duree_deplacement = 2

# Règles de collecte : 3 points par zone, 3 lectures par point
nombre_points = 3
nombre_lectures = 3