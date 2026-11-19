"""Capteur d'humidité virtuel : génère des lectures plausibles ou aberrantes.

Produit exactement le format attendu par le backend :
    {"numero_point": 1..3, "numero_lecture": 1..3,
     "valeur_brute": int, "humidite": float}

Modes disponibles :
    normal       humidité autour d'une valeur de base, avec bruit
    sec          humidité sous le seuil bas de la zone (déclenche arrosage)
    humide       humidité au-dessus du seuil haut
    defaillant   valeurs hors plage (capteur débranché)
"""
import random

import configuration


class CapteurVirtuel:
    """Génère les lectures d'une étape (nombre_points x nombre_lectures)."""

    def __init__(self, humidite_base=42.0, bruit=2.0, mode="normal"):
        self.humidite_base = humidite_base
        self.bruit = bruit
        self.mode = mode

    def _lire_valeur(self):
        """Retourne (valeur_brute, humidite_pct) pour une lecture."""
        if self.mode == "defaillant":
            # Capteur débranché : ADC sature, pourcentage hors plage
            return 4095, 150.0

        if self.mode == "sec":
            humidite = 15.0 + random.uniform(-self.bruit, self.bruit)
        elif self.mode == "humide":
            humidite = 85.0 + random.uniform(-self.bruit, self.bruit)
        else:
            humidite = self.humidite_base + random.uniform(-self.bruit, self.bruit)

        humidite = max(0.0, min(100.0, humidite))
        # ADC 12 bits : 0-4095, proportionnel au pourcentage
        valeur_brute = int(humidite * 40.95)
        return valeur_brute, round(humidite, 2)

    def lire_etape(self):
        """Retourne les lectures d'une étape (configuration.nombre_points x
        configuration.nombre_lectures)."""
        lectures = []
        for numero_point in range(1, configuration.nombre_points + 1):
            for numero_lecture in range(1, configuration.nombre_lectures + 1):
                valeur_brute, humidite = self._lire_valeur()
                lectures.append({
                    "numero_point": numero_point,
                    "numero_lecture": numero_lecture,
                    "valeur_brute": valeur_brute,
                    "humidite_pct": humidite,
                })
        return lectures