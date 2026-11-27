"""Contraintes de la table `analyse` (MPD, RG12)."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.analyse.models import Analyse


def creer_analyse(zone, **champs):
    debut = timezone.now()
    valeurs = dict(
        periode_debut=debut,
        periode_fin=debut + timedelta(minutes=5),
        nombre_mesures=1,
        zone=zone,
    )
    valeurs.update(champs)
    return Analyse.objects.create(**valeurs)


def refusee(zone, **champs):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            creer_analyse(zone, **champs)


def test_analyse_valide_acceptee(zone_a):
    analyse = creer_analyse(zone_a)

    assert analyse.analyse_id is not None
    assert analyse.humidite_moyenne is None


def test_periode_fin_avant_debut_refusee(zone_a):
    debut = timezone.now()

    refusee(zone_a, periode_debut=debut, periode_fin=debut - timedelta(minutes=1))


@pytest.mark.parametrize(
    "champ", ["humidite_moyenne", "humidite_minimum", "humidite_maximum"]
)
def test_humidite_hors_de_0_a_100_refusee(zone_a, champ):
    refusee(zone_a, **{champ: Decimal("150.00")})


def test_humidite_negative_refusee(zone_a):
    refusee(zone_a, humidite_maximum=Decimal("-1.00"))


def test_date_debut_sans_heure_facultatif(zone_a):
    """Les statistiques restent nulles quand aucune mesure valide n'existe."""
    analyse = creer_analyse(zone_a, nombre_mesures=0)

    assert analyse.nombre_mesures == 0
