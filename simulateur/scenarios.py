"""Scénarios de panne déclenchables par le robot virtuel."""

SCENARIOS = {
    "nominal": {
        "description": "Mission complète, tout se passe bien",
        "capteur_mode": "normal",
        "obstacle_apres": None,
        "perte_reseau": False,
        "forcer_doublon": False,
    },
    "sol_sec": {
        "description": "Humidité sous le seuil, arrosage recommandé",
        "capteur_mode": "sec",
        "obstacle_apres": None,
        "perte_reseau": False,
        "forcer_doublon": False,
    },
    "sol_humide": {
        "description": "Humidité au-dessus du seuil haut",
        "capteur_mode": "humide",
        "obstacle_apres": None,
        "perte_reseau": False,
        "forcer_doublon": False,
    },
    "capteur_defaillant": {
        "description": "Capteur débranché, mesure invalide + incident",
        "capteur_mode": "defaillant",
        "obstacle_apres": None,
        "perte_reseau": False,
        "forcer_doublon": False,
    },
    "obstacle": {
        "description": "Obstacle détecté à l'étape 1, incident + arrêt",
        "capteur_mode": "normal",
        "obstacle_apres": 1,
        "perte_reseau": False,
        "forcer_doublon": False,
    },
    "perte_reseau": {
        "description": "Coupure Wi-Fi, messages non envoyés",
        "capteur_mode": "normal",
        "obstacle_apres": None,
        "perte_reseau": True,
        "forcer_doublon": False,
    },
    "doublon": {
        "description": "Renvoi du même message_id (test anti-doublon)",
        "capteur_mode": "normal",
        "obstacle_apres": None,
        "perte_reseau": False,
        "forcer_doublon": True,
    },
}