import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.mesures.services import enregistrer_mesure
from apps.parcelles.models import Parcelle, Zone

pytestmark = pytest.mark.django_db


@pytest.fixture
def zone():
    return Zone.objects.create(parcelle=Parcelle.objects.create(nom="P"), nom="Z1")


def test_mesure_valide(zone):
    mesure = enregistrer_mesure(zone, 1, 42.0, timezone.now())
    assert mesure.valide


def test_mesure_invalide_conservee(zone):
    mesure = enregistrer_mesure(zone, 1, 250.0, timezone.now())
    assert not mesure.valide and mesure.motif_invalidite == "hors_plage"


def test_sequence_dupliquee_refusee_par_la_base(zone):
    maintenant = timezone.now()
    enregistrer_mesure(zone, 1, 42.0, maintenant)
    with pytest.raises(IntegrityError), transaction.atomic():
        enregistrer_mesure(zone, 1, 43.0, maintenant)
