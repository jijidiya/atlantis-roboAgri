Protocole de communication RoboAgri-Kin
=======================================

Version 1.0. Le robot ESP32 interroge l'application Django toutes les 3 s (HTTP), envoie ses messages JSON avec un message_id unique, garde en file ceux qu'il n'a pas pu envoyer et les renvoie au retour du réseau ; l'application ignore les doublons. Une table de correspondance (8.4) prépare le passage à MQTT.

1. Objet et périmètre
=====================

Ce document fixe les règles d'échange entre le robot ESP32 et l'application Django, de façon qu'un membre d'un autre binôme puisse implémenter l'API ou le client robot sans poser de question.

Ce que le protocole couvre :

- le transport (HTTP en polling, évolution vers MQTT) ;
- le format des messages JSON dans les deux sens ;
- l'API HTTP : endpoints, authentification, codes d'erreur ;
- les six comportements exigés par le sujet : envoi de mission, réception, messages répétés, coupure, non-duplication, missions non confirmées ;
- le comportement côté ESP32 : file d'attente, renvoi, sauvegarde du compteur.

Ce qu'il ne couvre pas : la règle de décision d'irrigation (document d'analyse), le schéma complet de la base de données (binôme B), le câblage et l'étalonnage physique du capteur.

Vocabulaire. « Robot » désigne l'ESP32 ; « application » désigne le serveur Django ; « message » désigne un objet JSON envoyé par le robot ; « mission » est l'ordre envoyé par l'application au robot.

2. Principes
============

2.1 Transport : HTTP (polling 3 s), MQTT en évolution
-----------------------------------------------------

Le projet démarre en HTTP : le robot interroge l'application toutes les 3 secondes pour récupérer une mission, et envoie ses messages par POST. C'est le plus simple à tester et à déboguer. Le contenu des messages est identique à celui qu'on enverrait en MQTT : changer de transport ne demande pas de réécrire les messages (section 8).

2.2 Un seul robot, pas d'identifiant de robot
---------------------------------------------

Il n'y a qu'un seul robot. Aucun identifiant de robot n'est donc prévu dans les messages, et les topics MQTT n'ont pas d'identifiant de robot. Si un second robot apparaît, il faudra ajouter cet identifiant, l'inclure dans les topics et revoir la règle d'unicité de message_id (section 10).

2.3 message_id (anti-doublon) et num_sequence (ordre)
-----------------------------------------------------

Deux identifiants, deux rôles séparés :

- message_id identifie le message. C'est la seule clé anti-doublon. Un message_id déjà reçu avec le même contenu renvoie la même réponse (200) sans rien enregistrer. Avec un contenu différent : 409 Conflict et création d'un incident.
- num_sequence donne l'ordre des messages et permet de détecter les trous (86 puis 88 signifie que le 87 manque). Il ne sert jamais à dédupliquer.

Pourquoi les deux : si l'ESP32 redémarre et perd son compteur, le dédoublonnage reste correct ; MQTT en QoS 1 peut livrer deux fois un message ; l'unicité en base repose sur une colonne dédiée (message_id unique), facile à tester.

2.4 Valeur mesurée (%) et valeur brute (diagnostic)
---------------------------------------------------

Le robot envoie l'humidité étalonnée en pourcentage (humidite_pct), utilisée par la règle d'irrigation, et la valeur brute du capteur (valeur_brute), uniquement pour le diagnostic. La règle de décision ne s'applique jamais à la valeur brute. L'étalonnage vit dans la configuration de l'ESP32 ; la valeur brute permet de recalculer le pourcentage si besoin.

3. Conventions
==============

3.1 Noms de champs, encodage, dates ISO 8601 UTC
------------------------------------------------

- Noms de champs en snake_case, sans accent, en français (humidite_pct, num_sequence).
- JSON encodé en UTF-8, en-tête Content-Type: application/json.
- Dates au format ISO 8601 en UTC, avec le suffixe Z : 2026-11-03T10:15:30Z.
- Le robot récupère l'heure par NTP au démarrage (le Wi-Fi du labo doit avoir un accès Internet) puis horodate chaque message lui-même. Un message renvoyé après une coupure garde donc l'heure de sa mesure, pas celle du renvoi.
- Si le NTP échoue, le robot continue de fonctionner : horodatage vaut null, et uptime_ms (temps écoulé depuis le démarrage, en millisecondes) permet de situer les messages entre eux. L'application utilise alors l'heure de réception et le marque comme approximatif.
- message_id : 16 caractères hexadécimaux en minuscules, tirés au hasard (os.urandom(8).hex()), par exemple 9f3a1c7e5b2d4086. Aucun état à sauvegarder.
- Les booléens s'écrivent true ou false en minuscules, sans guillemets : jamais "oui", "true" ou 1.

3.2 Statuts de mission
----------------------

| Statut | Signification | Passé à ce statut quand |
| --- | --- | --- |
| en_attente | Créée, pas encore remise au robot | l'utilisateur crée la mission |
| envoyee | Remise au robot par le GET | le robot récupère la mission |
| recue | Le robot confirme l'avoir lue | message mission_recue enregistré |
| en_cours | Exécution commencée | premier message etape_atteinte |
| terminee | Toutes les étapes faites | changement_etat vers repos avec mission_terminee: true |
| echouee | Arrêt définitif signalé par le robot | incident de gravité bloquant |
| non_confirmee | Le résultat n'a pas pu être confirmé | règle de la section 6.6 |

3.3 Types de messages
---------------------

| Type | Sens | Rôle |
| --- | --- | --- |
| mission | application vers robot | ordre de mission |
| mission_recue | robot vers application | accusé de réception de la mission |
| etape_atteinte | robot vers application | une étape (zone) est atteinte |
| mesure | robot vers application | humidité d'une zone |
| changement_etat | robot vers application | l'état du robot change |
| incident | robot vers application | problème détecté |

États du robot : repos, en_deplacement, en_mesure, arret, erreur, hors_ligne.

4. Format des messages JSON
===========================

4.1 Champs communs
------------------

Tous les messages envoyés par le robot portent ces cinq champs, tous obligatoires.

| Champ | Type | Règle |
| --- | --- | --- |
| message_id | texte | 16 caractères hexadécimaux, unique, clé anti-doublon |
| num_sequence | entier | croissant, sert à l'ordre et aux trous |
| type | texte | un des types de la section 3.3 |
| horodatage | texte ou null | ISO 8601 UTC ; null si le NTP a échoué |
| uptime_ms | entier | millisecondes depuis le démarrage du robot |

4.2 mission (application vers robot)
------------------------------------

Renvoyée par GET /api/robot/mission. Elle n'a pas de num_sequence : elle est identifiée par mission_id. Si le robot récupère deux fois la même mission, il ignore la seconde.

```json
{
  "type": "mission",
  "mission_id": 12,
  "cree_le": "2026-11-03T10:00:00Z",
  "duree_prevue_s": 600,
  "etapes": [
    {"etape": 1, "zone_id": 1},
    {"etape": 2, "zone_id": 2},
    {"etape": 3, "zone_id": 3}
  ]
}
```

4.3 mission_recue
-----------------

Envoyé avant que le robot démarre. Il prouve que le robot a lu et accepté la mission.

```json
{"message_id": "a41c09e2d7f3b856", "num_sequence": 1, "type": "mission_recue",
 "horodatage": "2026-11-03T10:00:04Z", "uptime_ms": 184200, "mission_id": 12}
```

4.4 etape_atteinte
------------------

```json
{"message_id": "5be2f0137a9c4d68", "num_sequence": 2, "type": "etape_atteinte",
 "horodatage": "2026-11-03T10:01:10Z", "uptime_ms": 250900,
 "mission_id": 12, "etape": 1, "zone_id": 1}
```

4.5 mesure
----------

humidite_pct (0 à 100) est la valeur étalonnée utilisée par la règle d'irrigation. valeur_brute est la lecture du capteur, pour le diagnostic seulement. Quand le capteur est invalide, valide vaut false et humidite_pct vaut null.

```json
{"message_id": "c7d81a4f02e9b365", "num_sequence": 3, "type": "mesure",
 "horodatage": "2026-11-03T10:01:14Z", "uptime_ms": 254800,
 "mission_id": 12, "zone_id": 1,
 "humidite_pct": 34.5, "valeur_brute": 2310, "valide": true}
```

4.6 changement_etat
-------------------

mission_terminee vaut true uniquement dans le dernier changement d'état d'une mission réussie.

```json
{"message_id": "0e6b93d1c5a7f284", "num_sequence": 9, "type": "changement_etat",
 "horodatage": "2026-11-03T10:08:40Z", "uptime_ms": 760100,
 "mission_id": 12, "etat_precedent": "en_mesure", "etat_nouveau": "repos",
 "mission_terminee": true}
```

4.7 incident
------------

gravite vaut info, avertissement ou bloquant. Seul bloquant fait passer la mission à echouee.

| Code | Créé par | Cas |
| --- | --- | --- |
| OBSTACLE | robot | obstacle détecté par le HC-SR04 |
| FILE_PLEINE | robot | messages perdus car la file est pleine (avec nb_perdus) |
| NTP_ECHEC | robot | heure non récupérée au démarrage |
| CAPTEUR_INVALIDE | application | mesure reçue avec valide: false |
| MESSAGE_CONFLIT | application | même message_id, contenu différent |
| MISSION_NON_CONFIRMEE | application | règle de la section 6.6 |

```json
{"message_id": "7a30c5e19b4d2f68", "num_sequence": 15, "type": "incident",
 "horodatage": "2026-11-03T10:04:02Z", "uptime_ms": 500300,
 "mission_id": 12, "code": "FILE_PLEINE", "gravite": "avertissement",
 "description": "File pleine pendant la coupure", "nb_perdus": 12}
```

4.8 Réponse de l'application
----------------------------

Réponse à un message accepté (200) :

```json
{"statut": "ok", "message_id": "c7d81a4f02e9b365",
 "recommandation_arrosage": "arroser"}
```

- Pour un doublon (même message_id, même contenu), l'application renvoie exactement la même réponse que la première fois, sans rien enregistrer.
- recommandation_arrosage n'est présent que pour une mesure. Valeurs : arroser, ne_pas_arroser, interdite (mesure invalide).

Réponse à une erreur (4xx ou 5xx) :

```json
{"statut": "erreur", "code": "MESSAGE_CONFLIT",
 "detail": "message_id déjà reçu avec un contenu différent"}
```

5. API HTTP
===========

5.1 Authentification (token en en-tête)
---------------------------------------

Chaque requête du robot porte l'en-tête Authorization: Token <jeton>. Le jeton est créé une fois par l'administrateur, stocké dans la configuration de l'ESP32, et jamais placé dans l'URL. Sans jeton ou avec un jeton faux, l'application répond 401 et n'enregistre rien.

5.2 Tableau des endpoints
-------------------------

| Méthode et chemin | Rôle | Réponses |
| --- | --- | --- |
| GET /api/robot/mission | le robot récupère la mission en attente (toutes les 3 s) | 200, 204, 401 |
| POST /api/robot/messages | le robot envoie un message de n'importe quel type | 200, 400, 401, 409, 422, 5xx |
| POST /api/robot/etat | le robot signale son état (message changement_etat) | 200, 400, 401, 409, 422, 5xx |
| POST /api/robot/messages/sync | le robot renvoie sa file après une coupure (tous types) | 200, 400, 401, 5xx |

5.3 Récupérer la mission (GET)
------------------------------

- 200 avec le JSON de la section 4.2 s'il y a une mission à exécuter ; 204 sans corps sinon.
- Tant que le message mission_recue n'est pas enregistré, l'application renvoie la même mission à chaque appel. Une réponse perdue ne fait donc jamais perdre la mission.
- Dès que mission_recue est enregistré, le GET renvoie 204.
- Le délai maximal d'attente de la réponse est de 5 s ; au-delà le robot considère l'appel comme échoué.

5.4 Envoyer un message (POST)
-----------------------------

Corps : un message de la section 4 (type mission_recue, etape_atteinte, mesure, changement_etat ou incident). Réponse 200 de la section 4.8 si le message est enregistré ou si c'est un doublon identique.

Signaler l'état. POST /api/robot/etat accepte uniquement le type changement_etat (section 4.6) ; tout autre type reçoit 422. Le traitement est identique à celui de POST /api/robot/messages : même contrôle du message_id, mêmes réponses et mêmes codes d'erreur (5.6). Cet endpoint correspond au topic MQTT roboagri/etat (8.4). La file de renvoi (7.2) peut contenir des changement_etat : ils partent alors par l'endpoint de sync.

5.5 Renvoi groupé (sync)
------------------------

Après une coupure, le robot envoie sa file en un seul appel :

```json
{"messages": [ {"message_id": "...", "num_sequence": 4, ...},
               {"message_id": "...", "num_sequence": 5, ...} ]}
```

- 20 messages au maximum par appel, classés par num_sequence croissant.
- L'application traite les messages dans cet ordre, un par un, avec les mêmes règles que le POST simple.
- Réponse 200 avec un résultat par message ; une erreur sur l'un n'empêche pas les suivants.

```json
{"resultats": [
  {"message_id": "...", "statut": "ok"},
  {"message_id": "...", "statut": "erreur", "code": "MESSAGE_CONFLIT"}
]}
```

5.6 Codes d'erreur et réaction du robot
---------------------------------------

| Code | Cause | Réaction du robot |
| --- | --- | --- |
| 200 | message enregistré ou doublon identique | retire le message de la file |
| 204 | pas de mission (GET) | continue le polling |
| 400 | JSON invalide ou champ obligatoire manquant | retire le message, le note dans son journal local, ne le renvoie pas |
| 401 | jeton absent ou invalide | garde la file, arrête les envois, réessaie toutes les 30 s |
| 409 | même message_id, contenu différent | retire le message, ne le renvoie pas (l'application a créé l'incident) |
| 422 | valeur incohérente (par exemple humidite_pct hors de 0 à 100, mission_id inconnu, type non accepté par l'endpoint) | retire le message, le note dans son journal local |
| 5xx, délai dépassé, réseau coupé | application ou réseau indisponible | garde le message, réessaie après 3 s, 6 s, 12 s, puis toutes les 30 s |

6. Comportements exigés par le sujet
====================================

6.1 Envoi d'une mission
-----------------------

1. L'utilisateur crée la mission dans l'application : statut en_attente.
2. Au prochain polling (3 s au plus), le robot appelle GET /api/robot/mission et reçoit la mission : statut envoyee.
3. Le robot vérifie la mission, puis envoie mission_recue avant de démarrer : statut recue. Tant que ce message n'est pas enregistré, le GET renvoie la même mission.
4. Le robot démarre ; au premier etape_atteinte, la mission passe à en_cours.

6.2 Réception des mesures et changements d'état
-----------------------------------------------

- L'application contrôle le jeton, la validité du JSON, puis le message_id (6.3), avant d'enregistrer.
- Une mesure valide est enregistrée avec humidite_pct et valeur_brute ; la règle d'irrigation s'applique à humidite_pct seulement et la réponse contient recommandation_arrosage.
- Une mesure avec valide: false est enregistrée, l'application crée l'incident CAPTEUR_INVALIDE et répond interdite : aucune recommandation d'arrosage n'est produite.
- Un changement_etat met à jour l'état courant du robot ; avec mission_terminee: true, la mission passe à terminee.
- Le trou de num_sequence (86 puis 88) est noté par l'application sans bloquer le traitement : le 87 est peut-être simplement en retard.

6.3 Messages répétés
--------------------

| Cas | Réponse | Effet |
| --- | --- | --- |
| message_id déjà reçu, contenu identique | 200, même réponse que la première fois | rien n'est enregistré |
| message_id déjà reçu, contenu différent | 409 | incident MESSAGE_CONFLIT, le message d'origine reste inchangé |

« Contenu identique » signifie que tous les champs du message sont identiques, uptime_ms compris.

6.4 Interruption de communication
---------------------------------

Si un envoi échoue (réseau coupé, délai de 5 s dépassé, 5xx), le robot continue sa mission avec les informations déjà reçues. Il place chaque nouveau message dans sa file en RAM (7.1). Dès que le réseau revient, il renvoie la file par l'endpoint de sync, dans l'ordre de num_sequence (7.2). Si la file a débordé, il envoie ensuite un incident FILE_PLEINE.

6.5 Non-duplication
-------------------

La non-duplication repose sur une colonne message_id unique en base. L'application vérifie le message_id et enregistre le message dans la même transaction. Si deux requêtes identiques arrivent en même temps, la contrainte d'unicité en laisse passer une seule ; l'autre est traitée comme un doublon. num_sequence n'intervient pas.

6.6 Missions non confirmées
---------------------------

Une mission recue ou en_cours passe à non_confirmee quand l'une des deux conditions est vraie :

| Condition | Valeur par défaut | Rôle |
| --- | --- | --- |
| Silence du robot : aucun message reçu depuis N cycles de polling | N = 10, soit 30 s | détecter vite une panne ou une coupure |
| Plafond global : durée écoulée depuis recue supérieure à 3 fois duree_prevue_s | 3 × la durée prévue | borner la mission même si le robot continue de communiquer |

N et le facteur 3 sont configurables dans l'application.

Pourquoi les deux : le silence seul ne voit pas un robot qui communique mais n'avance plus ; le plafond seul fait attendre trop longtemps après une vraie panne. Au passage à non_confirmee, l'application crée l'incident MISSION_NON_CONFIRMEE en indiquant la cause (silence ou plafond).

7. Côté ESP32
=============

7.1 File de messages et taille maximale
---------------------------------------

Le robot garde les messages non confirmés dans une file en RAM, limitée à 100 messages. Un message y reste jusqu'à la réponse 200 (ou jusqu'à un 400, 409 ou 422 qui le rejette définitivement, voir 5.6).

Quand la file est pleine, le message le plus ancien est écrasé et le robot compte les messages perdus. Au retour du réseau, il envoie un incident FILE_PLEINE avec nb_perdus. Limite assumée : une file en RAM est perdue si le robot redémarre ; la file en flash est notée comme amélioration (section 10).

```python
TAILLE_MAX = 100
file_msgs = []
nb_perdus = 0

def empiler(msg):
    global nb_perdus
    if len(file_msgs) >= TAILLE_MAX:
        file_msgs.pop(0)      # on écrase le plus ancien
        nb_perdus += 1
    file_msgs.append(msg)
```

7.2 Renvoi dans l'ordre de num_sequence
---------------------------------------

1. Le robot n'envoie rien en direct tant que la file n'est pas vide : tout nouveau message est ajouté à la fin, pour garder l'ordre.
2. Il envoie la file par paquets de 20 messages au plus, de l'ancien au récent (num_sequence croissant), via POST /api/robot/messages/sync.
3. Pour chaque résultat ok, ou erreur définitive (409, 422), le message sort de la file.
4. Au premier échec réseau, 5xx ou 401, il s'arrête, garde le reste et réessaie selon 5.6.
5. Quand la file est vide, il reprend les envois directs par POST /api/robot/messages.

7.3 Sauvegarde du compteur en flash
-----------------------------------

num_sequence doit rester croissant même après un redémarrage, sans écrire en flash à chaque message (usure). Le compteur est tenu en RAM : c'est lui qui est incrémenté à chaque message. Il est ensuite copié dans un fichier en flash seulement tous les N messages (N = 10), ce qui réduit l'usure de la flash par rapport à une écriture à chaque message. Au démarrage, il lit la valeur sauvegardée et ajoute N : le compteur ne revient jamais en arrière, mais la séquence peut contenir des trous. Ce n'est pas grave, car les doublons sont gérés par message_id.

```python
PAS = 10

def charger_compteur():
    try:
        with open("compteur.txt") as f:
            return int(f.read()) + PAS
    except OSError:
        return 0

def prochain_num():
    global compteur
    compteur += 1
    if compteur % PAS == 0:
        with open("compteur.txt", "w") as f:
            f.write(str(compteur))
    return compteur
```

7.4 Détection d'un capteur invalide
-----------------------------------

Après chaque lecture, le robot compare valeur_brute à deux bornes de la configuration : en dessous de BRUT_MIN_VALIDE (capteur débranché ou court-circuité) ou au-dessus de BRUT_MAX_VALIDE, la mesure est invalide. Il envoie alors une mesure avec valide: false et humidite_pct: null, et il ne calcule aucun pourcentage.

L'étalonnage (valeur brute à sec, valeur brute dans l'eau, les deux bornes ci-dessus) vit dans la configuration du robot. Ces valeurs de référence sont à documenter dans le dossier de tests.

