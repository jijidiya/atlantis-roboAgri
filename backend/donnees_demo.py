"""
Génère une base de DÉMONSTRATION pour RoboAgri-Kin.

Crée 1 administrateur et 3 propriétaires, chacun avec une parcelle (2, 3 puis
4 zones), des cultures, des missions (terminées, interrompue, non confirmée,
planifiée), des messages du robot, des mesures d humidité, des incidents, des
analyses, des décisions et des irrigations.

ATTENTION : toutes les valeurs sont FICTIVES (tirées au hasard, avec une graine
fixe pour obtenir toujours les mêmes données). Ce jeu de données sert
uniquement à tester et à présenter l application (livrable « base de
démonstration »). Il ne doit jamais être présenté comme des mesures
expérimentales dans le rapport. Les coordonnées GPS sont approximatives.

Usage, depuis backend/ avec l environnement virtuel activé :
    python donnees_demo.py                  # crée les données
    python donnees_demo.py --reinitialiser  # efface les données de démo, puis les recrée

Les comptes de démo ont tous un e-mail se terminant par @demo.roboagri.cd :
seuls ces comptes et leurs données sont effacés par --reinitialiser.
"""
import argparse
import os
import random
import sys
from collections import Counter
from datetime import timedelta
from statistics import mean

import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.analyse.models import Analyse  # noqa: E402
from apps.communication.models import Message  # noqa: E402
from apps.incidents.models import Incident  # noqa: E402
# Si l'import suivant échoue, adapter le chemin au module où se trouvent
# Decision et Irrigation dans votre projet.
from apps.irrigation.models import Decision, Irrigation  # noqa: E402
from apps.mesures.models import Mesure  # noqa: E402
from apps.missions.models import Etape, Mission  # noqa: E402
from apps.parcelles.models import Cultiver, Culture, Parcelle, Zone  # noqa: E402

DOMAINE = "demo.roboagri.cd"
MOT_DE_PASSE = "Demo2026!"  # mot de passe de démonstration uniquement
DEBIT_POMPE_ML_PAR_S = 16.7  # pompe d'environ 1 L/min (valeur fictive)

# --------------------------------------------------------------------------
# Données de départ
# --------------------------------------------------------------------------
PROPRIETAIRES = [
    {
        "prenom": "Junior", "nom": "Diyabanza", "email": "junior.diyabanza",
        "parcelle": {"nom": "Maraîchage de Kimwenza (démo)", "latitude": -4.42,
                     "longitude": 15.30, "superficie": 850},
        "zones": [
            {"nom": "Planche A - Tomates", "superficie": 200, "min": 35, "max": 70,
             "auto": True, "cultures": [("Tomate", "Roma")]},
            {"nom": "Planche B - Choux", "superficie": 180, "min": 40, "max": 75,
             "auto": False, "cultures": [("Chou", "Gloria")]},
        ],
    },
    {
        "prenom": "Gabriel", "nom": "Lukanda", "email": "gabriel.lukanda",
        "parcelle": {"nom": "Jardin expérimental de Mont-Ngafula (démo)", "latitude": -4.45,
                     "longitude": 15.25, "superficie": 1200},
        "zones": [
            {"nom": "Zone 1 - Aubergines", "superficie": 250, "min": 30, "max": 65,
             "auto": True, "cultures": [("Aubergine", "Africaine")]},
            {"nom": "Zone 2 - Amarante", "superficie": 220, "min": 35, "max": 70,
             "auto": False, "cultures": [("Amarante", None)]},
            {"nom": "Zone 3 - Oignons", "superficie": 300, "min": 25, "max": 60,
             "auto": False, "cultures": [("Oignon", "Red Creole"), ("Piment", None)]},
        ],
    },
    {
        "prenom": "Sabin", "nom": "Ntwali", "email": "sabin.ntwali",
        "parcelle": {"nom": "Pépinière de Maluku (démo)", "latitude": -4.05,
                     "longitude": 16.10, "superficie": 2000},
        "zones": [
            {"nom": "Bloc 1 - Piments", "superficie": 400, "min": 30, "max": 65,
             "auto": True, "cultures": [("Piment", "Pili-pili")]},
            {"nom": "Bloc 2 - Poivrons", "superficie": 380, "min": 35, "max": 70,
             "auto": False, "cultures": [("Poivron", None)]},
            {"nom": "Bloc 3 - Laitue", "superficie": 350, "min": 45, "max": 80,
             "auto": True, "cultures": [("Laitue", "Batavia")]},
            {"nom": "Bloc 4 - Concombres", "superficie": 420, "min": 40, "max": 75,
             "auto": False, "cultures": [("Concombre", None)]},
        ],
    },
]

