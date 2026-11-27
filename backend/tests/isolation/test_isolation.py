"""Isolation des données entre utilisateurs (architecture.pdf §13.2, écart 8).

Deux propriétaires possèdent chacun un jeu complet de ressources. On vérifie,
pour chaque ressource, que la liste et le détail ne laissent rien passer :
un propriétaire ne voit pas les données de l'autre, l'administrateur voit tout.
Les filtres d'URL ne doivent pas contourner cette restriction.
"""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.analyse.models import Analyse
from apps.communication.models import Message
from apps.incidents.models import Incident
from apps.irrigation import services as services_irrigation
from apps.irrigation.models import Decision, Irrigation
from apps.mesures import services as services_mesures
from apps.mesures.models import Mesure
from apps.missions.models import Etape, Mission
from apps.parcelles.models import Parcelle, Zone


def identifiants(reponse, cle):
    """Identifiants renvoyés par une liste de l'API (paginée ou non)."""
    assert reponse.status_code == 200, reponse.data
    corps = reponse.data["results"] if isinstance(reponse.data, dict) else reponse.data
    return {element[cle] for element in corps}


def construire_jeu(utilisateur, numero):
    """Une ressource de chaque type appartenant à `utilisateur`."""
    maintenant = timezone.now()
    parcelle = Parcelle.objects.create(
        nom=f"Parcelle {numero}", utilisateur=utilisateur
    )
    zone = Zone.objects.create(
        nom=f"Zone {numero}",
        humidite_minimum=30,
        humidite_maximum=70,
        parcelle=parcelle,
    )
    mission = Mission.objects.create(utilisateur=utilisateur, parcelle=parcelle)
    etape = Etape.objects.create(mission=mission, zone=zone, numero_ordre=1)
    message = Message.objects.create(
        message_id=f"{numero:016x}",
        type_message="mesure",
        contenu={},
        mission=mission,
    )
    mesure = Mesure.objects.create(
        numero_point=1,
        numero_lecture=1,
        valeur_brute=2000,
        valeur_humidite=Decimal("40.00"),
        date_heure_mesure=maintenant,
        statut="valide",
        etape=etape,
        message=message,
    )
    analyse = Analyse.objects.create(
        periode_debut=maintenant,
        periode_fin=maintenant,
        humidite_moyenne=Decimal("40.00"),
        humidite_minimum=Decimal("40.00"),
        humidite_maximum=Decimal("40.00"),
        nombre_mesures=1,
        zone=zone,
    )
    decision = Decision.objects.create(
        type_decision="humidite_insuffisante",
        action="arroser",
        seuil_min_applique=Decimal("30.00"),
        seuil_max_applique=Decimal("70.00"),
        statut="recommandee",
        analyse=analyse,
    )
    irrigation = Irrigation.objects.create(
        zone=zone,
        utilisateur=utilisateur,
        automatique=False,
        duree_secondes=20,
        date_debut=maintenant,
        date_fin=maintenant + timedelta(seconds=20),
        statut="terminee",
    )
    incident = Incident.objects.create(type_incident="obstacle", mission=mission)
    return {
        "parcelle": parcelle,
        "zone": zone,
        "mission": mission,
        "mesure": mesure,
        "decision": decision,
        "irrigation": irrigation,
        "incident": incident,
    }


@pytest.fixture
def jeux(utilisateur, autre_utilisateur):
    return {
        "moi": construire_jeu(utilisateur, 1),
        "autre": construire_jeu(autre_utilisateur, 2),
    }


def verifier_isolation(api, api_autre, api_admin, url, cle, mien, autre):
    """Listes et détails : isolement des propriétaires, accès total de l'admin."""
    assert mien in identifiants(api.get(url), cle)
    assert autre not in identifiants(api.get(url), cle)

    assert autre in identifiants(api_autre.get(url), cle)
    assert mien not in identifiants(api_autre.get(url), cle)

    assert {mien, autre} <= identifiants(api_admin.get(url), cle)

    assert api.get(f"{url}{autre}/").status_code == 404
    assert api_autre.get(f"{url}{mien}/").status_code == 404
    assert api_admin.get(f"{url}{autre}/").status_code == 200