8. Évolution vers MQTT
======================

En phase 2, le polling HTTP est remplacé par un broker MQTT (Mosquitto). Les corps JSON de la section 4 ne changent pas ; seuls le transport et l'accusé de réception changent.

8.1 Topics et QoS
-----------------

| Topic | Sens | Messages | QoS |
| --- | --- | --- | --- |
| roboagri/mission | application vers robot | mission (message conservé par le broker) | 1 |
| roboagri/etape | robot vers application | mission_recue, etape_atteinte | 1 |
| roboagri/mesure | robot vers application | mesure | 1 |
| roboagri/etat | robot vers application | changement_etat | 1 |
| roboagri/incident | robot vers application | incident | 1 |
| roboagri/ack | application vers robot | accusé de réception d'un message | 1 |

Le QoS 1 garantit au moins une livraison, donc un message peut arriver deux fois : message_id reste la clé anti-doublon, comme en HTTP. Les topics ne contiennent pas d'identifiant de robot (2.2).

8.2 Accusé de réception (roboagri/ack)
--------------------------------------

En HTTP, la réponse 200 sert d'accusé. En MQTT, l'application publie sur roboagri/ack après chaque message traité :

```json
{"message_id": "c7d81a4f02e9b365", "statut": "ok", "recommandation_arrosage": "arroser"}
```

