# ROBOAGRI-KIN : Manuel de firmware ESP32

Ce manuel explique comment installer MicroPython sur l'ESP32, quel outil utiliser pour développer, comment téléverser le code, comment le dossier `firmware/` est organisé et comment le robot gère sa connexion Wi-Fi.

---

## 1. Flasher MicroPython sur l'ESP32

### 1.1 Matériel utilisé

- Carte ESP32 (module générique, variante ESP32 / WROOM)
- Câble micro-USB qui transmet les données (un câble de charge seule ne fonctionne pas)

### 1.2 Le pont USB-série CP2102 et son pilote

L'ESP32 ne sait pas parler USB directement. Sur la carte, la petite puce CP2102, située près du port micro-USB, sert d'interprète : elle traduit l'USB du PC en signaux série que l'ESP32 comprend.

Le pilote CP210x est le logiciel qui permet à Windows de reconnaître cette puce et de créer un port COM virtuel. Sans pilote, aucun port n'apparaît et Thonny ne peut pas parler à la carte.

Comment l'utiliser :

1. Brancher l'ESP32 au PC avec un câble micro-USB de données.
2. Ouvrir le Gestionnaire de périphériques, rubrique Ports (COM et LPT), et repérer la ligne « Silicon Labs CP210x USB to UART Bridge (COMx) ». Le numéro x est le port de la carte (COM4 dans notre cas).
3. Dans Thonny, choisir ce port : en bas à droite de la fenêtre, ou dans la fenêtre de flashage sous le nom « CP2102 USB to UART Bridge Controller @ COM4 ».
4. Ce même port sert ensuite à tout : flasher le firmware, afficher la console (REPL) et téléverser les fichiers.

### 1.3 Procédure de flashage

1. Brancher l'ESP32 au PC avec le câble USB.
2. Vérifier dans le Gestionnaire de périphériques que la ligne « Silicon Labs CP210x USB to UART Bridge (COMx) » apparaît.
3. Ouvrir Thonny, puis aller dans Outils > Options > Interpréteur.
4. Choisir MicroPython (ESP32) comme interpréteur.
5. Cliquer sur Install or update MicroPython (esptool).
6. Renseigner la fenêtre :
   - Target port : CP2102 USB to UART Bridge Controller @ COM4
   - MicroPython family : ESP32
   - Variant : Espressif • ESP32 / WROOM
   - Version : dernière version stable
   - Cocher Erase flash before installing
7. Cliquer sur Install.
8. Attendre la fin de l'installation (environ 1 à 3 minutes) et le message « Done ».

### 1.4 Vérification

Au démarrage, la console Thonny affiche :

```
MicroPython v1.29.0 on 2026-08-24; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```

Le symbole `>>>` indique que MicroPython fonctionne et que la carte attend des commandes. Les lignes précédentes (`rst:0x1 (POWERON_RESET)`, `boot:0x13`, `load:...`) sont le message normal de démarrage de la puce, pas des erreurs.

### 1.5 Reprendre le travail après un débranchement

Le firmware est stocké dans la mémoire flash de l'ESP32 : il reste installé quand la carte est débranchée. Il n'est donc pas nécessaire de refaire le flashage. Il suffit de rebrancher la carte, d'ouvrir Thonny et de vérifier le port dans l'interpréteur (en bas à droite).

### 1.6 Si le flashage échoue avec « Failed to connect »

Ce problème n'est pas apparu pendant notre installation, mais il peut arriver sur d'autres cartes ou d'autres PC.

Pour recevoir un nouveau firmware, l'ESP32 doit être en mode téléchargement, le mode où sa mémoire peut être réécrite. D'habitude, Thonny l'active automatiquement : il envoie des signaux à travers le CP2102 qui font redémarrer la puce dans ce mode. Sur certaines cartes, ce mécanisme automatique ne fonctionne pas bien. La puce reste alors en mode normal, ne répond pas à Thonny, et le flashage s'arrête avec « Failed to connect ».

Solution :

