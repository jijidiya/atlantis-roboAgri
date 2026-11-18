# Simulateur du robot — RoboAgri-Kin

Faux robot écrit en Python. Il parle à l'API Django **exactement comme le vrai
ESP32** : il récupère une mission, simule un déplacement, génère des mesures,
puis envoie ses messages. Il sert à tester toute la chaîne sans matériel, et à
reproduire des pannes à volonté.

Le simulateur et le firmware partagent le **même protocole**. Ce qui fonctionne
ici fonctionnera sur l'ESP32 (aux différences près : `requests` vs `urequests`,
Wi-Fi, mémoire).

---

## Sommaire

1. [À quoi ça sert](#1-à-quoi-ça-sert)
2. [Structure du dossier](#2-structure-du-dossier)
3. [Prérequis](#3-prérequis)
4. [Configuration](#4-configuration)
5. [Utilisation](#5-utilisation)
6. [Scénarios disponibles](#6-scénarios-disponibles)
7. [Formats de messages](#7-formats-de-messages)
8. [Workflow d'une mission](#8-workflow-dune-mission)
9. [Dépannage](#9-dépannage)
10. [Relation avec le firmware](#10-relation-avec-le-firmware)

---

## 1. À quoi ça sert

- **Tester le backend sans robot** : vérifier que `POST /robot/messages/`
  accepte les bons formats, que les décisions d'irrigation sont calculées, que
  les incidents sont créés.
- **Scénarios dégradés** : capteur défaillant, perte de réseau, obstacle,
  doublon. Ces cas sont difficiles à reproduire sur le vrai robot (débrancher un
  câble, couper le Wi-Fi). Le simulateur les rejoue en une commande.
- **Préparer le firmware** : la logique de `client_api.py` est identique à
  `firmware/reseau.py`. On valide le protocole en Python avant de l'écrire en
  MicroPython.
- **Démo** : si le robot est indisponible, le simulateur fait tourner une
  mission complète en direct devant le jury.

---

## 2. Structure du dossier

```
simulateur/
├── README.md              ce fichier
├── configuration.py       URL du backend, chemins, jeton, délais
├── client_api.py          client HTTP : recuperer_mission(), envoyer_message()
├── capteur_virtuel.py     génère les lectures (valeur_brute, humidité)
├── robot_virtuel.py       états du robot, exécution d'une mission
├── scenarios.py           scénarios de panne (nominal, sec, obstacle, ...)
├── lancer.py              point d'entrée en ligne de commande
└── test_simple.py         test minimal (1 message, validation rapide)
```

---

## 3. Prérequis

- Python 3.10 ou plus récent
- Le backend Django lancé (`python manage.py runserver` sur `http://127.0.0.1:8000`)
- Le module `requests` installé :
  ```bash
  pip install requests
  ```
- Une **mission planifiée** créée dans l'interface web (`/missions`) avant de
  lancer le robot. Voir la section 8.

---

## 4. Configuration

Le fichier `configuration.py` contient tous les réglages :

```python
# Adresse de l'API Django
adresse_api = "http://127.0.0.1:8000"

# Jeton d'authentification du robot (CLE_ROBOT côté backend)
jeton_robot = "12340000"

# Chemins de l'API (le slash final est obligatoire)
chemin_mission = "/api/v1/robot/mission-suivante/"
chemin_messages = "/api/v1/robot/messages/"

# Délai maximal d'attente d'une réponse, en secondes
delai_attente = 20

# Délai entre deux demandes de mission, en secondes
delai_polling = 3

# Durée simulée d'un déplacement entre deux zones, en secondes
duree_deplacement = 2

# Règles de collecte : 3 points par zone, 3 lectures par point
nombre_points = 3
nombre_lectures = 3
```

### Points importants

- **Le slash final** dans `chemin_mission` et `chemin_messages` est
  obligatoire. Django ne peut pas rediriger un POST vers l'URL avec slash sans
  perdre le corps de la requête (erreur 500).
- **`delai_attente = 20`** est recommandé. Le backend met 8 à 10 s à traiter
  les 9 mesures d'une étape (première requête TimescaleDB). 5 s est trop court.
- **`jeton_robot`** doit être identique à `CLE_ROBOT` dans le backend
  (`backend/.env` ou `settings.py`). Il est envoyé dans l'en-tête
  `X-Cle-Robot`.

---

## 5. Utilisation

### Lancer le robot (une seule mission puis arrêt)

```bash
cd simulateur
python lancer.py --une-seule
```

### Lancer le robot en continu (boucle infinie)

```bash
python lancer.py
```

Le robot interroge le backend toutes les 3 s jusqu'à trouver une mission
`planifiee`. Dès qu'il en trouve une, il l'exécute et reprend le polling.

### Options disponibles

```
python lancer.py [--scenario NOM] [--vitesse N] [--une-seule] [--quiet]
```

| Option | Effet | Défaut |
|---|---|---|
| `--scenario NOM` | Scénario de panne à simuler | `nominal` |
| `--vitesse N` | Facteur de vitesse (2 = deux fois plus rapide) | `1.0` |
| `--une-seule` | Ne joue qu'une mission puis s'arrête | désactivé |
| `--quiet` | Affiche uniquement OK/WARN/ERR | désactivé |

### Test rapide (sans robot)

```bash
python test_simple.py
```

Envoie un seul message de mesure à la mission en attente et affiche la réponse
brute du backend. Utile après un changement de format.

---

## 6. Scénarios disponibles

| Scénario | Description | Effet attendu dans l'UI |
|---|---|---|
| `nominal` | Mission complète, mesures correctes | Statut `terminee`, mesures visibles |
| `sol_sec` | Humidité sous le seuil bas de la zone | Décision `humidite_insuffisante`, arrosage recommandé |
| `sol_humide` | Humidité au-dessus du seuil haut | Décision `humidite_suffisante`, aucun arrosage |
| `capteur_defaillant` | Valeurs hors plage (capteur débranché) | Mesure `invalide`, incident créé |
| `obstacle` | Obstacle détecté après l'étape 1 | Mission `interrompue`, incident `obstacle` |
| `perte_reseau` | Messages non envoyés | Aucun changement côté backend |
| `doublon` | Renvoie le même `message_id` deux fois | Réponse `deja_recu: true`, pas de doublon en base |

### Exemples

```bash
python lancer.py --scenario sol_sec --une-seule
python lancer.py --scenario obstacle --vitesse 3 --une-seule
python lancer.py --scenario capteur_defaillant --une-seule
python lancer.py --scenario doublon --une-seule
```

---

## 7. Formats de messages

Le simulateur envoie 3 types de messages, tous sur `POST /api/v1/robot/messages/`.

### Message de mesure

```json
{
  "message_id": "a3b4c5d6e7f8a9b0",
  "num_sequence": 1,
  "type": "mesure",
  "horodatage": "2026-11-18T14:30:00Z",
  "mission": 2,
  "etape": 1,
  "lectures": [
    {"numero_point": 1, "numero_lecture": 1, "valeur_brute": 1719, "humidite_pct": 42.0},
    {"numero_point": 1, "numero_lecture": 2, "valeur_brute": 1723, "humidite_pct": 42.1},
    {"numero_point": 1, "numero_lecture": 3, "valeur_brute": 1718, "humidite_pct": 41.9},
    {"numero_point": 2, "numero_lecture": 1, "valeur_brute": 1720, "humidite_pct": 42.0},
    {"numero_point": 2, "numero_lecture": 2, "valeur_brute": 1725, "humidite_pct": 42.2},
    {"numero_point": 2, "numero_lecture": 3, "valeur_brute": 1719, "humidite_pct": 42.0},
    {"numero_point": 3, "numero_lecture": 1, "valeur_brute": 1721, "humidite_pct": 42.0},
    {"numero_point": 3, "numero_lecture": 2, "valeur_brute": 1717, "humidite_pct": 41.9},
    {"numero_point": 3, "numero_lecture": 3, "valeur_brute": 1722, "humidite_pct": 42.1}
  ]
}
```

**Points à respecter** :

- `message_id` : 16 caractères hexadécimaux **uniques** (anti-doublon)
- `etape` : c'est le **`numero_ordre`** de l'étape dans la mission (1, 2, 3…),
  **pas** l'`etape_id` global
- `lectures` : 9 entrées (3 points × 3 lectures, RG7)
- `humidite_pct` : entre 0 et 100
- `valeur_brute` : 0 à 4095 (ADC 12 bits de l'ESP32)

### Message d'état

```json
{
  "message_id": "b4c5d6e7f8a9b0c1",
  "num_sequence": 2,
  "type": "etat",
  "horodatage": "2026-11-18T14:31:00Z",
  "mission": 2,
  "etat": "en_cours"
}
```

Valeurs acceptées par le backend : **`en_cours`, `terminee`, `interrompue`**.
Notez le féminin accordé avec « mission » (`terminee`, pas `termine` ;
`interrompue`, pas `interrompu`).

### Message d'incident

```json
{
  "message_id": "c5d6e7f8a9b0c1d2",
  "num_sequence": 3,
  "type": "incident",
  "horodatage": "2026-11-18T14:32:00Z",
  "mission": 2,
  "type_incident": "obstacle"
}
```

Valeurs acceptées : `obstacle`, `capteur_defaillant`, `perte_communication`,
`mesure_invalide`.

---

## 8. Workflow d'une mission

Le robot fonctionne en **pull automatique** : il interroge le backend, il
n'attend pas d'être appelé.

```
1. Utilisateur crée une mission dans l'UI (/missions → Planifier)
   └─> statut = "planifiee"

2. Robot poll GET /robot/mission-suivante/ toutes les 3 s
   └─> reçoit la mission

3. Robot envoie POST messages (type "etat", "en_cours")
   └─> statut mission = "en_cours"

4. Pour chaque étape :
   - pause simulée (déplacement)
   - génération de 9 mesures
   - POST messages (type "mesure")
   └─> mesures enregistrées, décision calculée

5. Robot envoie POST messages (type "etat", "terminee")
   └─> statut mission = "terminee"
```

**Aucun clic utilisateur n'est nécessaire** pour démarrer une mission. Le bouton
« Démarrer » n'existe plus dans l'UI : dès qu'une mission est `planifiee`, le
robot la prend en charge dans les 3 s.

L'utilisateur garde uniquement la possibilité d'**interrompre** une mission
`en_cours` si le robot ne répond plus.

---

## 9. Dépannage

### Erreur 500 sur POST `/api/v1/robot/messages`

L'URL ne finit pas par `/`. Vérifier `chemin_messages` dans `configuration.py`.

### Erreur 400 « Message du robot invalide »

Le backend refuse le payload. Le message d'erreur indique quel champ pose
problème :

```json
{"erreur": {"code": "DONNEES_INVALIDES", "details": {"etape": ["champ obligatoire."]}}}
```

Corriger le format selon la section 7.

### Broken pipe / échec réseau sur la mesure

Le timeout est trop court. Passer `delai_attente` à `20` dans
`configuration.py`. Le backend met 8 à 10 s pour traiter 9 mesures (première
requête TimescaleDB).

### `Aucune mission (204)` alors qu'une mission existe

- La mission n'est pas en statut `planifiee` (elle a déjà été prise ou terminée)
- La mission appartient à un autre utilisateur (filtrage par `utilisateur`)
- Vérifier dans `/admin/missions/mission/` le statut réel

### Anti-doublon KO (le 2e envoi crée un nouveau message)

Le modèle `Message` dans `apps/communication/models.py` n'a pas `message_id`
en `primary_key`. Vérifier le modèle.

### Le backend refuse le jeton (401)

- Vérifier que `jeton_robot` (simulateur) = `CLE_ROBOT` (backend `.env`)
- Vérifier que le jeton est envoyé dans l'en-tête `X-Cle-Robot`
- Redémarrer le serveur Django après toute modification du fichier `.env`

### Une mesure sur deux échoue

Le message de mesure fait 9 lectures (~2 Ko). Si le réseau local est instable,
augmenter `delai_attente` à 30.

---

## 10. Relation avec le firmware

Le simulateur et le firmware partagent le **même protocole**. Ce tableau
récapitule les équivalences.

| Concept | Simulateur (`client_api.py`) | Firmware (`firmware/reseau.py`) |
|---|---|---|
| Bibliothèque HTTP | `requests` | `urequests` |
| Client GET mission | `recuperer_mission()` | `recuperer_mission()` |
| Client POST message | `envoyer_message(msg)` | `envoyer_message(msg)` |
| En-tête auth | `X-Cle-Robot: <jeton>` | `X-Cle-Robot: <jeton>` |
| Timeout | `timeout=delai_attente` | `timeout=delai_attente` |
| Gestion d'erreur réseau | `try/except RequestException` | `try/except Exception` |
| Fermeture connexion | implicite | `r.close()` explicite (obligatoire) |
| File d'attente si offline | non (le simulateur relance) | oui (`stockage.py`, flash) |
| Génération des mesures | `capteur_virtuel.py` | `humidite.py` (ADC réel) |

**Conséquence pratique** : si `lancer.py --une-seule` passe, alors `reseau.py` a
de bonnes chances de fonctionner du premier coup côté ESP32. Les bugs restants
seront matériels (Wi-Fi, capteur, ADC), pas protocolaires.

---

## Voir aussi

- `protocole_communication.md` — format exact des messages et valeurs d'énumération
- `architecture.md` §3.4 — responsabilités du firmware
- `tests/test_e2e.py` — test de bout en bout (création mission + cycle complet)
- `docs/conception/` — diagrammes de séquence, états du robot