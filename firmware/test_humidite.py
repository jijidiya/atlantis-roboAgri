"""Test du capteur d'humidité résistif — sans Wi-Fi, sans API.

Affiche la valeur brute lue sur la broche ADC toutes les secondes.
À exécuter dans Thonny (F5) sur l'ESP32.

Ctrl+C pour arrêter.
"""
import time
from machine import ADC, Pin

capteur = ADC(Pin(34))
capteur.atten(ADC.ATTN_11DB)


while True:
    brut = capteur.read()
    print("brut =", brut)
    time.sleep(3)