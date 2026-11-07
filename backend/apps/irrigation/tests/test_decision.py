from apps.irrigation import decision, securite


def test_decision_suffisante():
    assert decision.decider(60, 40, True) == "suffisante"


def test_decision_insuffisante():
    assert decision.decider(20, 40, True) == "insuffisante"


def test_decision_invalide():
    assert decision.decider(20, 40, False) == "invalide"
    assert decision.decider(None, 40, True) == "invalide"


def test_securite_autorise():
    assert securite.verifier(True, False, 80).autorise


def test_securite_refuse():
    assert securite.verifier(False, False, 80).motif == "mesure_invalide"
    assert securite.verifier(True, True, 80).motif == "obstacle"
    assert securite.verifier(True, False, 5).motif == "batterie_faible"