def test_isolation_des_parcelles(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/parcelles/",
        "parcelle_id",
        jeux["moi"]["parcelle"].pk,
        jeux["autre"]["parcelle"].pk,
    )


def test_isolation_des_zones(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/zones/",
        "zone_id",
        jeux["moi"]["zone"].pk,
        jeux["autre"]["zone"].pk,
    )


def test_isolation_des_missions(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/missions/",
        "mission_id",
        jeux["moi"]["mission"].pk,
        jeux["autre"]["mission"].pk,
    )


def test_isolation_des_mesures(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/mesures/",
        "mesure_id",
        jeux["moi"]["mesure"].pk,
        jeux["autre"]["mesure"].pk,
    )


def test_isolation_des_decisions(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/decisions/",
        "decision_id",
        jeux["moi"]["decision"].pk,
        jeux["autre"]["decision"].pk,
    )


def test_isolation_des_irrigations(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/irrigations/",
        "irrigation_id",
        jeux["moi"]["irrigation"].pk,
        jeux["autre"]["irrigation"].pk,
    )


def test_isolation_des_incidents(api, api_autre, api_admin, jeux):
    verifier_isolation(
        api,
        api_autre,
        api_admin,
        "/api/v1/incidents/",
        "incident_id",
        jeux["moi"]["incident"].pk,
        jeux["autre"]["incident"].pk,
    )


def test_les_filtres_ne_contournent_pas_l_isolation(api, jeux):
    """Demander la zone ou la mission d'un autre ne renvoie jamais ses données."""
    zone_autre = jeux["autre"]["zone"]
    mission_autre = jeux["autre"]["mission"]

    assert identifiants(api.get("/api/v1/mesures/", {"zone": zone_autre.pk}), "mesure_id") == set()
    assert identifiants(api.get("/api/v1/mesures/", {"mission": mission_autre.pk}), "mesure_id") == set()
    assert identifiants(api.get("/api/v1/decisions/", {"zone": zone_autre.pk}), "decision_id") == set()
    assert identifiants(api.get("/api/v1/irrigations/", {"zone": zone_autre.pk}), "irrigation_id") == set()
    assert identifiants(api.get("/api/v1/incidents/", {"mission": mission_autre.pk}), "incident_id") == set()


def test_seuils_limites_aux_zones_du_proprietaire(api, jeux):
    reponse = api.get("/api/v1/irrigations/seuils/")

    assert reponse.status_code == 200
    assert {zone["zone_id"] for zone in reponse.data} == {jeux["moi"]["zone"].pk}


def test_lister_mesures_respecte_les_filtres(jeux):
    """`lister_mesures` filtre par zone, mission et statut (la vue ajoute l'isolation)."""
    mien, autre = jeux["moi"], jeux["autre"]

    assert list(services_mesures.lister_mesures(zone=mien["zone"].pk)) == [mien["mesure"]]
    assert list(services_mesures.lister_mesures(zone=autre["zone"].pk)) == [autre["mesure"]]
    assert list(services_mesures.lister_mesures(mission=autre["mission"].pk)) == [autre["mesure"]]
    assert services_mesures.lister_mesures(statut="invalide").count() == 0


def test_lister_decisions_respecte_les_filtres(jeux):
    """`lister_decisions` filtre par zone et statut (la vue ajoute l'isolation)."""
    mien, autre = jeux["moi"], jeux["autre"]

    assert list(services_irrigation.lister_decisions(zone=mien["zone"].pk)) == [mien["decision"]]
    assert list(services_irrigation.lister_decisions(zone=autre["zone"].pk)) == [autre["decision"]]
    assert services_irrigation.lister_decisions(statut="recommandee").count() == 2
