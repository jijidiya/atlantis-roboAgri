"""Agrégations en LECTURE SEULE (aucune écriture en base)."""

import pandas as pd
from django.db.models import Count

from apps.irrigation.models import Incident, Irrigation
from apps.mesures.models import Mesure
from apps.missions.models import Mission


def evolution_humidite(zone_id):
    lignes = Mesure.objects.filter(zone_id=zone_id, valide=True).values("mesuree_le", "humidite")
    df = pd.DataFrame(list(lignes))
    if df.empty:
        return []
    df["jour"] = pd.to_datetime(df["mesuree_le"]).dt.date.astype(str)
    return df.groupby("jour")["humidite"].mean().round(1).reset_index().to_dict("records")


def recapitulatif_missions():
    return list(Mission.objects.values("statut").annotate(total=Count("id")).order_by("statut"))


def resume_global():
    return {
        "missions": recapitulatif_missions(),
        "incidents": Incident.objects.count(),
        "irrigations": Irrigation.objects.count(),
        "volume_litres": sum(
            Irrigation.objects.exclude(volume_litres=None).values_list("volume_litres", flat=True)
        ),
    }
