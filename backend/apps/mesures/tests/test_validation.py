from apps.mesures.validation import valider_humidite


def test_valeur_normale():
    assert valider_humidite(45.0).valide


def test_valeur_manquante():
    assert valider_humidite(None).motif == "valeur_manquante"


def test_hors_plage():
    assert valider_humidite(120.0).motif == "hors_plage"
    assert valider_humidite(-1.0).motif == "hors_plage"


def test_saut_incoherent():
    assert valider_humidite(90.0, precedente=20.0).motif == "saut_incoherent"
