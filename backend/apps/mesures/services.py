"""Logique métier des mesures : enregistrement et consultation."""
from django.db import IntegrityError, transaction

from apps.core.exceptions import Conflit

from . import validation
from .models import Mesure


def enregistrer_mesures(message, etape, lectures, maintenant):
    """Valide puis enregistre les lectures d'une étape (RG7, RG8).

    `message` est le Message d'origine ; `lectures` vient de
    communication.protocole. Une mesure invalide est enregistrée avec son
    statut, pas rejetée. Renvoie la liste des Mesure créées.
    """
    mesures = []
    for lecture in lectures:
        verdict = validation.valider_mesure(
            lecture.humidite_pct, lecture.valeur_brute, lecture.horodatage, maintenant
        )
        mesures.append(Mesure(
            numero_point=lecture.numero_point,
            numero_lecture=lecture.numero_lecture,
            valeur_brute=lecture.valeur_brute,
            valeur_humidite=verdict.humidite_a_stocker,
            date_heure_mesure=lecture.horodatage,
            statut=verdict.statut,
            etape=etape,
            message=message,
        ))
    try:
        with transaction.atomic():
            return Mesure.objects.bulk_create(mesures)
    except IntegrityError:
        raise Conflit(
            "Des lectures de cette étape existent déjà.",
            {"etape": etape.pk},
        )


def lister_mesures(zone=None, mission=None, statut=None, du=None, au=None):
    """Mesures filtrées (tous les filtres sont facultatifs). `au` est exclusif."""
    requete = Mesure.objects.select_related("etape")
    if zone is not None:
        requete = requete.filter(etape__zone_id=zone)
    if mission is not None:
        requete = requete.filter(etape__mission_id=mission)
    if statut:
        requete = requete.filter(statut=statut)
    if du is not None:
        requete = requete.filter(date_heure_mesure__gte=du)
    if au is not None:
        requete = requete.filter(date_heure_mesure__lt=au)
    return requete