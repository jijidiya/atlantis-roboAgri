from apps.mesures.validation import valider_humidite


def test_valeur_normale():
    assert valider_humidite(45.0).est_valide


def test_valeur_manquante():
    assert valider_humidite(None).motif == "valeur_manquante"


def test_capteur_invalide():
    assert valider_humidite(45.0, est_valide_capteur=False).motif == "capteur_invalide"


def test_hors_plage():
    assert valider_humidite(120.0).motif == "hors_plage"
    assert valider_humidite(-1.0).motif == "hors_plage"
