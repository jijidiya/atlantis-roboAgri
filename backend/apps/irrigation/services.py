"""Logique métier de l'irrigation : décision après une mesure, intervention manuelle."""
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from apps.analyse.models import Analyse
from apps.core.exceptions import ArrosageInterdit, RessourceIntrouvable
from apps.incidents import services as incidents_services
from apps.mesures.models import Mesure
from apps.parcelles.models import Zone

from . import decision as regle_decision
from . import securite
from .models import Decision, Irrigation

# état de la règle pure -> type_decision du MPD
TYPE_PAR_ETAT = {
    "suffisante": "humidite_suffisante",
    "insuffisante": "humidite_insuffisante",
    "invalide": "mesure_invalide",
}


def _age_max_mesure():
    return getattr(settings, "AGE_MAX_MESURE_SECONDES", 1800)


def _duree_max_irrigation():
    return getattr(settings, "DUREE_MAX_IRRIGATION_SECONDES", 300)


def evaluer_zone(etape, mesures, maintenant=None):
    """Analyse les mesures d'une étape, décide, et signale un incident si besoin.

    Crée une Analyse (statistiques), une Decision (RG13 : les seuils sont copiés
    depuis la zone) et, si la règle l'exige, un Incident (RG17).
    Renvoie (decision, incident ou None).
    """
    maintenant = maintenant or timezone.now()
    zone = etape.zone
    valides = [m for m in mesures if m.statut == "valide"]
    humidites = [m.valeur_humidite for m in valides]
    moyenne = (sum(humidites) / len(humidites)).quantize(Decimal("0.01")) if humidites else None
    dates = [m.date_heure_mesure for m in mesures]

    # Une seule mesure douteuse suffit à invalider l'ensemble (RG17).
    tout_valide = bool(mesures) and len(valides) == len(mesures)
    age = (maintenant - max(dates)).total_seconds() if dates else None
    verdict = regle_decision.decider(
        moyenne, tout_valide, zone.humidite_minimum, age, _age_max_mesure()
    )

    analyse = Analyse.objects.create(
        periode_debut=min(dates),
        periode_fin=max(dates),
        humidite_moyenne=moyenne,
        humidite_minimum=min(humidites) if humidites else None,
        humidite_maximum=max(humidites) if humidites else None,
        nombre_mesures=len(mesures),
        resultat_analyse=verdict.motif,
        zone=zone,
    )
    Mesure.objects.filter(pk__in=[m.pk for m in mesures]).update(analyse=analyse)

    decision = Decision.objects.create(
        type_decision=TYPE_PAR_ETAT[verdict.etat],
        action="arroser" if verdict.arrosage_recommande else "ne_pas_arroser",
        justification=verdict.motif,
        seuil_min_applique=zone.humidite_minimum,
        seuil_max_applique=zone.humidite_maximum,
        statut="recommandee" if verdict.arrosage_recommande else "refusee",
        analyse=analyse,
    )

    incident = None
    if verdict.incident:
        concernees = [m for m in mesures if m.statut != "valide"] or list(mesures)
        incident = incidents_services.signaler_incident(
            "mesure_invalide", mission=etape.mission, mesures=concernees,
            date_incident=maintenant,
        )
    return decision, incident


def creer_irrigation_manuelle(
    zone, utilisateur, duree_secondes, volume_ml=None, date_debut=None, maintenant=None
):
    """Enregistre une intervention saisie par l'utilisateur (RG16 : pas de décision).

    Refuse (ARROSAGE_INTERDIT) si la durée dépasse le maximum (RG18) ou si la
    dernière mesure de la zone n'est pas valide (RG17).
    """
    maintenant = maintenant or timezone.now()
    derniere = (
        Mesure.objects.filter(etape__zone=zone).order_by("-date_heure_mesure").first()
    )
    verification = securite.verifier_intervention(
        duree_secondes,
        _duree_max_irrigation(),
        None if derniere is None else derniere.statut == "valide",
    )
    if not verification.autorisee:
        details = {"raison": verification.code}
        if derniere is not None:
            details["statut_mesure"] = derniere.statut
        raise ArrosageInterdit(verification.motif, details)

    debut = date_debut or maintenant
    return Irrigation.objects.create(
        zone=zone,
        utilisateur=utilisateur,
        automatique=False,
        decision=None,
        duree_secondes=duree_secondes,
        volume_ml=volume_ml,
        date_debut=debut,
        date_fin=debut + timedelta(seconds=duree_secondes),
        statut="terminee",
    )


def lister_irrigations(zone=None, automatique=None, statut=None, du=None, au=None):
    requete = Irrigation.objects.all()
    if zone is not None:
        requete = requete.filter(zone_id=zone)
    if automatique is not None:
        requete = requete.filter(automatique=automatique)
    if statut:
        requete = requete.filter(statut=statut)
    if du is not None:
        requete = requete.filter(date_debut__gte=du)
    if au is not None:
        requete = requete.filter(date_debut__lt=au)
    return requete


def lister_decisions(zone=None, statut=None, du=None, au=None):
    requete = Decision.objects.select_related("analyse")
    if zone is not None:
        requete = requete.filter(analyse__zone_id=zone)
    if statut:
        requete = requete.filter(statut=statut)
    if du is not None:
        requete = requete.filter(date_decision__gte=du)
    if au is not None:
        requete = requete.filter(date_decision__lt=au)
    return requete


def derniere_decision(zone_id):
    """Dernière décision d'une zone (404 si la zone ou la décision n'existe pas)."""
    if not Zone.objects.filter(pk=zone_id).exists():
        raise RessourceIntrouvable(f"La zone {zone_id} n'existe pas.", {"zone": zone_id})
    decision = (
        Decision.objects.select_related("analyse")
        .filter(analyse__zone_id=zone_id)
        .order_by("-date_decision", "-decision_id")
        .first()
    )
    if decision is None:
        raise RessourceIntrouvable("Aucune décision pour cette zone.", {"zone": zone_id})
    return decision


def seuils_par_zone():
    """Seuils d'humidité configurés pour chaque zone."""
    return Zone.objects.order_by("parcelle_id", "nom")