# Missions de chaque propriétaire : (statut, nombre de jours dans le passé).
SCENARIOS = {
    0: [("terminee", 9), ("terminee", 6), ("terminee", 3), ("interrompue", 1), ("planifiee", 0)],
    1: [("terminee", 8), ("terminee", 5), ("terminee", 2), ("non_confirmee", 1), ("planifiee", 0)],
    2: [("terminee", 10), ("terminee", 7), ("terminee", 4), ("terminee", 1), ("planifiee", 0)],
}

# Anomalies de lecture : (propriétaire, mission, zone) -> {(point, lecture): état}
ANOMALIES = {
    (0, 2, 0): {(1, 2): "invalide"},                                      # une lecture invalide
    (1, 0, 2): {(3, 3): "manquante"},                                     # une lecture manquante
    (2, 1, 1): {(2, 1): "invalide", (2, 2): "invalide", (2, 3): "invalide"},  # capteur défaillant
}


class Sequence:
    """Compteur de num_sequence pour les messages d'une mission."""

    def __init__(self):
        self.n = 0

    def suivant(self):
        self.n += 1
        return self.n


# --------------------------------------------------------------------------
# Effacement des données de démonstration
# --------------------------------------------------------------------------
def effacer_donnees_demo():
    """Supprime les données de démo, dans l'ordre imposé par les clés protégées."""
    utilisateur = get_user_model()
    parcelles = Parcelle.objects.filter(utilisateur__email__endswith="@" + DOMAINE)
    Irrigation.objects.filter(zone__parcelle__in=parcelles).delete()
    Decision.objects.filter(analyse__zone__parcelle__in=parcelles).delete()
    Mesure.objects.filter(etape__mission__parcelle__in=parcelles).delete()
    Analyse.objects.filter(zone__parcelle__in=parcelles).delete()
    Incident.objects.filter(mission__parcelle__in=parcelles).delete()
    Message.objects.filter(mission__parcelle__in=parcelles).delete()
    Etape.objects.filter(mission__parcelle__in=parcelles).delete()
    Mission.objects.filter(parcelle__in=parcelles).delete()
    Zone.objects.filter(parcelle__in=parcelles).delete()
    parcelles.delete()
    utilisateur.objects.filter(email__endswith="@" + DOMAINE).delete()


# --------------------------------------------------------------------------
# Parcelles et zones
# --------------------------------------------------------------------------
def carre(longitude, latitude, rang):
    """Petit polygone GeoJSON (carré d'environ 30 m) pour la carte Leaflet."""
    x = longitude + 0.0004 * rang
    c = 0.0003
    return {"type": "Polygon", "coordinates": [[
        [x, latitude], [x + c, latitude], [x + c, latitude + c],
        [x, latitude + c], [x, latitude],
    ]]}


def creer_parcelle(utilisateur, fiche):
    p = fiche["parcelle"]
    parcelle = Parcelle.objects.create(
        nom=p["nom"], latitude=p["latitude"], longitude=p["longitude"],
        superficie=p["superficie"], utilisateur=utilisateur,
    )
    zones = []
    for rang, z in enumerate(fiche["zones"]):
        zone = Zone.objects.create(
            nom=z["nom"], superficie=z["superficie"],
            humidite_minimum=z["min"], humidite_maximum=z["max"],
            geometrie_zone=carre(p["longitude"], p["latitude"], rang),
            irrigation_auto_active=z["auto"], parcelle=parcelle,
        )
        for nom, variete in z["cultures"]:
            culture, _ = Culture.objects.get_or_create(nom=nom, variete=variete)
            Cultiver.objects.get_or_create(zone=zone, culture=culture)
        zones.append(zone)
    return parcelle, zones


