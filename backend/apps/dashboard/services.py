"""Agrégations en LECTURE SEULE (aucune écriture en base)."""

import pandas as pd
from django.db.models import Count

from apps.irrigation.models import Incident, Irrigation
from apps.mesures.models import MesureHumidite
from apps.missions.models import Mission


def obtenir_evolution_humidite(zone_id):
    """Retourne l'humidité moyenne par jour d'une zone (mesures valides).

    Returns:
        Une liste de dictionnaires {"jour", "humidite_pourcent"}, vide sans mesure.
    """
    lignes = MesureHumidite.objects.filter(zone_id=zone_id, est_valide=True).values(
        "date_mesure", "humidite_pourcent"
    )
    tableau = pd.DataFrame(list(lignes))
    if tableau.empty:
        return []
    tableau["jour"] = pd.to_datetime(tableau["date_mesure"]).dt.date.astype(str)
    moyennes = tableau.groupby("jour")["humidite_pourcent"].mean().round(1)
    return moyennes.reset_index().to_dict("records")


def obtenir_recapitulatif_missions():
    """Retourne le nombre de missions par statut."""
    return list(
        Mission.objects.values("statut").annotate(total=Count("id")).order_by("statut")
    )


def obtenir_resume_global():
    """Retourne les indicateurs d'ensemble du système."""
    volumes = Irrigation.objects.exclude(volume_litres=None).values_list(
        "volume_litres", flat=True
    )
    return {
        "missions": obtenir_recapitulatif_missions(),
        "incidents": Incident.objects.count(),
        "irrigations": Irrigation.objects.count(),
        "volume_litres": sum(volumes),
    }