- Le robot ne retire un message de sa file qu'après l'accusé correspondant. Sans accusé après 5 s, il republie le même message, avec le même message_id.
- Pour une erreur, l'accusé porte "statut": "erreur" et un code, avec les mêmes règles de réaction que la section 5.6.

8.3 Last Will
-------------

À la connexion, le robot déclare un Last Will : si le broker perd le robot sans déconnexion propre, il publie lui-même ce message sur roboagri/etat (QoS 1, conservé) :

```json
{"message_id": "e19d4a7c60b3f258", "num_sequence": null, "type": "changement_etat",
 "horodatage": null, "uptime_ms": null, "etat_nouveau": "hors_ligne"}
```

C'est le seul cas où num_sequence et horodatage valent null : le message est préparé à la connexion, avant la panne. Le message_id est tiré à chaque connexion. À la connexion suivante, le robot publie repos sur le même topic, ce qui remplace le message conservé. Le Last Will alimente la règle du silence de la section 6.6.

8.4 Tableau de correspondance HTTP / MQTT
-----------------------------------------

| Fonction | HTTP (phase 1) | MQTT (phase 2) |
| --- | --- | --- |
| Récupérer la mission | GET /api/robot/mission toutes les 3 s | abonnement à roboagri/mission |
| Envoyer un message | POST /api/robot/messages | publication sur le topic du type |
| Signaler l'état | POST /api/robot/etat | publication sur roboagri/etat |
| Accusé de réception | réponse 200 | message sur roboagri/ack |
| Renvoi après coupure | POST /api/robot/messages/sync | republication de la file, dans l'ordre |
| Authentification | en-tête Authorization: Token | identifiant et mot de passe du broker |
| Détection de robot absent | silence de 30 s (6.6) | Last Will, plus silence (6.6) |
| Doublons | message_id unique | message_id unique (inchangé) |