1. Lancer l'installation dans Thonny.
2. Dès que « Connecting... » s'affiche, maintenir le bouton BOOT de la carte appuyé.
3. Garder BOOT appuyé jusqu'au début de l'écriture, puis le relâcher.

### 1.7 Autres problèmes fréquents

| Problème | Cause | Solution |
|---|---|---|
| Port COM absent de la liste | Câble de charge seule ou pilote manquant | Changer de câble, installer le pilote CP210x |

---

## 2. Outil de développement et téléversement du code

### 2.1 Outil retenu : Thonny

Thonny est un environnement de développement Python gratuit et open source, qui fonctionne sous Windows. Il est utilisé avec le firmware MicroPython v1.29.0 installé sur l'ESP32.

Pourquoi Thonny :

- Il gère MicroPython directement : flashage du firmware, console interactive (REPL) et gestion des fichiers de la carte dans un seul outil.
- Il est simple à prendre en main, ce qui convient à tous les membres du groupe, y compris les débutants.
- Il est gratuit.
- Le code est écrit en Python, le même langage que l'application du projet.
- La console permet de tester une instruction à la fois, ce qui est utile pour valider les capteurs (HC-SR04, humidité du sol).

### 2.2 Téléverser le code sur l'ESP32

1. Dans Thonny, ouvrir le panneau des fichiers : Affichage > Fichiers.
2. Dans la section « Ce PC », aller dans le dossier `firmware/` du projet.
3. Faire un clic droit sur un fichier, puis choisir Téléverser vers /. Répéter pour chaque fichier.
4. Appuyer sur le bouton EN/RST de la carte pour relancer le programme.

---

## 3. Structure du dossier firmware

```
atlantis-roboAgri/
├── .gitignore
└── firmware/
    ├── main.py
    ├── config.py
    ├── reseau.py
    ├── humidite.py
    ├── moteurs.py
    ├── obstacle.py
    ├── parcours.py
    ├── batterie.py
    ├── secrets.py          (non suivi par Git)
    ├── secrets.example.py  (modèle, suivi par Git)
    └── test_ping.py
```

Le fichier `.gitignore` se trouve à la racine du projet, en dehors du dossier `firmware/`.

**Règle d'organisation : un module par fonction.** Chaque fichier a une seule responsabilité, ce qui permet de tester et de corriger une partie sans toucher aux autres.

### 3.1 Rôle de chaque module

- **`main.py`** : chef d'orchestre. Il démarre au branchement, lance la connexion Wi-Fi, puis tourne en boucle. À chaque tour, il demande une mission au serveur, appelle les autres modules et envoie les résultats.
- **`config.py`** : toutes les constantes au même endroit : broches, adresse du serveur, délais, seuils de batterie, bornes d'étalonnage. On change une valeur ici, sans fouiller le code. Il ne contient aucun mot de passe.
- **`reseau.py`** : gère le Wi-Fi. Il connecte la carte, vérifie que la connexion est toujours active et la rétablit après une coupure.
- **`humidite.py`** : lit le capteur d'humidité du sol. Il convertit la valeur brute en pourcentage et signale si la lecture est invalide (capteur débranché par exemple).
- **`moteurs.py`** : contrôle les moteurs du robot : avancer, reculer, tourner à gauche, tourner à droite, s'arrêter.
- **`obstacle.py`** : détecte les obstacles avec le capteur de distance et indique au robot quand il doit s'arrêter ou contourner.
- **`parcours.py`** : simule un parcours que le robot doit suivre. Il détecte les obstacles et fait prendre un autre chemin au robot, jusqu'à ce que la voie soit libre.
- **`batterie.py`** : mesure la tension de la batterie, la convertit en pourcentage approximatif et signale quand le niveau est faible.
- **`secrets.py`** : contient les informations privées : nom et mot de passe du réseau Wi-Fi, adresse du serveur, clé et nom du robot. Il n'est jamais publié sur GitHub.
- **`secrets.example.py`** : modèle vide de `secrets.py`, publié sur GitHub pour montrer ce qu'il faut remplir.
- **`test_ping.py`** : test de communication. L'ESP32 contacte une route de test du serveur (`/api/ping/`) pour vérifier que la liaison fonctionne.

