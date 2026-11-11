"""Lecture des paramètres d'URL (?zone=3&du=2026-11-01) avec erreur 400 claire."""
from datetime import datetime, time, timedelta, timezone

from django.utils.dateparse import parse_date, parse_datetime

from .exceptions import DonneesInvalides


def lire_entier(parametres, nom):
    """Renvoie l'entier du paramètre `nom`, ou None s'il est absent."""
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return None
    try:
        return int(valeur)
    except ValueError:
        raise DonneesInvalides(
            f"Le paramètre « {nom} » doit être un entier.", {nom: ["Entier attendu."]}
        )


def lire_date(parametres, nom, fin=False):
    """Renvoie une date-heure (UTC) ou None.

    Accepte « 2026-11-01 » ou une date-heure ISO 8601. Pour une borne de fin
    donnée sans heure, on prend le lendemain à minuit : la journée est incluse
    (utiliser alors `__lt`).
    """
    valeur = parametres.get(nom)
    if not valeur:
        return None
    try:
        moment = parse_datetime(valeur)
        if moment is None:
            jour = parse_date(valeur)
            if jour is None:
                raise ValueError
            moment = datetime.combine(jour, time.min)
            if fin:
                moment += timedelta(days=1)
    except ValueError:
        raise DonneesInvalides(
            f"Le paramètre « {nom} » doit être une date ISO 8601.",
            {nom: ["Date invalide (ex. 2026-11-08)."]},
        )
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def lire_booleen(parametres, nom):
    """« true » / « false » -> True / False ; absent -> None."""
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return None
    if valeur.lower() in ("true", "1"):
        return True
    if valeur.lower() in ("false", "0"):
        return False
    raise DonneesInvalides(
        f"Le paramètre « {nom} » doit valoir true ou false.", {nom: ["Booléen attendu."]}
    )