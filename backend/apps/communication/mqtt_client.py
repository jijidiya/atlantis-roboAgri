"""Abonné MQTT (squelette, phase 2). Même fonction que les vues HTTP.

Topics : docs/protocole.md, section 8.1. Les messages du robot passent par
`handlers.traiter_message`, comme en HTTP ; l'accusé de réception est publié
sur `roboagri/ack` (section 8.2).
"""

import json

from . import protocole
from .handlers import traiter_message

TOPICS_ROBOT = (
    "roboagri/etape",
    "roboagri/mesure",
    "roboagri/etat",
    "roboagri/incident",
)
TOPIC_ACCUSE = "roboagri/ack"


def gerer_message(client, donnees_utilisateur, message_mqtt):
    """Traite un message du robot et publie l'accusé de réception."""
    try:
        donnees = json.loads(message_mqtt.payload)
    except json.JSONDecodeError:
        corps = protocole.construire_reponse_erreur(
            protocole.CODE_MESSAGE_INVALIDE, "JSON invalide"
        )
    else:
        corps = traiter_message(donnees).corps
    client.publish(TOPIC_ACCUSE, json.dumps(corps), qos=1)


def demarrer(hote="localhost", port=1883):
    """Se connecte au broker et écoute les topics du robot (boucle infinie)."""
    import paho.mqtt.client as mqtt  # import tardif : dépendance optionnelle

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = gerer_message
    client.connect(hote, port)
    for topic in TOPICS_ROBOT:
        client.subscribe(topic, qos=1)
    client.loop_forever()