---

## 4. Connexion Wi-Fi avec reconnexion automatique

### 4.1 Pourquoi le Wi-Fi

Le robot travaille dans un champ, loin du laptop. Le Wi-Fi est son seul lien avec l'application : il y demande ses missions et il y envoie ses mesures. Un robot qui perd le Wi-Fi sans pouvoir le retrouver est inutilisable, d'où la reconnexion automatique.

### 4.2 Où sont les identifiants et pourquoi

Le nom du réseau (SSID) et le mot de passe sont dans un fichier à part, `secrets.py`, et non dans `config.py`. La raison est simple : `config.py` est partagé avec toute l'équipe sur GitHub, alors que le mot de passe doit rester privé.

- Le `.gitignore` contient la ligne `**/secrets.py`. Git ignore donc ce fichier et il n'est jamais publié.
- `secrets.example.py` est un modèle avec des champs vides, qui lui est publié. Il montre à chaque membre de l'équipe ce qu'il faut remplir.

Le fichier `secrets.py` contient cinq informations, chacune sous un nom fixe que les autres modules utilisent :

- `WIFI_SSID` : le nom du réseau Wi-Fi, tel qu'on le voit dans la liste des réseaux d'un téléphone. Il doit s'agir d'un réseau en 2,4 GHz (voir 4.4).
- `WIFI_PASSWORD` : le mot de passe de ce réseau.
- `API_URL` : l'adresse du serveur de l'application. Elle se compose de `http://`, de l'adresse IP du PC qui fait tourner le serveur (les « x » du modèle sont à remplacer), et du port `:8000`. Elle est ici, et non dans `config.py`, parce qu'elle change selon le PC et le réseau utilisés.
- `ROBOT_API_TOKEN` : la clé secrète du robot. Il l'envoie au serveur à chaque requête pour prouver que c'est bien lui. C'est l'authentification par clé d'API décidée dans le protocole. Elle doit être identique à celle enregistrée côté serveur.
- `ROBOT_ID` : le nom du robot (par exemple « robot-01 »), qui l'identifie dans les messages envoyés au serveur.

Le mot de passe Wi-Fi et la clé du robot sont les deux valeurs vraiment sensibles : quiconque les connaît peut entrer sur le réseau ou se faire passer pour le robot.

Pour démarrer :

1. Copier `secrets.example.py` en `secrets.py`.
2. Remplir les cinq valeurs avec les vraies informations.
3. Téléverser `secrets.py` sur la carte comme les autres fichiers.

`reseau.py` lit ensuite `WIFI_SSID` et `WIFI_PASSWORD` en important `secrets.py`.

### 4.3 Logique de la reconnexion dans reseau.py

**Le problème à résoudre.** Le Wi-Fi n'est jamais parfaitement stable : le routeur peut redémarrer, le robot peut s'éloigner, un obstacle peut couper le signal. Si le programme ne tente la connexion qu'une fois au démarrage, la moindre coupure bloque le robot jusqu'à un redémarrage manuel.

**Le principe.** On ne suppose jamais que le Wi-Fi est connecté : on le vérifie et, s'il est coupé, on le rétablit. Cela se fait en deux temps.

**Temps 1 : établir la connexion**

1. **Activer le Wi-Fi de la carte en mode client.** L'ESP32 a deux modes : le mode client, où il se connecte à un réseau existant comme un téléphone se connecte à une box, et le mode point d'accès, où il crée son propre réseau. On utilise le mode client, sur un réseau en 2,4 GHz (voir 4.4).
2. **Vérifier si la carte est déjà connectée.** Si oui, on ne fait rien : cela évite de couper une connexion qui marche.
3. **Lancer la connexion** avec le nom et le mot de passe du réseau, lus dans `secrets.py`. Cette commande rend la main tout de suite : elle ne dit pas « connecté », elle dit seulement « la connexion est lancée ». Elle se fait en arrière-plan, et on vérifie ensuite si la carte est réellement connectée.
4. **Attendre la réponse, mais pas indéfiniment.** On regarde l'état toutes les demi-secondes pendant un délai maximum, `DELAI_CONNEXION_S` (15 secondes, défini dans `config.py`).
   - Pourquoi cette limite : si on écrit « attendre tant que la carte n'est pas connectée » sans limite, un mauvais mot de passe ou un routeur éteint ne passera jamais à « connecté ». La boucle d'attente ne se termine alors jamais, le programme n'avance plus et le robot reste bloqué. Avec la limite, on sort de l'attente au bout de 15 secondes, on constate l'échec et on décide quoi faire.
