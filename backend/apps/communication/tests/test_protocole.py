import pytest

from apps.communication import protocole


def message_valide(**changements):
    base = {
        "id_message": "m1", "zone_id": 1, "sequence": 1,
        "humidite": 42.5, "mesure_le": "2026-11-04T10:00:00+01:00",
    }
    return {**base, **changements}


def test_message_valide():
    message = protocole.valider(message_valide())
    assert message.zone_id == 1 and message.humidite == 42.5


def test_champ_manquant():
    donnees = message_valide()
    del donnees["zone_id"]
    with pytest.raises(protocole.MessageInvalide):
        protocole.valider(donnees)


def test_date_invalide():
    with pytest.raises(protocole.MessageInvalide):
        protocole.valider(message_valide(mesure_le="pas une date"))