9. Scénarios complets (requêtes et réponses)
============================================

Dans tous les exemples, chaque requête porte Authorization: Token <jeton> et Content-Type: application/json, sauf le 9.6. Les champs horodatage et uptime_ms sont abrégés par … pour la lisibilité ; ils sont obligatoires en vrai.

9.1 Cas nominal
---------------

```http
GET /api/robot/mission
-> 200  {"type":"mission","mission_id":12,"duree_prevue_s":600,
          "etapes":[{"etape":1,"zone_id":1},{"etape":2,"zone_id":2}]}

POST /api/robot/messages
{"message_id":"a41c09e2d7f3b856","num_sequence":1,"type":"mission_recue","mission_id":12,…}
-> 200  {"statut":"ok","message_id":"a41c09e2d7f3b856"}      # mission : recue

GET /api/robot/mission
-> 204                                                       # plus de répétition

POST /api/robot/messages
{"message_id":"5be2f0137a9c4d68","num_sequence":2,"type":"etape_atteinte","etape":1,"zone_id":1,…}
-> 200  {"statut":"ok","message_id":"5be2f0137a9c4d68"}      # mission : en_cours

POST /api/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure","zone_id":1,
 "humidite_pct":34.5,"valeur_brute":2310,"valide":true,…}
-> 200  {"statut":"ok","message_id":"c7d81a4f02e9b365","recommandation_arrosage":"arroser"}

... (etape 2, mesure de la zone 2) ...

POST /api/robot/messages
{"message_id":"0e6b93d1c5a7f284","num_sequence":9,"type":"changement_etat",
 "etat_precedent":"en_mesure","etat_nouveau":"repos","mission_terminee":true,…}
-> 200  {"statut":"ok","message_id":"0e6b93d1c5a7f284"}      # mission : terminee
```