5. **Si la connexion réussit**, le routeur a donné au robot une adresse IP, qui est son identité sur le réseau. On l'affiche sur la console série (par exemple `Wi-Fi connecte, IP : 192.168.1.42`) : cela confirme que la connexion marche et sert au diagnostic. Puis on rend la main : la fonction de `reseau.py` se termine en indiquant « connecté », et `main.py` continue son travail (test de liaison, demande de mission, mesures).
6. **Si elle échoue**, on affiche l'échec sur la console, on attend `DELAI_RECONNEXION_S` (5 secondes, défini dans `config.py`), puis on recommence à l'étape 3. Cette pause laisse au routeur le temps de revenir et évite de multiplier les tentatives en rafale.

**Temps 2 : surveiller en permanence**

7. À chaque tour de la boucle de `main.py`, avant de contacter le serveur, on vérifie que la carte est encore connectée.
8. Si elle ne l'est plus, on affiche un avertissement sur la console et on repart de l'étape 3.

Les états du robot :

```
Déconnecté → tentative de connexion → Connecté
    ↑                                     │
    └──────────── coupure détectée ───────┘
```

**Résultat :** le robot ne plante jamais à cause du Wi-Fi. Il continue d'essayer, à intervalles réguliers, jusqu'au retour du réseau, et reprend son travail tout seul.

### 4.4 Le Wi-Fi 2,4 GHz : de quoi s'agit-il et que faire

**De quoi il s'agit.** Le Wi-Fi utilise des ondes radio réparties sur des « bandes » de fréquence, un peu comme les stations de radio ont chacune leur fréquence. Deux bandes sont courantes :

- la 2,4 GHz : portée plus longue, traverse mieux les murs, un peu moins rapide ;
- la 5 GHz : plus rapide, mais portée plus courte.

Beaucoup de box et de téléphones récents émettent sur les deux bandes.

**Pourquoi c'est important.** La puce Wi-Fi de l'ESP32 ne sait écouter que la 2,4 GHz. Un réseau qui émet uniquement en 5 GHz est invisible pour elle. Le piège est que la carte ne signale pas « mauvaise bande » : elle échoue simplement à se connecter, ce qui ressemble à un mauvais mot de passe.

**Que faire.**