# --------------------------------------------------------------------------
# Messages du robot
# --------------------------------------------------------------------------
def creer_message(rng, mission, type_message, numero, quand, contenu, stats):
    """Crée un message du robot (le contenu garde le message complet, comme le protocole)."""
    message_id = f"{rng.getrandbits(64):016x}"
    corps = {
        "message_id": message_id, "num_sequence": numero, "type": type_message,
        "horodatage": quand.strftime("%Y-%m-%dT%H:%M:%SZ"), "uptime_ms": numero * 15000,
        "mission_id": mission.pk, **contenu,
    }
    stats["messages"] += 1
    return Message.objects.create(
        message_id=message_id, num_sequence=numero, type_message=type_message,
        contenu=corps, mission=mission, date_heure=quand,
    )


# --------------------------------------------------------------------------
# Mesures, analyse, décision, irrigation (une étape terminée)
# --------------------------------------------------------------------------
def enregistrer_mesures(rng, utilisateur, mission, etape, zone, anomalies,
                        debut_etape, fin_etape, seq, stats):
    """Crée les 9 mesures d'une étape (3 points x 3 lectures, RG7), puis l'analyse,
    la décision et, si nécessaire, l'irrigation."""
    minimum, maximum = float(zone.humidite_minimum), float(zone.humidite_maximum)
    # Humidité moyenne de la zone pour cette visite : parfois sous le minimum (arrosage).
    moyenne_zone = max(5.0, rng.uniform(minimum - 12, maximum - 12))
    quand = debut_etape + timedelta(seconds=40)

    lectures, mesures = [], []
    for i, (point, numero) in enumerate((p, n) for p in (1, 2, 3) for n in (1, 2, 3)):
        etat = anomalies.get((point, numero), "valide")
        instant = quand + timedelta(seconds=5 * i)
        if etat == "valide":
            humidite = round(min(100.0, max(0.0, moyenne_zone + rng.uniform(-1.5, 1.5))), 2)
            brute = int(3400 - humidite * 20)  # conversion FICTIVE valeur brute <- humidité
        elif etat == "invalide":
            humidite, brute = None, 0  # capteur débranché
        else:  # manquante
            humidite, brute = None, None
        if etat != "manquante":  # une lecture manquante n'a pas été reçue
            lectures.append({"numero_point": point, "numero_lecture": numero,
                             "humidite_pct": humidite, "valeur_brute": brute,
                             "valide": etat == "valide"})
        mesures.append(Mesure(
            numero_point=point, numero_lecture=numero, valeur_brute=brute,
            valeur_humidite=humidite, date_heure_mesure=instant, statut=etat, etape=etape,
        ))

    message = creer_message(rng, mission, "mesure", seq.suivant(), quand,
                            {"etape": etape.numero_ordre, "zone_id": zone.pk,
                             "lectures": lectures}, stats)
    for mesure in mesures:
        mesure.message = message

    # RG17 : une mesure invalide crée un incident (capteur défaillant si 3 lectures ou plus).
    invalides = [m for m in mesures if m.statut == "invalide"]
    if invalides:
        type_incident = "capteur_defaillant" if len(invalides) >= 3 else "mesure_invalide"
        incident = Incident.objects.create(
            type_incident=type_incident, mission=mission, date_incident=fin_etape)
        for mesure in invalides:
            mesure.incident = incident
        stats["incidents"] += 1
    Mesure.objects.bulk_create(mesures)
    stats["mesures"] += len(mesures)

    # Analyse : synthèse des mesures valides de la zone (RG12).
    valides = [m for m in mesures if m.statut == "valide"]
    valeurs = [float(m.valeur_humidite) for m in valides]
    moyenne = round(mean(valeurs), 2) if valeurs else None
    resultat = (f"Humidité moyenne {moyenne} % (plage cible {minimum:g}-{maximum:g} %)."
                if valeurs else "Aucune mesure valide.")
    analyse = Analyse.objects.create(
        zone=zone, date_analyse=fin_etape, periode_debut=debut_etape, periode_fin=fin_etape,
        humidite_moyenne=moyenne,
        humidite_minimum=round(min(valeurs), 2) if valeurs else None,
        humidite_maximum=round(max(valeurs), 2) if valeurs else None,
        nombre_mesures=len(valeurs), resultat_analyse=resultat,
    )
    Mesure.objects.filter(pk__in=[m.pk for m in valides]).update(analyse=analyse)
    stats["analyses"] += 1

    # Décision : les seuils sont copiés depuis la zone (RG13).
    if invalides:
        type_decision, statut, action = "mesure_invalide", "refusee", "aucune_irrigation"
        justification = "Mesure invalide : arrosage automatique interdit (RG17)."
    elif moyenne < minimum:
        type_decision = "humidite_insuffisante"
        if zone.irrigation_auto_active:
            statut, action = "autorisee", "arrosage_automatique"
        else:
            statut, action = "recommandee", "arrosage_recommande"
        justification = f"Humidité moyenne {moyenne} % sous le minimum de {minimum:g} %."
    else:
        # Aucune action requise : la décision est enregistrée pour la traçabilité.
        type_decision, statut, action = "humidite_suffisante", "recommandee", "aucune_action"
        justification = f"Humidité moyenne {moyenne} % dans la plage cible."
    decision = Decision.objects.create(
        type_decision=type_decision, action=action, justification=justification,
        seuil_min_applique=zone.humidite_minimum, seuil_max_applique=zone.humidite_maximum,
        statut=statut, date_decision=fin_etape + timedelta(seconds=10), analyse=analyse,
    )
    stats["decisions"] += 1

    # Irrigation (durée limitée, RG18). Automatique : liée à la décision, sans utilisateur
    # (RG15). Manuelle : lancée par le propriétaire, sans décision (RG16).
    if type_decision == "humidite_insuffisante":
        duree = rng.choice([30, 45, 60, 75, 90])
        debut = fin_etape + timedelta(minutes=1)
        automatique = statut == "autorisee"
        if automatique or rng.random() < 0.7:  # le propriétaire suit souvent la recommandation
            Irrigation.objects.create(
                volume_ml=round(duree * DEBIT_POMPE_ML_PAR_S, 2), duree_secondes=duree,
                date_debut=debut, date_fin=debut + timedelta(seconds=duree), statut="terminee",
                automatique=automatique, zone=zone,
                decision=decision if automatique else None,
                utilisateur=None if automatique else utilisateur,
            )
            stats["irrigations"] += 1