9.2 Doublon (même contenu)
--------------------------

La réponse 200 du message c7d81a4f02e9b365 s'est perdue ; le robot le renvoie tel quel.

```http
POST /api/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure", ... (identique) ...}
-> 200  {"statut":"ok","message_id":"c7d81a4f02e9b365","recommandation_arrosage":"arroser"}
```

Résultat : réponse identique à la première, une seule mesure en base.

9.3 Doublon avec contenu différent (409)
----------------------------------------

```http
POST /api/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure","zone_id":1,
 "humidite_pct":12.0,"valeur_brute":3400,"valide":true,…}
-> 409  {"statut":"erreur","code":"MESSAGE_CONFLIT",
         "detail":"message_id déjà reçu avec un contenu différent"}
```

Résultat : la mesure d'origine reste inchangée, l'application crée l'incident MESSAGE_CONFLIT, le robot retire le message de sa file sans le renvoyer.

9.4 Coupure puis renvoi
-----------------------

1. Le Wi-Fi tombe après le message 3. Les messages 4, 5 et 6 (deux mesures et une étape) sont mis en file ; les envois directs échouent après 5 s (réessais à 3 s, 6 s, 12 s, puis 30 s).
2. Le Wi-Fi revient. Le robot envoie la file d'un seul appel, dans l'ordre :