1. Mettre dans `WIFI_SSID` le nom d'un réseau en 2,4 GHz. Quand une box propose deux réseaux (par exemple « NomBox » et « NomBox_5G »), prendre celui qui n'a pas la mention 5G.
2. Si la box regroupe les deux bandes sous un seul nom, la carte s'y connecte en général sans problème. Si elle n'y arrive pas, il faut séparer les deux bandes ou désactiver temporairement la 5 GHz dans les réglages de la box.
3. Avec le partage de connexion d'un téléphone, activer l'option qui impose la bande 2,4 GHz (selon le téléphone, elle s'appelle « bande 2,4 GHz » ou « maximiser la compatibilité »).
4. Si le nom et le mot de passe sont corrects mais que la connexion échoue toujours, la bande est le premier suspect.

---

## 5. Test de communication avec le serveur (/api/ping/)

### 5.1 À quoi sert ce test

Avant d'écrire la logique des missions et des capteurs, il faut être sûr que le robot peut joindre l'application. Le test `/api/ping/` vérifie toute la chaîne d'un seul coup :

```
ESP32 → Wi-Fi → réseau local → PC → application
```

S'il réussit, toute la chaîne fonctionne. S'il échoue, on sait que le problème est dans la communication et non dans les capteurs ou les moteurs. Ce test isole donc la panne.

### 5.2 Le principe

C'est une question simple suivie d'une réponse simple, comme dire « Allô ? » et entendre « Oui ». Le robot demande l'adresse `/api/ping/` et l'application répond « ok ». Rien n'est lu dans une base de données ni enregistré : c'est seulement un test de liaison.

Ce test ne demande pas les autres modules du firmware. Il lui faut seulement `config.py` (le délai d'attente), `secrets.py` (l'adresse du serveur), `reseau.py` (pour être connecté) et un serveur qui répond. Si la route de l'application n'est pas encore prête, un petit serveur de test lancé sur le PC suffit (voir 5.5).

### 5.3 Les choix et leurs raisons

| Choix | Décision | Pourquoi |
|---|---|---|
| Méthode HTTP | GET | On demande seulement une réponse, on n'envoie aucune donnée. |
| Adresse | `/api/ping/` | Une route dédiée, sans base de données ni mission : elle ne peut échouer que pour une raison de réseau. |
| Adresse du serveur | `API_URL` dans `secrets.py` | Elle change selon le PC et le réseau : on la modifie à un seul endroit, sans toucher au code partagé. |
| Réponse | JSON `{"status": "ok", "message": "pong"}` | Facile à lire pour l'ESP32 et pour un navigateur. C'est le format des futurs messages du robot. |
| Signe de réussite | Code HTTP 200 | Le code standard pour « tout s'est bien passé ». |
| Protocole | HTTP | Réseau local en développement. HTTPS demanderait des certificats, trop lourd pour l'ESP32 à ce stade. |
| Délai d'attente | `TIMEOUT_REQUETE_S` (5 s, dans `config.py`) | Si l'application ne répond pas, le robot abandonne au lieu de rester bloqué. |

### 5.4 La logique du test, étape par étape

1. **Vérifier que le Wi-Fi est connecté.** Sans Wi-Fi, la requête ne peut pas partir. On le vérifie d'abord pour afficher un message clair (« Wi-Fi non connecté ») au lieu d'une erreur réseau difficile à comprendre.
2. **Construire l'adresse complète.** On prend `API_URL` de `secrets.py` et on y ajoute `/api/ping/`. L'adresse du serveur est comme l'adresse d'un immeuble, et `/api/ping/` est le numéro de la porte à laquelle on frappe.
3. **Envoyer la question (requête GET) avec un délai maximum.** On attend la réponse au plus `TIMEOUT_REQUETE_S` secondes. Sans cette limite, un serveur éteint ferait attendre le robot indéfiniment, comme pour le Wi-Fi.
4. **Afficher ce qui est reçu.** Le code et le contenu de la réponse s'affichent sur la console. C'est ce qui permet de savoir si le test a marché et, sinon, pourquoi.
5. **Décider du résultat.** Un code 200 veut dire que le test est réussi. Tout autre code est un échec. Si aucune réponse n'arrive (serveur injoignable, délai dépassé), l'erreur est attrapée, affichée, et le test conclut à l'échec sans faire planter le robot.
6. **Fermer la réponse.** Cela libère la mémoire. L'ESP32 en a très peu : des réponses jamais fermées finissent par la saturer après quelques tests. Cette étape est faite même quand il y a eu une erreur.

Selon la version de MicroPython, la bibliothèque qui envoie les requêtes s'appelle `requests` ou `urequests` : le module essaie la première, puis la seconde.

### 5.5 Le serveur de test

Le vrai serveur de l'application n'est pas encore disponible pour ce test. On utilise donc `serveur_test.py`, un mini-serveur qui tourne sur le PC (et non sur la carte). Il répond « ok » à l'adresse `/api/ping/` et « introuvable » à toute autre adresse. Il affiche aussi chaque requête reçue, ce qui permet de voir que le robot a bien contacté le PC.

Il écoute toutes les connexions du réseau, pas seulement celles du PC lui-même : sans cela, l'ESP32 ne pourrait pas l'atteindre. Quand la vraie route sera prête dans l'application, il suffira de changer `API_URL` dans `secrets.py`.

### 5.6 Procédure du test

1. Mettre le PC et l'ESP32 sur le même réseau Wi-Fi (en 2,4 GHz).
2. Lancer `serveur_test.py` sur le PC. Au premier lancement, Windows demande d'autoriser le programme à travers le pare-feu : accepter pour les réseaux privés.
3. Trouver l'adresse IP du PC : dans l'invite de commandes Windows, lancer la commande `ipconfig` et lire l'« Adresse IPv4 » de la carte Wi-Fi.
4. Vérifier avec le navigateur d'un téléphone connecté au même Wi-Fi : ouvrir l'adresse du PC suivie de `:8000/api/ping/`. Si la réponse s'affiche, le serveur est prêt.
5. Écrire cette adresse dans `API_URL` de `secrets.py`, avec `http://` au début et `:8000` à la fin, sans « / » final.
6. Téléverser sur l'ESP32 les fichiers `config.py`, `secrets.py`, `reseau.py` et `test_ping.py`.
7. Dans la console de Thonny (interpréteur MicroPython de l'ESP32), appeler la fonction `connecter` du module `reseau`, puis la fonction `tester_ping` du module `test_ping`.

Avec le vrai serveur de l'application, il faut en plus autoriser l'adresse IP du PC dans ses paramètres, sinon il refuse la requête avec une erreur 400.

### 5.7 Lire le résultat

En cas de succès, la console affiche :

```
[TEST] Envoi de la requete vers http://192.168.1.10:8000/api/ping/
[TEST] Code HTTP : 200
[TEST] Reponse : {"status": "ok", "message": "pong"}
```

En cas d'échec :

| Message | Signification | Action |
|---|---|---|
| Wi-Fi non connecte | La connexion Wi-Fi n'a pas été établie avant le test | Refaire la connexion du module `reseau` ; vérifier nom, mot de passe et bande 2,4 GHz |
| Code HTTP : 400 | L'adresse IP n'est pas autorisée dans l'application | L'ajouter dans les paramètres de l'application |
| Code HTTP : 404 | La route `/api/ping/` n'existe pas | Vérifier que la route est bien définie |
| ETIMEDOUT | Pas de réponse : mauvaise IP, pare-feu, ou serveur qui n'écoute pas sur tout le réseau | Revoir les étapes 2, 3 et 5 |
| EHOSTUNREACH | Le robot n'est pas sur le même réseau que le PC | Vérifier que les deux sont sur le même Wi-Fi |

Si une erreur parle du paramètre de délai (« timeout »), la version de la bibliothèque ne l'accepte pas : il faut alors retirer ce paramètre de la requête dans `test_ping.py`.

---

## 6. Journalisation simple sur la console série

### 6.1 Principe

Le robot n'a pas d'écran. On utilise donc `print()` : Thonny affiche tout dans sa console, à travers le câble USB. C'est ce qui permet de suivre ce que fait le robot et de comprendre une panne.

### 6.2 Conventions à respecter dans tous les modules

- Un préfixe entre crochets au début de chaque ligne :
  - `[INFO]` : fonctionnement normal
  - `[ATTENTION]` : problème récupérable
  - `[ERREUR]` : échec
  - `[TEST]` : diagnostic
- Un message court avec la valeur utile, par exemple `[INFO] Humidite : 42.5 %`.
- Un message à chaque événement important : connexion Wi-Fi réussie, coupure, reconnexion, batterie faible, obstacle détecté.

### 6.3 Exemple de ce qu'on voit dans la console

```
[INFO] Connexion Wi-Fi en cours...
[INFO] Wi-Fi connecte, IP : 192.168.1.42
[INFO] Humidite : 42.5 % Batterie : 7.6 V (73 %)
[ATTENTION] Wi-Fi perdu, nouvel essai dans 5 s
[ERREUR] Echec de communication : [Errno 110] ETIMEDOUT
```

### 6.4 Précautions

- Ne jamais afficher le mot de passe Wi-Fi.
- Ne pas journaliser à chaque tour d'une boucle très rapide : la console devient illisible. On utilise `INTERVALLE_MESURE_S` pour espacer les messages.
- La console série ne fonctionne que câble branché.
