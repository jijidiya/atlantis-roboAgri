"""Abonné MQTT (squelette). Même fonction que la vue HTTP : traiter_message."""

import json

from .handlers import traiter_message

TOPIC = "roboagri/mesures"


def lors_message(client, userdata, msg):
    try:
        donnees = json.loads(msg.payload)
    except json.JSONDecodeError:
        donnees = {}
    traiter_message(donnees)


def demarrer(hote="localhost", port=1883):
    import paho.mqtt.client as mqtt  # import tardif : dépendance optionnelle

    client = mqtt.Client()
    client.on_message = lors_message
    client.connect(hote, port)
    client.subscribe(TOPIC)
    client.loop_forever()
