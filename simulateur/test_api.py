"""Test des 3 types de messages robot + cas critiques (anti-doublon, sécurité).

Ce script vérifie que le backend accepte les messages du robot au bon format.
Il envoie de VRAIS messages : mesure, état, incident, doublon, mauvais jeton.
À lancer sur une base de démonstration ou nettoyer après.
"""
import uuid
from datetime import datetime, timezone

import client_api


def horodatage():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def titre(texte):
    print(f"\n--- {texte} ---")


def afficher_reponse(code, corps):
    print(f"   Code HTTP : {code}")
    print(f"   Corps     : {corps}")
    if corps and "erreur" in corps:
        details = corps["erreur"].get("details", {})
        if details:
            print("   Champs en erreur :")
            for champ, msgs in details.items():
                print(f"     - {champ} : {msgs}")


def resumer(nom, code):
    if code in (200, 201):
        print(f"   [OK] {nom}")
        return True
    print(f"   [KO] {nom} (code {code})")
    return False


# ---------------------------------------------------------------------------
# Récupération d'une mission
# ---------------------------------------------------------------------------

titre("Récupération d'une mission")
mission = client_api.recuperer_mission()

if mission is None:
    print("   Aucune mission (204 ou erreur réseau). Crée une mission dans l'interface.")
    exit(0)

mission_id = mission["mission_id"]
etapes = mission.get("etapes", [])
if not etapes:
    print(f"   Mission #{mission_id} sans étapes. Impossible de tester.")
    exit(0)

numero_ordre = etapes[0]["numero_ordre"]
zone_id = etapes[0]["zone"]
print(f"   Mission #{mission_id}, étape n°{numero_ordre} (zone {zone_id})")


# ---------------------------------------------------------------------------
# 1. Message de mesure
# ---------------------------------------------------------------------------

titre("1. Message de mesure (type 'mesure')")
lectures = [
    {"numero_point": p, "numero_lecture": l, "valeur_brute": 1000 + p * 10 + l,
     "humidite": 42.0 + l}
    for p in range(1, 4)
    for l in range(1, 4)
]
msg_mesure = {
    "message_id": uuid.uuid4().hex[:16],
    "num_sequence": 1,
    "type": "mesure",
    "horodatage": horodatage(),
    "mission": mission_id,
    "etape": numero_ordre,
    "lectures": lectures,
}
print(f"   Envoi de 9 lectures sur l'étape n°{numero_ordre}...")
code, corps = client_api.envoyer_message(msg_mesure)
afficher_reponse(code, corps)
res_mesure = resumer("mesure", code)


# ---------------------------------------------------------------------------
# 2. Message d'état
# ---------------------------------------------------------------------------

titre("2. Message d'état (type 'etat')")
msg_etat = {
    "message_id": uuid.uuid4().hex[:16],
    "num_sequence": 2,
    "type": "etat",
    "horodatage": horodatage(),
    "mission": mission_id,
    "etat": "en_cours",   # valeurs possibles : demarre, en_cours, termine, interrompu, ...
}
print(f"   Envoi d'un état 'en_cours'...")
code, corps = client_api.envoyer_message(msg_etat)
afficher_reponse(code, corps)
res_etat = resumer("etat", code)


# ---------------------------------------------------------------------------
# 3. Message d'incident
# ---------------------------------------------------------------------------

titre("3. Message d'incident (type 'incident')")
msg_incident = {
    "message_id": uuid.uuid4().hex[:16],
    "num_sequence": 3,
    "type": "incident",
    "horodatage": horodatage(),
    "mission": mission_id,
    "type_incident": "obstacle",   # valeurs : obstacle, capteur_defaillant, perte_communication, mesure_invalide
}
print(f"   Envoi d'un incident 'obstacle'...")
code, corps = client_api.envoyer_message(msg_incident)
afficher_reponse(code, corps)
res_incident = resumer("incident", code)


# ---------------------------------------------------------------------------
# 4. Anti-doublon (RG10) — renvoyer le même message_id
# ---------------------------------------------------------------------------

titre("4. Anti-doublon (renvoi du même message_id)")
print(f"   Renvoi du message de mesure {msg_mesure['message_id'][:8]}...")
code, corps = client_api.envoyer_message(msg_mesure)
afficher_reponse(code, corps)

if code == 200 and corps and corps.get("deja_recu"):
    print("   [OK] Message identifié comme doublon (anti-doublon fonctionne)")
    res_doublon = True
elif code == 201:
    print("   [KO] Un doublon a été créé — vérifier la clé primaire de Message")
    res_doublon = False
else:
    print(f"   [KO] Code inattendu ({code})")
    res_doublon = False


# ---------------------------------------------------------------------------
# 5. Sécurité — mauvais jeton robot
# ---------------------------------------------------------------------------

titre("5. Sécurité (mauvais jeton robot)")
original = client_api.entetes["X-Cle-Robot"]
client_api.entetes["X-Cle-Robot"] = "mauvais_jeton_test_1234567890"
try:
    code, corps = client_api.envoyer_message(msg_etat)
finally:
    client_api.entetes["X-Cle-Robot"] = original

print(f"   Code HTTP : {code}")
if code in (401, 403):
    print("   [OK] Jeton invalide rejeté")
    res_securite = True
else:
    print(f"   [KO] Jeton invalide accepté (code {code})")
    res_securite = False


# ---------------------------------------------------------------------------
# 6. Mission inexistante
# ---------------------------------------------------------------------------

titre("6. Mission inexistante")
msg_faux = {
    "message_id": uuid.uuid4().hex[:16],
    "num_sequence": 4,
    "type": "etat",
    "horodatage": horodatage(),
    "mission": 999999,
    "etat": "en_cours",
}
code, corps = client_api.envoyer_message(msg_faux)
afficher_reponse(code, corps)
res_mission = (code == 404)
print(f"   {'[OK]' if res_mission else '[KO]'} Code attendu : 404")


# ---------------------------------------------------------------------------
# Résumé
# ---------------------------------------------------------------------------

titre("Résumé")
resultats = {
    "mesure": res_mesure,
    "etat": res_etat,
    "incident": res_incident,
    "anti-doublon": res_doublon,
    "sécurité": res_securite,
    "mission inexistante": res_mission,
}

reussis = 0
for nom, succes in resultats.items():
    symbole = "OK " if succes else "KO "
    print(f"   [{symbole}] {nom}")
    if succes:
        reussis += 1

print(f"\n   {reussis}/{len(resultats)} test(s) réussi(s).")