# --------------------------------------------------------------------------
# Missions
# --------------------------------------------------------------------------
def creer_mission(rng, utilisateur, parcelle, zones, statut, jours, anomalies, stats):
    """Crée une mission avec ses étapes, messages, mesures, etc. selon son statut."""
    maintenant = timezone.now()
    stats["missions"] += 1

    if statut == "planifiee":  # prête à être récupérée par le robot ou le simulateur
        mission = Mission.objects.create(
            statut="planifiee", date_creation=maintenant, utilisateur=utilisateur, parcelle=parcelle)
        for rang, zone in enumerate(zones, start=1):
            Etape.objects.create(mission=mission, numero_ordre=rang, zone=zone, statut="planifiee")
        return

    debut = (maintenant - timedelta(days=jours)).replace(hour=7, minute=30, second=0, microsecond=0)
    mission = Mission.objects.create(
        statut=statut, date_creation=debut - timedelta(minutes=10), date_debut=debut,
        utilisateur=utilisateur, parcelle=parcelle)
    seq = Sequence()
    creer_message(rng, mission, "mission_recue", seq.suivant(), debut, {}, stats)

    nb_faites = len(zones) if statut == "terminee" else 1
    fin = debut
    for rang, zone in enumerate(zones, start=1):
        debut_etape = debut + timedelta(minutes=4 * (rang - 1) + 1)
        fin_etape = debut_etape + timedelta(minutes=3)
        champs = {"mission": mission, "numero_ordre": rang, "zone": zone}

        if rang <= nb_faites:
            etape = Etape.objects.create(
                statut="terminee", date_debut=debut_etape, date_fin=fin_etape, **champs)
            creer_message(rng, mission, "etape_atteinte", seq.suivant(), debut_etape,
                          {"etape": rang, "zone_id": zone.pk}, stats)
            enregistrer_mesures(rng, utilisateur, mission, etape, zone, anomalies.get(rang - 1, {}),
                                debut_etape, fin_etape, seq, stats)
            fin = fin_etape
        elif rang == nb_faites + 1 and statut == "interrompue":
            Etape.objects.create(statut="interrompue", date_debut=debut_etape, **champs)
            creer_message(rng, mission, "etape_atteinte", seq.suivant(), debut_etape,
                          {"etape": rang, "zone_id": zone.pk}, stats)
            fin = debut_etape + timedelta(minutes=1)
            Incident.objects.create(type_incident="obstacle", mission=mission, date_incident=fin)
            creer_message(rng, mission, "incident", seq.suivant(), fin,
                          {"code": "OBSTACLE", "gravite": "bloquant",
                           "description": "Obstacle détecté sur le parcours"}, stats)
            stats["incidents"] += 1
        elif rang == nb_faites + 1 and statut == "non_confirmee":
            Etape.objects.create(statut="en_cours", date_debut=debut_etape, **champs)
            creer_message(rng, mission, "etape_atteinte", seq.suivant(), debut_etape,
                          {"etape": rang, "zone_id": zone.pk}, stats)
            Incident.objects.create(type_incident="perte_communication", mission=mission,
                                    date_incident=debut_etape + timedelta(minutes=2))
            stats["incidents"] += 1
            fin = None  # le résultat n'a pas pu être confirmé : pas de date de fin
        else:
            Etape.objects.create(statut="planifiee", **champs)

    if statut == "terminee":
        fin = fin + timedelta(minutes=1)
        creer_message(rng, mission, "changement_etat", seq.suivant(), fin,
                      {"etat_precedent": "en_mesure", "etat_nouveau": "repos",
                       "mission_terminee": True}, stats)
    mission.date_fin = fin
    mission.save(update_fields=["date_fin"])


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
def generer():
    rng = random.Random(2026)  # graine fixe : toujours les mêmes données
    stats = Counter()
    utilisateur_modele = get_user_model()

    utilisateur_modele.objects.create_superuser(
        email=f"admin@{DOMAINE}", password=MOT_DE_PASSE, nom="Admin", prenom="RoboAgri")
    stats["utilisateurs"] += 1

    for indice, fiche in enumerate(PROPRIETAIRES):
        utilisateur = utilisateur_modele.objects.create_user(
            email=f"{fiche['email']}@{DOMAINE}", password=MOT_DE_PASSE,
            nom=fiche["nom"], prenom=fiche["prenom"], role="proprietaire")
        stats["utilisateurs"] += 1
        parcelle, zones = creer_parcelle(utilisateur, fiche)
        stats["parcelles"] += 1
        stats["zones"] += len(zones)
        for numero, (statut, jours) in enumerate(SCENARIOS[indice]):
            anomalies = {z: a for (p, m, z), a in ANOMALIES.items() if p == indice and m == numero}
            creer_mission(rng, utilisateur, parcelle, zones, statut, jours, anomalies, stats)

    print("Données de démonstration créées :")
    for cle in ("utilisateurs", "parcelles", "zones", "missions", "messages",
                "mesures", "incidents", "analyses", "decisions", "irrigations"):
        print(f"  {cle:<13} {stats[cle]}")
    print(f"\nMot de passe de tous les comptes : {MOT_DE_PASSE}")
    print(f"  admin@{DOMAINE}")
    for fiche in PROPRIETAIRES:
        print(f"  {fiche['email']}@{DOMAINE}")


def main():
    parseur = argparse.ArgumentParser(description="Génère la base de démonstration.")
    parseur.add_argument("--reinitialiser", action="store_true",
                         help="efface les données de démo existantes avant de les recréer")
    args = parseur.parse_args()

    existe = get_user_model().objects.filter(email__endswith="@" + DOMAINE).exists()
    if existe and not args.reinitialiser:
        print("Les données de démo existent déjà. Relancer avec --reinitialiser pour les recréer.")
        sys.exit(1)
    with transaction.atomic():  # tout ou rien
        if existe:
            effacer_donnees_demo()
        generer()


if __name__ == "__main__":
    main()