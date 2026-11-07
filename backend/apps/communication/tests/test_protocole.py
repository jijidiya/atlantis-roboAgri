from datetime import datetime, timedelta, timezone

import pytest

from apps.communication import protocole

from .conftest import construire_message

T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=timezone.utc)

EXEMPLES = [
    construire_message("mission_recue", 1, "a41c09e2d7f3b856", mission_id=12),
    construire_message(
        "etape_atteinte", 2, "5be2f0137a9c4d68", mission_id=12, etape=1, zone_id=1
    ),
    construire_message(
        "mesure",
        3,
        "c7d81a4f02e9b365",
        mission_id=12,
        zone_id=1,
        humidite_pct=34.5,
        valeur_brute=2310,
        valide=True,
    ),
    construire_message(
        "changement_etat",
        9,
        "0e6b93d1c5a7f284",
        mission_id=12,
        etat_precedent="en_mesure",
        etat_nouveau="repos",
        mission_terminee=True,
    ),
    construire_message(
        "incident",
        15,
        "7a30c5e19b4d2f68",
        mission_id=12,
        code="FILE_PLEINE",
        gravite="avertissement",
        description="File pleine",
        nb_perdus=12,
    ),
]


@pytest.mark.parametrize("donnees", EXEMPLES, ids=lambda d: d["type"])
def test_les_exemples_du_protocole_sont_valides(donnees):
    message = protocole.valider_message(donnees)
    assert message.type == donnees["type"]
    assert message.date_horodatage == datetime(
        2026, 11, 3, 10, 1, 14, tzinfo=timezone.utc
    )


def test_le_dernier_voeu_mqtt_accepte_des_valeurs_nulles():
    donnees = {
        "message_id": "e19d4a7c60b3f258",
        "num_sequence": None,
        "type": "changement_etat",
        "horodatage": None,
        "uptime_ms": None,
        "etat_nouveau": "hors_ligne",
    }
    message = protocole.valider_message(donnees)
    assert message.num_sequence is None and message.date_horodatage is None


def test_une_mesure_invalide_accepte_humidite_nulle():
    donnees = construire_message(
        "mesure",
        11,
        "b82e51f7d0a3c496",
        mission_id=12,
        zone_id=2,
        humidite_pct=None,
        valeur_brute=0,
        valide=False,
    )
    assert protocole.valider_message(donnees).donnees["valide"] is False


def corrompre(donnees, **changements):
    return {**donnees, **changements}


MESURE = EXEMPLES[2]


@pytest.mark.parametrize(
    "donnees",
    [
        "pas un objet",
        {k: v for k, v in MESURE.items() if k != "message_id"},
        {k: v for k, v in MESURE.items() if k != "zone_id"},
        corrompre(MESURE, message_id="ABC"),
        corrompre(MESURE, message_id="C7D81A4F02E9B365"),
        corrompre(MESURE, type="mission"),
        corrompre(MESURE, num_sequence="3"),
        corrompre(MESURE, num_sequence=True),
        corrompre(MESURE, valide=1),
        corrompre(MESURE, valide="oui"),
        corrompre(MESURE, humidite_pct="34.5"),
        corrompre(MESURE, horodatage="2026-11-03 10:01:14"),
        corrompre(MESURE, horodatage="n'importe quoi"),
        corrompre(EXEMPLES[3], etat_nouveau="dort"),
        corrompre(EXEMPLES[4], gravite="grave"),
        corrompre(EXEMPLES[4], code="CAPTEUR_INVALIDE"),
    ],
)
def test_messages_invalides(donnees):
    with pytest.raises(protocole.MessageInvalide):
        protocole.valider_message(donnees)


def test_construire_les_reponses():
    assert protocole.construire_reponse_ok("abc") == {
        "statut": "ok",
        "message_id": "abc",
    }
    assert (
        protocole.construire_reponse_ok("abc", "arroser")["recommandation_arrosage"]
        == "arroser"
    )
    erreur = protocole.construire_reponse_erreur("MESSAGE_CONFLIT", "détail")
    assert erreur == {"statut": "erreur", "code": "MESSAGE_CONFLIT", "detail": "détail"}


def test_convertir_decision_en_recommandation():
    assert protocole.convertir_decision_en_recommandation("insuffisante") == "arroser"
    assert (
        protocole.convertir_decision_en_recommandation("suffisante") == "ne_pas_arroser"
    )
    assert protocole.convertir_decision_en_recommandation("invalide") == "interdite"


def test_construire_la_mission_du_robot():
    mission = protocole.construire_mission(12, T0, 600, [(1, 1), (2, 2)])
    assert mission == {
        "type": "mission",
        "mission_id": 12,
        "cree_le": "2026-11-03T10:00:00Z",
        "duree_prevue_s": 600,
        "etapes": [{"etape": 1, "zone_id": 1}, {"etape": 2, "zone_id": 2}],
    }


def evaluer(maintenant, derniere_activite=T0, duree_prevue_secondes=600):
    return protocole.evaluer_non_confirmation(
        maintenant=maintenant,
        derniere_activite=derniere_activite,
        date_recue=T0,
        duree_prevue_secondes=duree_prevue_secondes,
    )


def test_silence_de_dix_cycles():
    assert evaluer(T0 + timedelta(seconds=29)) is None
    assert evaluer(T0 + timedelta(seconds=30)) == "silence"


def test_plafond_global_meme_si_le_robot_communique():
    derniere = T0 + timedelta(seconds=1795)
    assert evaluer(T0 + timedelta(seconds=1800), derniere) is None
    assert evaluer(T0 + timedelta(seconds=1801), derniere) == "plafond"