```http
POST /api/robot/messages/sync
{"messages":[ {"message_id":"…","num_sequence":4,…},
               {"message_id":"…","num_sequence":5,…},
               {"message_id":"…","num_sequence":6,…} ]}
-> 200  {"resultats":[{"message_id":"…","statut":"ok"},
                     {"message_id":"…","statut":"ok"},
                     {"message_id":"…","statut":"ok"}]}
```

3. La file est vide : le robot reprend les envois directs. Les horodatages d'origine sont conservés (3.1).

Si la file avait dépassé 100 messages, le robot enverrait ensuite un incident FILE_PLEINE avec nb_perdus.

9.5 Mission non confirmée
-------------------------

1. La mission 12 est en_cours ; le dernier message reçu date de 10:04:00.
2. À 10:04:30 (10 cycles de 3 s sans message), l'application passe la mission à non_confirmee et crée l'incident MISSION_NON_CONFIRMEE avec la cause silence.
3. La mission reste non_confirmee et l'utilisateur décide de la relancer.

Même résultat par le plafond : une mission de 600 s prévues, restant en_cours après 1 800 s, passe à non_confirmee avec la cause plafond.

9.6 Token invalide
------------------

```http
POST /api/robot/messages
Authorization: Token mauvais_jeton
{"message_id":"…","num_sequence":10,"type":"mesure",…}
-> 401  {"statut":"erreur","code":"JETON_INVALIDE","detail":"jeton absent ou invalide"}
```

