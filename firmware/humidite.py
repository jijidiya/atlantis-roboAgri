
import config
import time

try:
    from machine import ADC, Pin
    SUR_ESP32 = True
except ImportError:
    SUR_ESP32 = False  
    import random

if SUR_ESP32:
    adc = ADC(Pin(config.BROCHE_HUMIDITE))
    adc.atten(ADC.ATTN_11DB)  
    alim = Pin(config.BROCHE_ALIM_HUMIDITE, Pin.OUT, value=0)


def allumer_capteur():
    """Alimente le capteur et attend que le signal se stabilise."""
    if SUR_ESP32:
        alim.value(1)
        time.sleep_ms(config.DELAI_STABILISATION_MS)


def eteindre_capteur():
    """Coupe l'alimentation (limite la corrosion de la sonde)."""
    if SUR_ESP32:
        alim.value(0)


def lire_brut():
    """Une lecture brute du capteur (0 à 4095)."""
    if SUR_ESP32:
        return adc.read()
    return random.randint(1200, 2800) 


def mediane(valeurs):
    v = sorted(valeurs)
    return v[len(v) // 2]


def mesurer():
    """Retourne (valeur_brute, humidite_pct, valide)."""
    allumer_capteur()
    try:
        lectures = [lire_brut() for _ in range(config.NB_LECTURES)]
    finally:
        eteindre_capteur()  
    brut = mediane(lectures)
    if brut < config.BRUT_MIN_VALIDE or brut > config.BRUT_MAX_VALIDE:
        return brut, None, False  
    pct = (config.BRUT_SEC - brut) / (config.BRUT_SEC - config.BRUT_EAU) * 100
    pct = max(0.0, min(100.0, pct))
    return brut, round(pct, 1), True