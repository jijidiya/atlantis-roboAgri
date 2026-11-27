"""Contraintes de la table `mesure` (MPD, RG7 et RG8)."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.mesures.models import Mesure


def creer_mesure(etape, message, **champs):
    valeurs = dict(
        numero_point=1,
        numero_lecture=1,
        valeur_brute=2000,
        valeur_humidite=Decimal("40.00"),
        date_heure_mesure=timezone.now(),
        statut="valide",
        etape=etape,
        message=message,
    )
    valeurs.update(champs)
    return Mesure.objects.create(**valeurs)


def refusee(etape, message, **champs):
    """Vérifie que la base refuse l'insertion (contrainte CHECK ou UNIQUE)."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            creer_mesure(etape, message, **champs)


def test_mesure_valide_acceptee(etape, message):
    mesure = creer_mesure(etape, message)

    assert mesure.statut == "valide"
    assert mesure.valeur_humidite == Decimal("40.00")


@pytest.mark.parametrize("numero_point", [0, 4])
def test_numero_point_hors_de_1_a_3_refuse(etape, message, numero_point):
    refusee(etape, message, numero_point=numero_point)


@pytest.mark.parametrize("numero_lecture", [0, 4])
def test_numero_lecture_hors_de_1_a_3_refuse(etape, message, numero_lecture):
    refusee(etape, message, numero_lecture=numero_lecture)


@pytest.mark.parametrize("valeur", [Decimal("-0.01"), Decimal("100.01")])
def test_humidite_hors_de_0_a_100_refusee(etape, message, valeur):
    refusee(etape, message, valeur_humidite=valeur)


def test_mesure_valide_sans_humidite_refusee(etape, message):
    refusee(etape, message, valeur_humidite=None)


def test_mesure_invalide_sans_humidite_acceptee(etape, message):
    mesure = creer_mesure(etape, message, statut="invalide", valeur_humidite=None)

    assert mesure.statut == "invalide"
    assert mesure.valeur_humidite is None


def test_meme_point_et_meme_lecture_au_meme_moment_refuses(etape, message):
    moment = timezone.now()
    creer_mesure(etape, message, date_heure_mesure=moment, numero_lecture=2)

    refusee(etape, message, date_heure_mesure=moment, numero_lecture=2)


def test_meme_lecture_a_une_autre_heure_acceptee(etape, message):
    moment = timezone.now()
    creer_mesure(etape, message, date_heure_mesure=moment, numero_lecture=2)

    mesure = creer_mesure(
        etape, message, date_heure_mesure=moment + timedelta(minutes=1), numero_lecture=2
    )

    assert mesure.pk is not None
