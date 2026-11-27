# Scénarios du robot, à la main : compte rendu

Date : 22 novembre 2026. Méthode : requêtes `Invoke-RestMethod` / `Invoke-WebRequest` (PowerShell) contre le serveur local `http://localhost:8000/api/v1`, avec la clé `X-Cle-Robot` pour le robot et un jeton JWT pour le propriétaire.

Données utilisées : base de démonstration (`donnees_demo.py`), compte `junior.diyabanza@demo.roboagri.cd`, parcelle 10, zones 22 (« Planche A - Tomates », seuils 35–70 %, irrigation auto activée) et 23 (« Planche B - Choux », seuils 40–75 %).

**Convention.** « Observé » = résultat visible dans le terminal. « Déduit du code » = prévision tirée de la lecture du code, **pas encore vérifiée** par une requête.

## 1. Résultats

| # | Scénario | Attendu (cahier) | Observé | Conclusion |
| --- | --- | --- | --- | --- |
| 1a | Cas nominal : `GET robot/mission-suivante/` | Mission à exécuter | `200`, mission 43, `planifiee`, parcelle 10, 2 étapes (zones 22 et 23) | Conforme |
| 1b | Cas nominal : message `etat` = `en_cours` | Mission démarrée | `201`, `deja_recu: false`, aucune mesure ni décision | Conforme |
| 1c | Cas nominal : message `mesure` avec 9 lectures (25 %, brut 2000) | Mesures enregistrées, décision créée | `201`, 9 mesures (ids 1099 à 1107), décision 123, `valide: true`, aucun incident | Conforme |
| 1d | Cas nominal : message `mission_recue` (les deux autres types de la démo ne sont pas testés) | Accepté | `400` « type : valeurs possibles : mesure, etat, incident » | **Incohérence** n°1 (confirmée) |
| 1e | Cas nominal : fin de mission (`etat` = `terminee`) sur la mission 56 (en cours) | Mission terminée | `201`, `deja_recu: false`. `GET missions/56/` : statut `terminee`, `date_debut` 11:37:10Z, `date_fin` 12:44:03Z | Conforme |
| 1f | Transition interdite : `etat` = `terminee` sur la mission 58 (planifiée) | Refusée | `409 TRANSITION_INTERDITE` « Impossible de passer la mission de « planifiee » à « terminee » », détails `statut_actuel` / `statut_demande` | Conforme |
| 2 | Doublon : même message renvoyé | Même réponse, rien de plus en base | `200`, `deja_recu: true`, mêmes ids de mesures (1099 à 1107) et même décision (123) | Conforme (le nombre de lignes en base n'a pas été contrôlé) |
| 3 | Conflit : même `message_id`, lectures à 80 % au lieu de 25 % | `409` | `200`, `deja_recu: true`, mêmes ids (1099 à 1107) et même décision (123) : le contenu n'est pas comparé | **Incohérence** n°2 (confirmée) |
| 4 | Lecture invalide : brut extrême (5), mission 57, zone 22 | Recommandation interdite, incident créé | `201`, `valide: false`, 9 mesures (ids 1137 à 1145), incident 15 `mesure_invalide`, décision 127. `GET mesures/` : statut invalide, `valeur_brute: 5`, `valeur_humidite: 25.00`. `GET zones/22/decision/` : `mesure_invalide`, `ne_pas_arroser`, statut `refusee`, moyenne vide, seuils 35 / 70 | **Conforme** (les essais précédents avaient échoué en 400 faute de `$m2`) |
| 5 | Humidité hors de 0 à 100 (150 %), mission 58, zone 22 | `422`, rien d'enregistré | `201`, `valide: false`, **9 mesures enregistrées** (ids 1157 à 1165, `valeur_humidite` vide), incident 17, décision 129 (`GET decisions/?zone=22` : `mesure_invalide`, `ne_pas_arroser`). (Un premier essai avait donné `409` : horodatage réutilisé.) | **Incohérence** n°3 (confirmée) : pas de 422, les lectures sont conservées avec le statut « invalide » |

Ce qui est validé : l'authentification, la validation de forme du message (le `400` du test 4 est bien renvoyé, au format `{erreur: {code, message, details}}`), l'enregistrement de 9 mesures, la création d'une décision et l'idempotence sur doublon.

## 2. Incohérences trouvées

### Entre le cahier des charges et le code

1. **Types de messages.** Le cahier cite `mission_recue`, `etape_atteinte` et `changement_etat`. Le protocole du backend (`protocole.py`) n'accepte que `mesure`, `etat` et `incident`. Ces trois noms n'existent que dans `donnees_demo.py`. Décision à prendre : adapter le cahier, ou ajouter ces types au backend.
2. **Conflit sur `message_id`.** Le cahier attend un `409` si le même identifiant revient avec un contenu différent. Le code ne regarde que l'identifiant et répond `200 deja_recu`. Un contenu différent est ignoré en silence.
3. **Humidité hors plage.** Le cahier attend un `422` et rien d'enregistré. Le code enregistre la lecture avec le statut « invalide », crée un incident et répond `201`. Le code `422` n'existe pas dans le backend. Le comportement du code est cohérent avec la règle « une mesure douteuse n'est jamais rejetée » (RG17).

### Entre la base de démonstration et le vrai traitement

4. **Décisions de la démo.** `donnees_demo.py` crée des décisions « autorisée » avec l'action `arrosage_automatique`, ainsi que `arrosage_recommande` et `aucune_action`. Le vrai code ne produit que le statut `recommandee` ou `refusee` et les actions `arroser` ou `ne_pas_arroser`. Les écrans du frontend testés sur la démo n'afficheront donc pas les mêmes valeurs qu'avec de vrais messages.
5. **Statut « refusée » pour une humidité suffisante.** Quand l'humidité est suffisante, le vrai code enregistre une décision `refusee` (action `ne_pas_arroser`). Le mot est trompeur : rien n'est refusé, il n'y a simplement rien à faire. La démo utilise `recommandee` + `aucune_action` pour le même cas.
6. **Irrigation automatique jamais déclenchée.** La zone 22 a `irrigation_auto_active: true` (observé), mais le traitement du robot ne crée aucune irrigation automatique. La case n'a aucun effet aujourd'hui.

### Dans le comportement de l'API

7. **`mission-suivante` n'est pas ciblée.** Elle renvoie la plus ancienne mission planifiée de **tous** les utilisateurs et ne la marque pas comme prise. Observé : elle a renvoyé la mission 43 (démo, deux étapes), qui n'est pas forcément la mission de test créée à la main. Un second appel renvoie la même mission tant que le robot n'a pas envoyé `etat = en_cours`.
8. **Aucun contrôle de l'état de la mission pour une mesure** (déduit du code). Une mesure est acceptée sur une mission `planifiee`, `terminee` ou `interrompue`. L'étape passe directement à « terminée » sans passer par « en cours ».
9. **Mesures anciennes.** Une mesure dont l'horodatage a plus de 30 minutes (`AGE_MAX_MESURE_SECONDES`) est traitée comme invalide et crée un incident. Un robot qui renvoie des messages mis en attente pendant une coupure produira des incidents « mesure invalide » à tort (déduit du code).
10. **Pagination irrégulière.** `GET parcelles/` renvoie un simple tableau (observé : `(…)[0]` donne la première parcelle), alors que mesures, décisions, irrigations et incidents renvoient `{count, next, previous, results}`.
11. **Modèle inutilisé.** `MessageRecu` existe en base mais le traitement n'utilise que `Message`.

### Constatés pendant les tests

12. **Une étape accepte plusieurs lots de 9 lectures** (observé). Deux messages `mesure` successifs sur l'étape 153 (mission 57), avec des horodatages différents, ont été acceptés : ids 1137 à 1145, puis 1147 à 1155, soit 18 lectures pour une étape censée en avoir 9 (RG7). Seule la contrainte d'unicité (étape, point, lecture, horodatage) existe : elle ne bloque que les lectures à horodatage identique, d'où le `409` du scénario 5. Chaque lot crée en plus sa propre analyse, sa décision et un incident (incidents 15 et 16).
13. **Faille confirmée : mission créée sur la parcelle d'un autre utilisateur.** La mission 56 a été créée par `junior` avec `parcelle=1` et `zone=1`, alors que ses parcelles sont la 10 (zones 22 et 23). Le backend l'a acceptée. Le sérialiseur ne vérifie que la règle RG5 (la zone appartient à la parcelle de la mission), pas que la parcelle appartient à l'utilisateur. Vérification faite : `GET parcelles/1/` avec le jeton de `junior` répond `404 RESSOURCE_INTROUVABLE`, donc la parcelle 1 n'est pas la sienne alors qu'une mission (56) a été créée dessus. C'est une faille de contrôle d'accès : un propriétaire peut planifier le robot sur la parcelle d'un autre. Correction à prévoir dans `MissionSerializer.validate` : refuser (403 ou 404) si `parcelle.utilisateur` n'est pas l'utilisateur connecté, sauf pour un administrateur.
14. **Le robot peut travailler sur une autre mission que celle qu'il a reçue.** `mission-suivante` a renvoyé la mission 43 ; les messages ont été envoyés sur la mission 56, acceptée sans contrôle (confirme les points 7 et 8).
15. **Jeton d'accès expiré.** Une heure après la connexion, `GET mesures/`, `zones/22/decision/` et `incidents/` répondent `401 NON_AUTHENTIFIE` (observé). `settings.py` ne fixe pas la durée du jeton : c'est la valeur par défaut de simplejwt (5 minutes). Le frontend doit donc appeler `auth/rafraichir/` régulièrement, et les tests manuels doivent se reconnecter.
16. **Accents mal affichés** dans le terminal : « Maraîchage de Kimwenza (démo) » apparaît « MaraÃ®chage … dÃ©mo ». C'est un défaut d'affichage de PowerShell (décodage de la réponse), pas des données : la base contient le bon texte. Contournement : décoder la réponse en UTF-8 (`[Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray())`) ou utiliser PowerShell 7.

## 3. Conclusion

Tous les scénarios ont été exécutés. Le backend est conforme sur : le cas nominal (mission, état, 9 mesures, décision, fin de mission), le doublon, la lecture invalide, le refus d'une transition interdite. Les écarts avec le cahier (types de messages, absence de 409 sur conflit de contenu, absence de 422 hors plage) sont décrits en section 2.

Corrections conseillées dans le backend, par priorité :

1. **Contrôle de propriété de la parcelle** à la création d'une mission (point 13, faille confirmée).
2. **Limite de 9 lectures par étape** et refus d'un second lot (point 12).
3. **`mission-suivante` réservée** : la marquer comme prise ou la lier à une parcelle, et vérifier que les messages visent la mission en cours (points 7, 8, 14).
4. **Décision à prendre avec l'équipe** : aligner le cahier sur le code (types de messages, 200 sur conflit, 201 sur humidité hors plage) ou l'inverse.
5. Aligner `donnees_demo.py` sur le vrai traitement (points 4 et 5) et brancher ou retirer `irrigation_auto_active` (point 6).