Résultat : rien n'est enregistré. Le robot garde le message en file, arrête ses envois et réessaie toutes les 30 s ; une fois le jeton corrigé dans sa configuration, la file repart dans l'ordre.

9.7 Capteur invalide
--------------------

Le capteur est débranché : la lecture brute est hors des bornes valides (7.4).

```http
POST /api/robot/messages
{"message_id":"b82e51f7d0a3c496","num_sequence":11,"type":"mesure","zone_id":2,
 "humidite_pct":null,"valeur_brute":0,"valide":false,…}
-> 200  {"statut":"ok","message_id":"b82e51f7d0a3c496","recommandation_arrosage":"interdite"}
```

Résultat : la mesure est enregistrée avec sa valeur brute pour le diagnostic, l'application crée l'incident CAPTEUR_INVALIDE, et aucun arrosage n'est recommandé pour cette zone.

10. Limites et points ouverts
=============================

- File en RAM : les messages en attente sont perdus si le robot redémarre ou perd le courant pendant une coupure. Amélioration prévue si le temps le permet : file persistée en flash (survit au redémarrage, mais code plus lourd et usure de la flash).
- File limitée à 100 messages : au-delà, les plus anciens sont perdus ; seul l'incident FILE_PLEINE en garde la trace.
- Trous de num_sequence : l'application les détecte et les note, mais ne redemande pas le message manquant. Les sauts de N au redémarrage (7.3) en créent volontairement.
- Heure du robot : sans NTP, horodatage vaut null et l'application utilise l'heure de réception, donc approximative pour un message renvoyé.
- Sécurité : le jeton est statique et le trafic HTTP du labo n'est pas chiffré. Acceptable pour le projet ; à remplacer par HTTPS et un jeton renouvelable en production.
- Un seul robot : en ajouter un second demande un identifiant de robot dans les messages, des topics par robot et une unicité de message_id par robot.
