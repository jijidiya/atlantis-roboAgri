"""Robot virtuel : joue une mission en parlant à l'API comme le vrai ESP32.

Ce fichier est la version Python du firmware. Il fait exactement ce que fera
l'ESP32 : GET mission, pause (déplacement), POST mesures, POST état.
"""
import time
import uuid
from datetime import datetime, timezone

import client_api
import configuration
from capteur_virtuel import CapteurVirtuel
from scenarios import SCENARIOS


class RobotVirtuel:
    """Simule un robot qui exécute des missions."""

    def __init__(self, scenario="nominal", vitesse=1.0, une_seule=False, verbose=True):
        if scenario not in SCENARIOS:
            raise ValueError(f"Scénario inconnu : {scenario}")
        self.scenario_nom = scenario
        self.scenario = SCENARIOS[scenario]
        self.vitesse = max(0.1, vitesse)
        self.une_seule = une_seule
        self.verbose = verbose

        self.capteur = CapteurVirtuel(mode=self.scenario["capteur_mode"])
        self._num_sequence = 0
        self._en_marche = True
        self._missions_jouees = 0

    # --- Logs ------------------------------------------------------------

    def _log(self, niveau, texte):
        if not self.verbose and niveau == "INFO":
            return
        print(f"[{niveau:<4}] {texte}", flush=True)

    # --- Horloge et identifiants -----------------------------------------

    def _horodatage(self):
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _message_id(self):
        return uuid.uuid4().hex[:16]

    def _prochain_numero_sequence(self):
        self._num_sequence += 1
        return self._num_sequence

    # --- Pauses simulées -------------------------------------------------

    def _pause(self, duree):
        time.sleep(duree / self.vitesse)

    # --- Construction des messages ---------------------------------------

    def _message_mesure(self, mission_id, etape_ordre):
        return {
            "message_id": self._message_id(),
            "num_sequence": self._prochain_numero_sequence(),
            "type": "mesure",
            "horodatage": self._horodatage(),
            "mission": mission_id,
            "etape": etape_ordre,
            "lectures": self.capteur.lire_etape(),
        }

    def _message_etat(self, mission_id, etat):
        return {
            "message_id": self._message_id(),
            "num_sequence": self._prochain_numero_sequence(),
            "type": "etat",
            "horodatage": self._horodatage(),
            "mission": mission_id,
            "etat": etat,
        }

    def _message_incident(self, mission_id, type_incident):
        return {
            "message_id": self._message_id(),
            "num_sequence": self._prochain_numero_sequence(),
            "type": "incident",
            "horodatage": self._horodatage(),
            "mission": mission_id,
            "type_incident": type_incident,
        }

    # --- Envoi -----------------------------------------------------------

    def _envoyer(self, message):
        """Envoie le message, retourne (code, corps). Gère le mode perte_reseau."""
        if self.scenario["perte_reseau"]:
            self._log("WARN", "Perte réseau simulée : message non envoyé.")
            return None, None

        code, corps = client_api.envoyer_message(message)
        if code is None:
            self._log("WARN", f"Échec réseau ({message['type']})")
        elif code in (200, 201):
            deja = corps.get("deja_recu") if corps else False
            suffixe = " (deja_recu)" if deja else ""
            self._log("OK", f"Message {message['type']} accepté [HTTP {code}]{suffixe}")
        else:
            self._log("ERR", f"Message {message['type']} refusé [HTTP {code}] : {corps}")
        return code, corps

    # --- Exécution d'une mission -----------------------------------------

    def executer_mission(self, mission):
        mission_id = mission["mission_id"]
        etapes = mission.get("etapes", [])
        self._log("INFO", f"Mission #{mission_id} : {len(etapes)} étape(s)")

        # 1. Message d'état : démarrage
        self._envoyer(self._message_etat(mission_id, "en_cours"))

        for etape in etapes:
            ordre = etape["numero_ordre"]
            self._log("INFO", f"  Étape n°{ordre} (zone {etape.get('zone')})")

            # 2. Déplacement simulé
            self._pause(configuration.duree_deplacement)

            # 3. Mesure
            message_mesure = self._message_mesure(mission_id, ordre)
            code, _ = self._envoyer(message_mesure)

            # 4. Scénario doublon : renvoyer le même message
            if self.scenario["forcer_doublon"] and code in (200, 201):
                self._log("INFO", "  Renvoi du même message_id (test doublon)")
                client_api.envoyer_message(message_mesure)

            # 5. Scénario obstacle : interrompre après l'étape configurée
            if self.scenario["obstacle_apres"] == ordre:
                self._log("WARN", "  Obstacle simulé, arrêt de la mission.")
                self._envoyer(self._message_incident(mission_id, "obstacle"))
                self._envoyer(self._message_etat(mission_id, "interrompue"))
                self._pause(configuration.duree_deplacement)
                return

        # 6. Fin de mission
        self._pause(configuration.duree_deplacement)
        self._envoyer(self._message_etat(mission_id, "terminee"))
        self._log("OK", f"Mission #{mission_id} terminée.")
        self._missions_jouees += 1

    # --- Boucle principale -----------------------------------------------

    def boucle(self):
        self._log("INFO", f"Robot virtuel démarré (scénario : {self.scenario_nom})")
        self._log("INFO", f"Backend : {configuration.adresse_api}")

        while self._en_marche:
            mission = client_api.recuperer_mission()

            if mission is None:
                if self.une_seule and self._missions_jouees > 0:
                    break
                time.sleep(configuration.delai_polling)
                continue

            try:
                self.executer_mission(mission)
            except KeyboardInterrupt:
                self._log("WARN", "Interruption clavier, arrêt.")
                self._en_marche = False
            except Exception as exc:
                self._log("ERR", f"Exception pendant la mission : {exc}")

            if self.une_seule:
                break