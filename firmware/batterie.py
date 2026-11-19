
import config

try:
    from machine import ADC, Pin
    SUR_ESP32 = True
except ImportError:
    SUR_ESP32 = False  
    import random

if SUR_ESP32:
    adc = ADC(Pin(config.BROCHE_BATTERIE))
    adc.atten(ADC.ATTN_11DB)  


def lire_brut():
    """Une lecture brute de l'ADC (0 à 4095)."""
    if SUR_ESP32:
        return adc.read()
    return random.randint(1500, 2500)  


def lire_tension():
    """Tension réelle de la batterie en volts (après le pont diviseur)."""
    lectures = sorted(lire_brut() for _ in range(config.NB_LECTURES_BATT))
    brut = lectures[len(lectures) // 2]
    tension_adc = brut / 4095 * 3.3
    return round(tension_adc * config.RAPPORT_DIVISEUR, 2)


def pourcentage(tension):
    """Niveau de la batterie en % (calcul linéaire simple, approximatif)."""
    plage = config.TENSION_BATT_MAX - config.TENSION_BATT_MIN
    pct = (tension - config.TENSION_BATT_MIN) / plage * 100
    return round(max(0.0, min(100.0, pct)), 0)


def est_faible():
    """True si la batterie est sous le seuil d'alerte."""
    return pourcentage(lire_tension()) < config.SEUIL_BATTERIE_FAIBLE