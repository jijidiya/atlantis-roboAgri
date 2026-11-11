"""Logique métier des incidents.

Seuls `irrigation` et `communication` créent des incidents, via
`signaler_incident` (architecture.pdf §3.3).
"""
from django.utils import timezone

from apps.mesures.models import Mesure

from .models import Incident


def signaler_incident(type_incident, mission=None, mesures=(), date_incident=None):
    """Crée un incident et le lie aux mesures concernées (RG11)."""
    incident = Incident.objects.create(
        type_incident=type_incident,
        mission=mission,
        date_incident=date_incident or timezone.now(),
    )
    identifiants = [mesure.pk for mesure in mesures]
    if identifiants:
        Mesure.objects.filter(pk__in=identifiants).update(incident=incident)
    return incident


def lister_incidents(mission=None, type_incident=None, du=None, au=None):
    """Incidents filtrés (tous les filtres sont facultatifs). `au` est exclusif."""
    requete = Incident.objects.prefetch_related("mesures")
    if mission is not None:
        requete = requete.filter(mission_id=mission)
    if type_incident:
        requete = requete.filter(type_incident=type_incident)
    if du is not None:
        requete = requete.filter(date_incident__gte=du)
    if au is not None:
        requete = requete.filter(date_incident__lt=au)
    return requete