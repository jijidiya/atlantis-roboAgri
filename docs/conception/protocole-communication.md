# Protocole de communication RoboAgri-Kin

Version 1.1 (16 novembre 2026). Le robot ESP32 interroge l'application Django toutes les 3 s (HTTP), envoie ses messages JSON avec un `message_id` unique, garde en file ceux qu'il n'a pas pu envoyer et les renvoie au retour du réseau ; l'application ignore les doublons. **Un message `mesure` regroupe les lectures d'une étape** (jusqu'à 9). Une table de correspondance (8.4) prépare le passage à MQTT.

> **Priorité en cas de divergence** : ce protocole a été écrit avant le modèle de données (MPD). Le MPD fait foi pour les tables, les champs et les règles de gestion ; ce document décrit ce que le MPD ne couvre pas (adresses, authentification, réponses, codes d'erreur, comportement du robot). La version 1.1 aligne le protocole sur le MPD et sur le code du backend.

## Changements par rapport à la version 1.0

À lire en premier par le binôme qui programme l'ESP32 (le firmware doit suivre le point 1).

| N° | Sujet | Version 1.0 | Version 1.1 |
| --- | --- | --- | --- |
| 1 | Message `mesure` | un message par zone, une seule humidité | **un message par étape** : `etape` et un tableau `lectures` de 1 à 9 éléments (3 points × 3 lectures) |
| 2 | Statuts de mission | sept statuts (`en_attente`, `envoyee`, `recue`...) | cinq statuts du MPD : `planifiee`, `en_cours`, `terminee`, `interrompue`, `non_confirmee` (3.2) |
| 3 | Incidents | codes en majuscules et gravité | quatre types du MPD, sans gravité enregistrée (4.7) ; `MESSAGE_CONFLIT` et `NTP_ECHEC` ne sont plus enregistrés |
| 4 | Conflit de `message_id` | `409` et incident `MESSAGE_CONFLIT` | `409` seulement, aucun incident créé (2.3, 6.3) |
| 5 | Mission envoyée au robot | contient `duree_prevue_s` | ne contient plus `duree_prevue_s` (absent du MPD) |
| 6 | Missions non confirmées | silence **et** plafond de durée | **silence seulement** (6.6) |
| 7 | `mission_id` | présent dans chaque type de message, hors champs communs | **champ commun obligatoire** de tous les messages (4.1) |
| 8 | Adresses | `/api/robot/...` | `/api/v1/robot/...`, sans slash final (5.2) |
| 9 | Codes d'erreur | liste générale | codes précis pour les 400, 409 et 422 (5.6) |
| 10 | Réponse `401` | corps du protocole | corps par défaut de DRF ; le robot ne lit que le code `401` (5.1) |

## 1. Objet et périmètre

Ce document fixe les règles d'échange entre le robot ESP32 et l'application Django, de façon qu'un membre d'un autre binôme puisse implémenter l'API ou le client robot sans poser de question.

Ce que le protocole couvre :

- le transport (HTTP en polling, évolution vers MQTT) ;
- le format des messages JSON dans les deux sens ;
- l'API HTTP : endpoints, authentification, codes d'erreur ;
- les six comportements exigés par le sujet : envoi de mission, réception, messages répétés, coupure, non-duplication, missions non confirmées ;
- le comportement côté ESP32 : file d'attente, renvoi, sauvegarde du compteur.

Ce qu'il ne couvre pas : la règle de décision d'irrigation (document d'analyse), le schéma complet de la base de données (modèle de données, binôme B), le câblage et l'étalonnage physique du capteur.

Vocabulaire. « Robot » désigne l'ESP32 ; « application » désigne le serveur Django ; « message » désigne un objet JSON envoyé par le robot ; « mission » est l'ordre envoyé par l'application au robot ; « étape » est la visite d'une zone pendant une mission.

## 2. Principes

### 2.1 Transport : HTTP (polling 3 s), MQTT en évolution

Le projet démarre en HTTP : le robot interroge l'application toutes les 3 secondes pour récupérer une mission, et envoie ses messages par POST. C'est le plus simple à tester et à déboguer. Le contenu des messages est identique à celui qu'on enverrait en MQTT : changer de transport ne demande pas de réécrire les messages (section 8).

### 2.2 Un seul robot, pas d'identifiant de robot

Il n'y a qu'un seul robot. Aucun identifiant de robot n'est donc prévu dans les messages, et les topics MQTT n'ont pas d'identifiant de robot. Si un second robot apparaît, il faudra ajouter cet identifiant, l'inclure dans les topics et revoir la règle d'unicité de `message_id` (section 10).

### 2.3 message_id (anti-doublon) et num_sequence (ordre)

Deux identifiants, deux rôles séparés :

- `message_id` identifie le message. C'est la seule clé anti-doublon : c'est la clé primaire de la table `message`. Un `message_id` déjà reçu avec le même contenu renvoie la même réponse (200) sans rien enregistrer. Avec un contenu différent : 409 Conflict, rien n'est enregistré et le message d'origine reste inchangé.
- `num_sequence` donne l'ordre des messages et permet de détecter les trous (86 puis 88 signifie que le 87 manque). Il ne sert jamais à dédupliquer.

Pourquoi les deux : si l'ESP32 redémarre et perd son compteur, le dédoublonnage reste correct ; MQTT en QoS 1 peut livrer deux fois un message ; l'unicité en base repose sur une clé primaire, facile à tester.

### 2.4 Valeur mesurée (%) et valeur brute (diagnostic)

Le robot envoie l'humidité étalonnée en pourcentage (`humidite_pct`), utilisée par la règle d'irrigation, et la valeur brute du capteur (`valeur_brute`), uniquement pour le diagnostic. La règle de décision ne s'applique jamais à la valeur brute. L'étalonnage vit dans la configuration de l'ESP32 ; la valeur brute permet de recalculer le pourcentage si besoin.

### 2.5 Un message par étape

Pendant une étape, le robot prend **3 points de collecte, avec 3 lectures par point**, soit 9 lectures au plus. Il les regroupe dans **un seul message `mesure`**, envoyé quand l'étape est terminée. Le serveur enregistre le message et toutes ses lectures dans une seule transaction : tout est enregistré, ou rien.

## 3. Conventions

### 3.1 Noms de champs, encodage, dates ISO 8601 UTC

- Noms de champs en snake_case, sans accent, en français (`humidite_pct`, `num_sequence`).
- JSON encodé en UTF-8, en-tête `Content-Type: application/json`.
- Dates au format ISO 8601 en UTC, avec le suffixe Z : `2026-11-03T10:15:30Z`.
- Le robot récupère l'heure par NTP au démarrage (le Wi-Fi du labo doit avoir un accès Internet) puis horodate chaque message lui-même. Un message renvoyé après une coupure garde donc l'heure de sa mesure, pas celle du renvoi.
- Si le NTP échoue, le robot continue de fonctionner : `horodatage` vaut `null`, et `uptime_ms` (temps écoulé depuis le démarrage, en millisecondes) permet de situer les messages entre eux. L'application utilise alors l'heure de réception pour les dates qu'elle enregistre.
- `message_id` : 16 caractères hexadécimaux en minuscules, tirés au hasard (`os.urandom(8).hex()`), par exemple `9f3a1c7e5b2d4086`. Aucun état à sauvegarder.
- Les booléens s'écrivent `true` ou `false` en minuscules, sans guillemets : jamais `"oui"`, `"true"` ou `1`.

### 3.2 Statuts de mission

Les statuts sont ceux du modèle de données. Le robot ne les envoie pas : l'application les fait évoluer d'après les messages reçus.

| Statut | Signification | Passé à ce statut quand |
| --- | --- | --- |
| `planifiee` | Créée, pas encore démarrée | l'utilisateur crée la mission |
| `en_cours` | Exécution commencée | premier message `etape_atteinte` |
| `terminee` | Toutes les étapes faites | `changement_etat` vers `repos` avec `mission_terminee: true` |
| `interrompue` | Arrêt signalé | incident `OBSTACLE` pendant que la mission est `en_cours`, ou action manuelle de l'utilisateur |
| `non_confirmee` | Le résultat n'a pas pu être confirmé | règle de la section 6.6 |

Deux notions de la version 1.0 n'ont pas de statut propre :

- **mission envoyée au robot** : la mission est simplement renvoyée à chaque `GET` tant que le robot ne l'a pas accusée ;
- **mission reçue** : c'est l'existence d'un message `mission_recue` pour cette mission. Dès qu'il est enregistré, le `GET` ne renvoie plus la mission (5.3), même si son statut reste `planifiee` jusqu'au premier `etape_atteinte`.

### 3.3 Types de messages

| Type | Sens | Rôle | Enregistré dans `message` |
| --- | --- | --- | --- |
| `mission` | application vers robot | ordre de mission | non (pas de `message_id`) |
| `mission_recue` | robot vers application | accusé de réception de la mission | oui |
| `etape_atteinte` | robot vers application | une étape (zone) est atteinte | oui |
| `mesure` | robot vers application | lectures d'humidité d'une étape | oui |
| `changement_etat` | robot vers application | l'état du robot change | oui |
| `incident` | robot vers application | problème détecté | oui |

États du robot : `repos`, `en_deplacement`, `en_mesure`, `arret`, `erreur`, `hors_ligne`.

## 4. Format des messages JSON

### 4.1 Champs communs

Tous les messages envoyés par le robot portent ces six champs, tous obligatoires côté robot.

| Champ | Type | Règle |
| --- | --- | --- |
| `message_id` | texte | 16 caractères hexadécimaux en minuscules, unique, clé anti-doublon |
| `num_sequence` | entier | croissant, sert à l'ordre et aux trous |
| `type` | texte | un des types du robot de la section 3.3 |
| `mission_id` | entier | mission concernée (existe dans l'application) |
| `horodatage` | texte ou `null` | ISO 8601 UTC ; `null` si le NTP a échoué |
| `uptime_ms` | entier | millisecondes depuis le démarrage du robot |

Le serveur refuse (400) un message sans `message_id`, `num_sequence`, `type` ou `mission_id`. `horodatage` et `uptime_ms` sont conservés tels que reçus. Le seul message sans `mission_id` serait le Last Will de MQTT (8.3), traité en phase 2.

### 4.2 mission (application vers robot)

Renvoyée par `GET /api/v1/robot/mission`. Elle n'a pas de `num_sequence` : elle est identifiée par `mission_id`. Si le robot récupère deux fois la même mission, il ignore la seconde.

```json
{
  "type": "mission",
  "mission_id": 12,
  "cree_le": "2026-11-03T10:00:00Z",
  "etapes": [
    {"etape": 1, "zone_id": 1},
    {"etape": 2, "zone_id": 2},
    {"etape": 3, "zone_id": 3}
  ]
}
```

`etape` est le numéro d'ordre de l'étape dans la mission (à partir de 1) : c'est ce numéro que le robot renvoie dans `etape_atteinte` et `mesure`.

### 4.3 mission_recue

Envoyé avant que le robot démarre. Il prouve que le robot a lu et accepté la mission.

```json
{"message_id": "a41c09e2d7f3b856", "num_sequence": 1, "type": "mission_recue",
 "horodatage": "2026-11-03T10:00:04Z", "uptime_ms": 184200, "mission_id": 12}
```

### 4.4 etape_atteinte

`etape` et `zone_id` doivent correspondre à une étape de la mission. Sinon : 422.

```json
{"message_id": "5be2f0137a9c4d68", "num_sequence": 2, "type": "etape_atteinte",
 "horodatage": "2026-11-03T10:01:10Z", "uptime_ms": 250900,
 "mission_id": 12, "etape": 1, "zone_id": 1}
```

### 4.5 mesure

Un message `mesure` regroupe les lectures d'**une** étape.

```json
{"message_id": "c7d81a4f02e9b365", "num_sequence": 3, "type": "mesure",
 "horodatage": "2026-11-03T10:01:14Z", "uptime_ms": 254800,
 "mission_id": 12, "etape": 1, "zone_id": 1,
 "lectures": [
   {"numero_point": 1, "numero_lecture": 1, "humidite_pct": 34.5, "valeur_brute": 2310, "valide": true},
   {"numero_point": 1, "numero_lecture": 2, "humidite_pct": 34.1, "valeur_brute": 2318, "valide": true},
   {"numero_point": 1, "numero_lecture": 3, "humidite_pct": null, "valeur_brute": 0, "valide": false}
 ]}
```

Cet exemple est un extrait : un message complet contient jusqu'à 9 lectures (points 1 à 3, lectures 1 à 3).

Règles du champ `lectures` :

- 1 à 9 éléments ; `numero_point` et `numero_lecture` valent chacun 1, 2 ou 3 ; la même paire (point, lecture) ne peut apparaître qu'une fois. Sinon : 422 `LECTURES_INVALIDES`.
- `humidite_pct` (0 à 100) est la valeur étalonnée utilisée par la règle d'irrigation. Pour une lecture valide, une valeur hors de 0 à 100 donne 422 `HUMIDITE_INVALIDE`.
- `valeur_brute` est la lecture du capteur, pour le diagnostic seulement.
- Quand le capteur est invalide, `valide` vaut `false` et `humidite_pct` vaut `null`.
- Une lecture qui n'a pas pu être faite est simplement **omise** du tableau. Le statut `manquante` du modèle de données est réservé à un usage ultérieur.
- `etape` et `zone_id` doivent désigner la même étape de la mission. Sinon : 422 `ETAPE_INCONNUE` ou `ZONE_INCOHERENTE`.

### 4.6 changement_etat

`mission_terminee` vaut `true` uniquement dans le dernier changement d'état d'une mission réussie.

```json
{"message_id": "0e6b93d1c5a7f284", "num_sequence": 9, "type": "changement_etat",
 "horodatage": "2026-11-03T10:08:40Z", "uptime_ms": 760100,
 "mission_id": 12, "etat_precedent": "en_mesure", "etat_nouveau": "repos",
 "mission_terminee": true}
```

### 4.7 incident

Le modèle de données connaît quatre types d'incident : `obstacle`, `capteur_defaillant`, `perte_communication`, `mesure_invalide`. Les codes du robot sont traduits ainsi. La gravité, si le robot l'envoie, est conservée dans le message mais pas dans la table des incidents.

| Code | Créé par | Cas | Type enregistré (MPD) | Effet |
| --- | --- | --- | --- | --- |
| `OBSTACLE` | robot | obstacle détecté par le HC-SR04 | `obstacle` | la mission passe à `interrompue` si elle est `en_cours` |
| `FILE_PLEINE` | robot | messages perdus car la file est pleine (avec `nb_perdus`) | `perte_communication` | aucun |
| `NTP_ECHEC` | robot | heure non récupérée au démarrage | *(aucun)* | le message est enregistré, pas d'incident |
| `CAPTEUR_INVALIDE` | application | lecture reçue avec `valide: false` | `mesure_invalide`, ou `capteur_defaillant` si au moins 3 lectures du message sont invalides | l'arrosage est interdit (6.2) |
| `MISSION_NON_CONFIRMEE` | application | règle de la section 6.6 | `perte_communication` | la mission passe à `non_confirmee` |
| `MESSAGE_CONFLIT` | application | même `message_id`, contenu différent | *(aucun)* | seule la réponse 409 est renvoyée |

```json
{"message_id": "7a30c5e19b4d2f68", "num_sequence": 15, "type": "incident",
 "horodatage": "2026-11-03T10:04:02Z", "uptime_ms": 500300,
 "mission_id": 12, "code": "FILE_PLEINE", "gravite": "avertissement",
 "description": "File pleine pendant la coupure", "nb_perdus": 12}
```

### 4.8 Réponse de l'application

Réponse à un message accepté (200) :

```json
{"statut": "ok", "message_id": "c7d81a4f02e9b365",
 "recommandation_arrosage": "arroser"}
```

- Pour un doublon (même `message_id`, même contenu), l'application renvoie la même réponse que la première fois, sans rien enregistrer.
- `recommandation_arrosage` n'est présent que pour une `mesure`. Valeurs : `arroser`, `ne_pas_arroser`, `interdite`.

Réponse à une erreur (4xx ou 5xx) :

```json
{"statut": "erreur", "code": "MESSAGE_CONFLIT",
 "detail": "message_id déjà reçu avec un contenu différent"}
```

### 4.9 Où chaque champ est enregistré

| Champ du message | Table et colonne du modèle de données |
| --- | --- |
| `message_id` | `message.message_id` (clé primaire) |
| `num_sequence` | `message.num_sequence` |
| `type` | `message.type_message` |
| `mission_id` | `message.mission_id` |
| message complet | `message.contenu` (JSON ; sert à comparer un doublon) |
| heure de réception | `message.date_heure` |
| `etape` | sert à retrouver l'étape (`etape.numero_ordre` dans la mission) |
| `numero_point`, `numero_lecture` | `mesure.numero_point`, `mesure.numero_lecture` |
| `humidite_pct` | `mesure.valeur_humidite` |
| `valeur_brute` | `mesure.valeur_brute` |
| `valide` | `mesure.statut` (`valide` ou `invalide`) |
| `horodatage` | `mesure.date_heure_mesure` (heure de réception si `null`) |

## 5. API HTTP

### 5.1 Authentification (token en en-tête)

Chaque requête du robot porte l'en-tête `Authorization: Token <jeton>`. Le jeton est créé une fois par l'administrateur, stocké dans la configuration de l'ESP32 (`config.py`, ignoré par Git), et jamais placé dans l'URL. Sans jeton ou avec un jeton faux, l'application répond **401** et n'enregistre rien. Le corps de cette réponse est celui de DRF (`{"detail": "..."}`), pas celui du protocole : le robot ne lit que le code 401.

### 5.2 Tableau des endpoints

Adresse de base : `http://<adresse-du-serveur>:8000/api/v1`. **Les adresses du robot n'ont pas de slash final.**

| Méthode et chemin | Rôle | Réponses |
| --- | --- | --- |
| `GET /api/v1/robot/mission` | le robot récupère la mission en attente (toutes les 3 s) | 200, 204, 401 |
| `POST /api/v1/robot/messages` | le robot envoie un message de n'importe quel type | 200, 400, 401, 409, 422, 5xx |
| `POST /api/v1/robot/etat` | le robot signale son état (message `changement_etat`) | 200, 400, 401, 409, 422, 5xx |
| `POST /api/v1/robot/messages/sync` | le robot renvoie sa file après une coupure (tous types) | 200, 400, 401, 5xx |

### 5.3 Récupérer la mission (GET)

- 200 avec le JSON de la section 4.2 s'il y a une mission à exécuter ; 204 sans corps sinon.
- L'application renvoie la mission `planifiee` la plus ancienne qui n'a pas encore de message `mission_recue`. Une réponse perdue ne fait donc jamais perdre la mission.
- Dès que `mission_recue` est enregistré, le GET renvoie 204.
- Le délai maximal d'attente de la réponse est de 5 s ; au-delà le robot considère l'appel comme échoué.

### 5.4 Envoyer un message (POST)

Corps : un message de la section 4 (type `mission_recue`, `etape_atteinte`, `mesure`, `changement_etat` ou `incident`). Réponse 200 de la section 4.8 si le message est enregistré ou si c'est un doublon identique. Un type inconnu, y compris `mission`, donne 400 `TYPE_INCONNU`.

Signaler l'état. `POST /api/v1/robot/etat` accepte uniquement le type `changement_etat` (section 4.6) ; tout autre type reçoit 422 `TYPE_NON_ACCEPTE`. Le traitement est identique à celui de `POST /robot/messages` : même contrôle du `message_id`, mêmes réponses et mêmes codes d'erreur (5.6). Cet endpoint correspond au topic MQTT `roboagri/etat` (8.4). La file de renvoi (7.2) peut contenir des `changement_etat` : ils partent alors par l'endpoint de sync.

### 5.5 Renvoi groupé (sync)

Après une coupure, le robot envoie sa file en un seul appel :

```json
{"messages": [ {"message_id": "...", "num_sequence": 4, ...},
               {"message_id": "...", "num_sequence": 5, ...} ]}
```

- 1 à 20 messages par appel, classés par `num_sequence` croissant. Une liste vide, absente ou de plus de 20 messages donne 400 `SYNC_INVALIDE`.
- L'application traite les messages dans cet ordre, un par un, avec les mêmes règles que le POST simple.
- Réponse 200 avec un résultat par message ; une erreur sur l'un n'empêche pas les suivants.

```json
{"resultats": [
  {"message_id": "...", "statut": "ok"},
  {"message_id": "...", "statut": "erreur", "code": "MESSAGE_CONFLIT"}
]}
```

### 5.6 Codes d'erreur et réaction du robot

| Code HTTP | Cause | Réaction du robot |
| --- | --- | --- |
| 200 | message enregistré ou doublon identique | retire le message de la file |
| 204 | pas de mission (GET) | continue le polling |
| 400 | JSON invalide ou champ obligatoire manquant | retire le message, le note dans son journal local, ne le renvoie pas |
| 401 | jeton absent ou invalide | garde la file, arrête les envois, réessaie toutes les 30 s |
| 409 | même `message_id`, contenu différent | retire le message, ne le renvoie pas (l'application n'a rien enregistré) |
| 422 | valeur incohérente (humidité hors de 0 à 100, mission ou étape inconnue, type non accepté par l'endpoint) | retire le message, le note dans son journal local |
| 5xx, délai dépassé, réseau coupé | application ou réseau indisponible | garde le message, réessaie après 3 s, 6 s, 12 s, puis toutes les 30 s |

Codes du champ `code` dans le corps de la réponse :

| HTTP | `code` | Cause |
| --- | --- | --- |
| 400 | `JSON_INVALIDE` | le corps n'est pas un objet JSON |
| 400 | `CHAMP_MANQUANT` | `message_id`, `num_sequence`, `type` ou `mission_id` absent |
| 400 | `MESSAGE_ID_INVALIDE` | pas 16 caractères hexadécimaux en minuscules |
| 400 | `TYPE_INCONNU` | type absent de la liste de 3.3 |
| 400 | `SEQUENCE_INVALIDE` | `num_sequence` ni entier ni `null` |
| 400 | `SYNC_INVALIDE` | liste `messages` absente, vide ou de plus de 20 éléments |
| 409 | `MESSAGE_CONFLIT` | même `message_id`, contenu différent |
| 422 | `MISSION_INCONNUE` | `mission_id` n'existe pas |
| 422 | `ETAPE_INCONNUE` | `etape` n'existe pas dans cette mission |
| 422 | `ZONE_INCOHERENTE` | `zone_id` ne correspond pas à l'étape |
| 422 | `LECTURES_INVALIDES` | `lectures` absent, hors de 1 à 9 éléments, point ou lecture hors de 1 à 3, ou paire en double |
| 422 | `HUMIDITE_INVALIDE` | `humidite_pct` d'une lecture valide hors de 0 à 100 |
| 422 | `TYPE_NON_ACCEPTE` | type autre que `changement_etat` envoyé à `/robot/etat` |

## 6. Comportements exigés par le sujet

### 6.1 Envoi d'une mission

1. L'utilisateur crée la mission dans l'application : statut `planifiee`.
2. Au prochain polling (3 s au plus), le robot appelle `GET /api/v1/robot/mission` et reçoit la mission.
3. Le robot vérifie la mission, puis envoie `mission_recue` avant de démarrer. Tant que ce message n'est pas enregistré, le GET renvoie la même mission.
4. Le robot démarre ; au premier `etape_atteinte`, la mission passe à `en_cours`.

### 6.2 Réception des mesures et changements d'état

- L'application contrôle le jeton, la validité du JSON, puis le `message_id` (6.3), avant d'enregistrer.
- Un message `etape_atteinte` passe l'étape à `en_cours`.
- Un message `mesure` enregistre le message et toutes ses lectures dans une seule transaction, puis passe l'étape à `terminee`. La réponse contient `recommandation_arrosage`.
- **Recommandation d'arrosage.** La règle de décision exacte est décrite dans le document d'analyse. Aujourd'hui, l'application applique ceci : si au moins une lecture est invalide, ou si aucune lecture n'est valide, la réponse est `interdite` ; sinon la moyenne des lectures est comparée au seuil minimum de la zone (`arroser` si elle est inférieure, `ne_pas_arroser` sinon).
- Une lecture avec `valide: false` est enregistrée avec le statut `invalide` et sans humidité, l'application crée un incident (`mesure_invalide`, ou `capteur_defaillant` si au moins 3 lectures du message sont invalides) et répond `interdite`. Aucune recommandation d'arrosage n'est produite.
- Un `incident` du robot est enregistré selon la table de 4.7.
- Un `changement_etat` est enregistré ; avec `mission_terminee: true`, la mission passe à `terminee`.
- Le trou de `num_sequence` (86 puis 88) est noté par l'application sans bloquer le traitement : le 87 est peut-être simplement en retard.

### 6.3 Messages répétés

| Cas | Réponse | Effet |
| --- | --- | --- |
| `message_id` déjà reçu, contenu identique | 200, même réponse que la première fois | rien n'est enregistré |
| `message_id` déjà reçu, contenu différent | 409 `MESSAGE_CONFLIT` | rien n'est enregistré, le message d'origine reste inchangé, aucun incident |

« Contenu identique » signifie que tous les champs du message sont identiques, `uptime_ms` compris.

### 6.4 Interruption de communication

Si un envoi échoue (réseau coupé, délai de 5 s dépassé, 5xx), le robot continue sa mission avec les informations déjà reçues. Il place chaque nouveau message dans sa file en RAM (7.1). Dès que le réseau revient, il renvoie la file par l'endpoint de sync, dans l'ordre de `num_sequence` (7.2). Si la file a débordé, il envoie ensuite un incident `FILE_PLEINE`.

### 6.5 Non-duplication

La non-duplication repose sur la clé primaire `message_id` de la table `message`. L'application vérifie le `message_id` et enregistre le message dans la même transaction. Si deux requêtes identiques arrivent en même temps, la clé primaire en laisse passer une seule ; l'autre est traitée comme un doublon. `num_sequence` n'intervient pas.

### 6.6 Missions non confirmées

Une mission `en_cours` passe à `non_confirmee` quand l'application ne reçoit **aucun message** depuis N cycles de polling (N = 10, soit 30 s, configurable). L'application enregistre alors un incident `MISSION_NON_CONFIRMEE` (type `perte_communication` dans le modèle de données).

La version 1.0 ajoutait un plafond global (3 fois `duree_prevue_s`). Il n'est pas retenu : `duree_prevue_s` n'existe pas dans le modèle de données. Pour le moment, le silence est la seule règle.

**État de l'implémentation** : cette détection n'est pas encore écrite côté application. En attendant, l'utilisateur peut interrompre manuellement une mission bloquée.

## 7. Côté ESP32

### 7.1 File de messages et taille maximale

Le robot garde les messages non confirmés dans une file en RAM, limitée à 100 messages. Un message y reste jusqu'à la réponse 200 (ou jusqu'à un 400, 409 ou 422 qui le rejette définitivement, voir 5.6).

Quand la file est pleine, le message le plus ancien est écrasé et le robot compte les messages perdus. Au retour du réseau, il envoie un incident `FILE_PLEINE` avec `nb_perdus`. Limite assumée : une file en RAM est perdue si le robot redémarre ; la file en flash est notée comme amélioration (section 10).

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

### 7.2 Renvoi dans l'ordre de num_sequence

1. Le robot n'envoie rien en direct tant que la file n'est pas vide : tout nouveau message est ajouté à la fin, pour garder l'ordre.
2. Il envoie la file par paquets de 20 messages au plus, de l'ancien au récent (`num_sequence` croissant), via `POST /api/v1/robot/messages/sync`.
3. Pour chaque résultat `ok`, ou erreur définitive (409, 422), le message sort de la file.
4. Au premier échec réseau, 5xx ou 401, il s'arrête, garde le reste et réessaie selon 5.6.
5. Quand la file est vide, il reprend les envois directs par `POST /api/v1/robot/messages`.

### 7.3 Sauvegarde du compteur en flash

`num_sequence` doit rester croissant même après un redémarrage, sans écrire en flash à chaque message (usure). Le compteur est tenu en RAM : c'est lui qui est incrémenté à chaque message. Il est ensuite copié dans un fichier en flash seulement tous les N messages (N = 10), ce qui réduit l'usure de la flash par rapport à une écriture à chaque message. Au démarrage, il lit la valeur sauvegardée et ajoute N : le compteur ne revient jamais en arrière, mais la séquence peut contenir des trous. Ce n'est pas grave, car les doublons sont gérés par `message_id`.

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

### 7.4 Détection d'un capteur invalide

Après **chaque lecture**, le robot compare `valeur_brute` à deux bornes de la configuration : en dessous de `BRUT_MIN_VALIDE` (capteur débranché ou court-circuité) ou au-dessus de `BRUT_MAX_VALIDE`, la lecture est invalide. Il l'ajoute alors au tableau `lectures` avec `valide: false` et `humidite_pct: null`, et il ne calcule aucun pourcentage pour elle. Les autres lectures de l'étape restent valides et sont envoyées dans le même message.

L'étalonnage (valeur brute à sec, valeur brute dans l'eau, les deux bornes ci-dessus) vit dans la configuration du robot. Ces valeurs de référence sont à documenter dans le dossier de tests.

### 7.5 Construire un message mesure

1. À l'arrivée sur une étape, le robot envoie `etape_atteinte` (`etape` et `zone_id` reçus dans la mission).
2. Il prend 3 points de collecte, avec 3 lectures par point, et construit pour chaque lecture un élément de `lectures` (`numero_point`, `numero_lecture`, `humidite_pct`, `valeur_brute`, `valide`).
3. Il ajoute `etape` et `zone_id`, tire un `message_id`, prend le `num_sequence` suivant, et envoie un **seul** message `mesure` pour l'étape.
4. Si l'envoi échoue, le message entier va dans la file (7.1) ; il n'est jamais découpé en lectures séparées.
5. À la fin de la dernière étape, il envoie `changement_etat` vers `repos` avec `mission_terminee: true`.

## 8. Évolution vers MQTT

En phase 2, le polling HTTP est remplacé par un broker MQTT (Mosquitto). Les corps JSON de la section 4 ne changent pas ; seuls le transport et l'accusé de réception changent.

### 8.1 Topics et QoS

| Topic | Sens | Messages | QoS |
| --- | --- | --- | --- |
| `roboagri/mission` | application vers robot | mission (message conservé par le broker) | 1 |
| `roboagri/etape` | robot vers application | `mission_recue`, `etape_atteinte` | 1 |
| `roboagri/mesure` | robot vers application | `mesure` (lectures d'une étape) | 1 |
| `roboagri/etat` | robot vers application | `changement_etat` | 1 |
| `roboagri/incident` | robot vers application | `incident` | 1 |
| `roboagri/ack` | application vers robot | accusé de réception d'un message | 1 |

Le QoS 1 garantit au moins une livraison, donc un message peut arriver deux fois : `message_id` reste la clé anti-doublon, comme en HTTP. Les topics ne contiennent pas d'identifiant de robot (2.2).

### 8.2 Accusé de réception (roboagri/ack)

En HTTP, la réponse 200 sert d'accusé. En MQTT, l'application publie sur `roboagri/ack` après chaque message traité :

```json
{"message_id": "c7d81a4f02e9b365", "statut": "ok", "recommandation_arrosage": "arroser"}
```

- Le robot ne retire un message de sa file qu'après l'accusé correspondant. Sans accusé après 5 s, il republie le même message, avec le même `message_id`.
- Pour une erreur, l'accusé porte `"statut": "erreur"` et un code, avec les mêmes règles de réaction que la section 5.6.

### 8.3 Last Will

À la connexion, le robot déclare un Last Will : si le broker perd le robot sans déconnexion propre, il publie lui-même ce message sur `roboagri/etat` (QoS 1, conservé) :

```json
{"message_id": "e19d4a7c60b3f258", "num_sequence": null, "type": "changement_etat",
 "horodatage": null, "uptime_ms": null, "etat_nouveau": "hors_ligne"}
```

C'est le seul cas où `num_sequence` et `horodatage` valent `null` : le message est préparé à la connexion, avant la panne. Le `message_id` est tiré à chaque connexion. À la connexion suivante, le robot publie `repos` sur le même topic, ce qui remplace le message conservé. Le Last Will alimente la règle du silence de la section 6.6.

**Point à trancher avant d'implémenter MQTT** : dans le modèle de données, `message.mission_id` est obligatoire, alors que le Last Will est préparé avant toute mission. Deux solutions : rattacher ce message à la mission en cours, ou rendre le lien facultatif pour ce type de message.

### 8.4 Tableau de correspondance HTTP / MQTT

| Fonction | HTTP (phase 1) | MQTT (phase 2) |
| --- | --- | --- |
| Récupérer la mission | `GET /api/v1/robot/mission` toutes les 3 s | abonnement à `roboagri/mission` |
| Envoyer un message | `POST /api/v1/robot/messages` | publication sur le topic du type |
| Signaler l'état | `POST /api/v1/robot/etat` | publication sur `roboagri/etat` |
| Accusé de réception | réponse 200 | message sur `roboagri/ack` |
| Renvoi après coupure | `POST /api/v1/robot/messages/sync` | republication de la file, dans l'ordre |
| Authentification | en-tête `Authorization: Token` | identifiant et mot de passe du broker |
| Détection de robot absent | silence de 30 s (6.6) | Last Will, plus silence (6.6) |
| Doublons | `message_id` unique | `message_id` unique (inchangé) |

## 9. Scénarios complets (requêtes et réponses)

Dans tous les exemples, chaque requête porte `Authorization: Token <jeton>` et `Content-Type: application/json`, sauf le 9.6. Les champs `horodatage` et `uptime_ms` sont abrégés par … pour la lisibilité ; ils sont obligatoires en vrai. Le tableau `lectures` est abrégé de la même façon (un vrai message contient jusqu'à 9 lectures).

### 9.1 Cas nominal

```http
GET /api/v1/robot/mission
-> 200  {"type":"mission","mission_id":12,"cree_le":"2026-11-03T10:00:00Z",
          "etapes":[{"etape":1,"zone_id":1},{"etape":2,"zone_id":2}]}

POST /api/v1/robot/messages
{"message_id":"a41c09e2d7f3b856","num_sequence":1,"type":"mission_recue","mission_id":12,…}
-> 200  {"statut":"ok","message_id":"a41c09e2d7f3b856"}      # mission reçue : le GET ne la renvoie plus

GET /api/v1/robot/mission
-> 204                                                       # plus de répétition

POST /api/v1/robot/messages
{"message_id":"5be2f0137a9c4d68","num_sequence":2,"type":"etape_atteinte","mission_id":12,"etape":1,"zone_id":1,…}
-> 200  {"statut":"ok","message_id":"5be2f0137a9c4d68"}      # mission : en_cours, étape 1 : en_cours

POST /api/v1/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure","mission_id":12,"etape":1,"zone_id":1,
 "lectures":[{"numero_point":1,"numero_lecture":1,"humidite_pct":34.5,"valeur_brute":2310,"valide":true}, …],…}
-> 200  {"statut":"ok","message_id":"c7d81a4f02e9b365","recommandation_arrosage":"arroser"}   # étape 1 : terminee

... (étape 2 : etape_atteinte, puis mesure de la zone 2) ...

POST /api/v1/robot/etat
{"message_id":"0e6b93d1c5a7f284","num_sequence":9,"type":"changement_etat","mission_id":12,
 "etat_precedent":"en_mesure","etat_nouveau":"repos","mission_terminee":true,…}
-> 200  {"statut":"ok","message_id":"0e6b93d1c5a7f284"}      # mission : terminee
```

### 9.2 Doublon (même contenu)

La réponse 200 du message `c7d81a4f02e9b365` s'est perdue ; le robot le renvoie tel quel.

```http
POST /api/v1/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure", ... (identique) ...}
-> 200  {"statut":"ok","message_id":"c7d81a4f02e9b365","recommandation_arrosage":"arroser"}
```

Résultat : réponse identique à la première, un seul message et un seul jeu de lectures en base.

### 9.3 Doublon avec contenu différent (409)

```http
POST /api/v1/robot/messages
{"message_id":"c7d81a4f02e9b365","num_sequence":3,"type":"mesure","mission_id":12,"etape":1,"zone_id":1,
 "lectures":[{"numero_point":1,"numero_lecture":1,"humidite_pct":12.0,"valeur_brute":3400,"valide":true}, …],…}
-> 409  {"statut":"erreur","code":"MESSAGE_CONFLIT",
         "detail":"message_id déjà reçu avec un contenu différent"}
```

Résultat : les lectures d'origine restent inchangées, rien n'est enregistré (aucun incident : ce cas n'a pas de type d'incident dans le modèle de données), le robot retire le message de sa file sans le renvoyer.

### 9.4 Coupure puis renvoi

1. Le Wi-Fi tombe après le message 3. Les messages 4, 5 et 6 (un `etape_atteinte`, une `mesure` et un autre `etape_atteinte`) sont mis en file ; les envois directs échouent après 5 s (réessais à 3 s, 6 s, 12 s, puis 30 s).
2. Le Wi-Fi revient. Le robot envoie la file d'un seul appel, dans l'ordre :

```http
POST /api/v1/robot/messages/sync
{"messages":[ {"message_id":"…","num_sequence":4,…},
               {"message_id":"…","num_sequence":5,…},
               {"message_id":"…","num_sequence":6,…} ]}
-> 200  {"resultats":[{"message_id":"…","statut":"ok"},
                     {"message_id":"…","statut":"ok"},
                     {"message_id":"…","statut":"ok"}]}
```

3. La file est vide : le robot reprend les envois directs. Les horodatages d'origine sont conservés (3.1).

Si la file avait dépassé 100 messages, le robot enverrait ensuite un incident `FILE_PLEINE` avec `nb_perdus`.

### 9.5 Mission non confirmée

1. La mission 12 est `en_cours` ; le dernier message reçu date de 10:04:00.
2. À 10:04:30 (10 cycles de 3 s sans message), l'application passe la mission à `non_confirmee` et enregistre l'incident `MISSION_NON_CONFIRMEE` (type `perte_communication`).
3. La mission reste `non_confirmee` et l'utilisateur décide de la relancer.

Cette détection est à implémenter côté application (6.6).

### 9.6 Token invalide

```http
POST /api/v1/robot/messages
Authorization: Token mauvais_jeton
{"message_id":"…","num_sequence":10,"type":"mesure",…}
-> 401  {"detail":"Jeton non valide."}
```

Résultat : rien n'est enregistré. Le robot ne lit que le code 401 : il garde le message en file, arrête ses envois et réessaie toutes les 30 s ; une fois le jeton corrigé dans sa configuration, la file repart dans l'ordre. Le texte exact de `detail` dépend de DRF et peut changer.

### 9.7 Capteur invalide

Le capteur est débranché pendant la visite de l'étape 2 : trois lectures du point 2 sont hors des bornes valides (7.4).

```http
POST /api/v1/robot/messages
{"message_id":"b82e51f7d0a3c496","num_sequence":11,"type":"mesure","mission_id":12,"etape":2,"zone_id":2,
 "lectures":[{"numero_point":1,"numero_lecture":1,"humidite_pct":33.0,"valeur_brute":2330,"valide":true},
             {"numero_point":2,"numero_lecture":1,"humidite_pct":null,"valeur_brute":0,"valide":false},
             {"numero_point":2,"numero_lecture":2,"humidite_pct":null,"valeur_brute":0,"valide":false},
             {"numero_point":2,"numero_lecture":3,"humidite_pct":null,"valeur_brute":0,"valide":false}, …],…}
-> 200  {"statut":"ok","message_id":"b82e51f7d0a3c496","recommandation_arrosage":"interdite"}
```

Résultat : toutes les lectures sont enregistrées (les invalides avec le statut `invalide` et leur valeur brute pour le diagnostic), l'application crée un incident `capteur_defaillant` (au moins 3 lectures invalides), et aucun arrosage n'est recommandé pour cette zone. Avec une ou deux lectures invalides seulement, l'incident serait `mesure_invalide`.

## 10. Limites et points ouverts

- File en RAM : les messages en attente sont perdus si le robot redémarre ou perd le courant pendant une coupure. Amélioration prévue si le temps le permet : file persistée en flash (survit au redémarrage, mais code plus lourd et usure de la flash).
- File limitée à 100 messages : au-delà, les plus anciens sont perdus ; seul l'incident `FILE_PLEINE` en garde la trace.
- Trous de `num_sequence` : l'application les détecte et les note, mais ne redemande pas le message manquant. Les sauts de N au redémarrage (7.3) en créent volontairement.
- Heure du robot : sans NTP, `horodatage` vaut `null` et l'application utilise l'heure de réception, donc approximative pour un message renvoyé.
- Une seule lecture invalide suffit à interdire la recommandation d'arrosage pour l'étape (choix de prudence, à valider avec le binôme chargé de la règle de décision).
- Lectures manquantes : une lecture non faite est omise du message ; le statut `manquante` du modèle de données n'est pas encore utilisé.
- Incidents : le modèle de données n'a que quatre types et pas de gravité. `MESSAGE_CONFLIT` et `NTP_ECHEC` ne sont pas enregistrés, et `gravite` n'est conservée que dans le contenu du message.
- Détection des missions non confirmées : règle définie (6.6), non implémentée.
- Last Will : le lien obligatoire du message avec une mission est à résoudre avant d'implémenter MQTT (8.3).
- Sécurité : le jeton est statique et le trafic HTTP du labo n'est pas chiffré. Acceptable pour le projet ; à remplacer par HTTPS et un jeton renouvelable en production.
- Un seul robot : en ajouter un second demande un identifiant de robot dans les messages, des topics par robot et une unicité de `message_id` par robot.

## 11. Historique des versions

| Version | Changement |
| --- | --- |
| 1.0 | Première rédaction : un message `mesure` par zone, sept statuts de mission, codes d'incident avec gravité, plafond de durée pour les missions non confirmées |
| 1.1 | Alignement sur le modèle de données (MPD) et sur le code du backend : message `mesure` par étape avec `lectures`, statuts de mission du MPD, correspondance des incidents, `mission_id` champ commun, suppression de `duree_prevue_s` et du plafond, adresses en `/api/v1/robot/` sans slash final, codes d'erreur détaillés, tableau des champs enregistrés (4.9) et construction d'un message côté ESP32 (7.5) |