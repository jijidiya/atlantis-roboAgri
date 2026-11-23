# Contrat d'API frontend ↔ backend

Rédigé le 18 novembre 2026 (binôme C). Source : lecture du code backend de `main` et des hooks du frontend.
La colonne « Testé » passe à ✅ quand l'adresse a été appelée à la main et que la réponse correspond.

## 1. Conventions

- **Préfixe** : `/api/v1/`. En développement, Vite redirige `/api` vers `http://localhost:8000` (`vite.config.js`).
- **Authentification** : JWT. En-tête `Authorization: Bearer <acces>`. Sur un 401, `api/http.js` appelle `POST /auth/rafraichir/` puis rejoue la requête une seule fois.
- **Rôles** : un administrateur voit tout ; un autre compte ne voit que ce qui touche ses parcelles ou ses missions.
- **Listes** : deux formes coexistent.
  - Tableau brut : parcelles, zones, cultures, missions.
  - Paginé `{ count, next, previous, results }`, 50 par page, 100 au maximum avec `?page_size=` : mesures, incidents, irrigations, décisions. Le frontend ne suit pas `next`.
- **Décimaux** : renvoyés **en texte** (`"30.00"`).
- **Erreurs** : toute erreur arrive sous la forme `{ "erreur": { "code", "message", "details" } }` (`apps/core/exceptions.py`). Codes : `DONNEES_INVALIDES` (400), `NON_AUTHENTIFIE` et `IDENTIFIANTS_INVALIDES` (401), `ACCES_REFUSE` et `ARROSAGE_INTERDIT` (403), `RESSOURCE_INTROUVABLE` (404), `METHODE_NON_AUTORISEE` (405), `TRANSITION_INTERDITE` et `CONFLIT` (409), `ERREUR_INTERNE` (500). Pour un 400 de validation, `details` vaut `{ champ: [messages] }` (ou `non_field_errors`). Deux exceptions à l'enveloppe : voir partie 8.

## 2. Authentification

| Hook | Appel | Corps / paramètres | Réponse | Testé |
|---|---|---|---|---|
| `useConnexion` | POST `/auth/connexion/` | `{ email, mot_de_passe }` | `{ acces, rafraichissement, utilisateur:{id,email,nom,prenom,role} }` | ✅ |
| `http.js` | POST `/auth/rafraichir/` | `{ rafraichissement }` | `{ acces, rafraichissement }` | ☐ |
| `useMoi` | GET `/auth/moi/` | | `{ id, email, nom, prenom, role }` | ✅ |
| `useModifierProfil` | PATCH `/auth/moi/` | `{ prenom, nom, email }` | profil mis à jour | ☐ |

## 3. Parcelles, zones, cultures

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useParcelles` | GET `/parcelles/` | | tableau brut, zones et cultures incluses | non | ✅ |
| `useParcelle(id)` | GET `/parcelles/{id}/` | | objet | non | ☐ |
| `useCreerParcelle` | POST `/parcelles/` | `nom, longitude, latitude, superficie` | objet | | ☐ |
| `useModifierParcelle(id)` | PATCH `/parcelles/{id}/` | champs à changer | objet | | ☐ |
| `useSupprimerParcelle` | DELETE `/parcelles/{id}/` | | 204 | | ☐ |
| `useZones` | GET `/zones/` | `?parcelle=ID` (facultatif) | tableau brut | non | ✅ |
| `useZone(id)` | GET `/zones/{id}/` | | objet | non | ☐ |
| `useCreerZone` | POST `/zones/` | `nom, superficie, humidite_minimum, humidite_maximum, parcelle…` | objet | | ☐ |
| `useModifierZone(id)`, `useModifierSeuilsZones` | PATCH `/zones/{id}/` | `{ humidite_minimum, humidite_maximum }` | objet ; 400 si minimum ≥ maximum | | ☐ |
| `useSupprimerZone` | DELETE `/zones/{id}/` | | 204 | | ☐ |
| `useCultures` | GET `/cultures/` | | tableau brut `{culture_id, nom, variete}` | non | ✅ |
| `useCreerCulture` | POST `/cultures/` | `nom, variete` | objet | | ☐ |

Champs d'une zone : `zone_id, nom, superficie, humidite_minimum, humidite_maximum, geometrie_zone, irrigation_auto_active, parcelle, cultures[]`.
Champs d'une parcelle : `parcelle_id, nom, longitude, latitude, superficie, utilisateur, zones[]`.

## 4. Missions

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useMissions` | GET `/missions/` | `?statut=` (un seul statut), `?parcelle=` | tableau brut | non | ✅ |
| `useMission(id)` | GET `/missions/{id}/` | | objet | 3 s tant que la mission n'est pas finale | ☐ |
| `useCreerMission` | POST `/missions/` | `{ parcelle, utilisateur (facultatif), etapes:[{numero_ordre, zone}] }` | objet ; 400 si zone hors parcelle | | ☐ |
| `useDemarrerMission` | POST `/missions/{id}/demarrer/` | | objet ; 409 si statut ≠ planifiee | | ☐ |
| `useTerminerMission` | POST `/missions/{id}/terminer/` | | objet ; 409 si statut ≠ en_cours | | ☐ |
| `useInterrompreMission` | POST `/missions/{id}/interrompre/` | | objet ; 409 si statut ≠ en_cours | | ☐ |

Champs d'une mission : `mission_id, statut, date_creation, date_debut, date_fin, utilisateur, parcelle, etapes[]`.
Champs d'une étape : `etape_id, numero_ordre, zone, statut, date_debut, date_fin`.

## 5. Mesures

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useMesures` | GET `/mesures/` | `mission, zone, statut, du, au` | paginé | 3 s si demandé | ✅ |
| `useMesuresRecentes` | GET `/mesures/` | `page_size, statut` | paginé | 3 s si demandé | ☐ |

Champs : `mesure_id, mission, zone, etape, numero_point, numero_lecture, valeur_brute, valeur_humidite, date_heure_mesure, statut, message, incident, analyse`.

## 6. Irrigation

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useDecisionCourante(zoneId)`, `useDecisionZone(id)` | GET `/zones/{id}/decision/` | | objet décision | non | ☐ |
| `useDecisions` | GET `/decisions/` | `zone, statut, du, au` | paginé | non | ✅ |
| `useIrrigations` | GET `/irrigations/` | `zone, statut` (le backend accepte aussi `automatique, du, au`) | paginé | non | ✅ |
| `useSeuilsZones` | GET `/irrigations/seuils/` | | tableau brut de zones (seuils) | non | ✅ |
| `useCreerIrrigation` | POST `/irrigations/` | `{ zone, duree_secondes }` | objet ; 403 si arrosage interdit | | ☐ |

Champs d'une décision : `decision_id, zone, type_decision, action, justification, humidite_moyenne, seuil_min_applique, seuil_max_applique, statut, date_decision, analyse`.
Champs d'une irrigation : `irrigation_id, zone, automatique, statut, duree_secondes, volume_ml, date_debut, date_fin, decision, utilisateur`.

Erreurs propres à cette partie :
- `GET /zones/{id}/decision/` : 404 `RESSOURCE_INTROUVABLE` (« Aucune décision pour cette zone ») si la zone n'a pas encore de décision.
- `POST /irrigations/` : 403 `ARROSAGE_INTERDIT` avec `details: { raison, statut_mesure }` si la dernière mesure n'est pas valide ou si la durée dépasse le maximum (300 s par défaut).

## 7. Incidents

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useIncidents` | GET `/incidents/` | `mission, type_incident, du, au` | paginé | 10 s par défaut | ✅ |

Champs : `incident_id, type_incident, date_incident, mission, mesures[]`. Pas de gravité, de statut ni de zone.

## 8. Différences à discuter avec le groupe B

Formats confirmés par appel direct le 18/11 ; le reste vient de la lecture du code.

1. **Sécurité : arrosage manuel sans contrôle de propriété (à traiter en priorité).** `IrrigationManuelleSerializer` accepte `Zone.objects.all()` et `creer_irrigation_manuelle` ne vérifie pas que la zone appartient à l'utilisateur, alors que `GET /irrigations/` est filtré par propriétaire. D'après le code, un compte non administrateur peut enregistrer un arrosage sur la zone d'un autre. À confirmer par un test avec un compte non administrateur, puis à corriger (restreindre le choix de la zone selon l'utilisateur).
2. **Décimaux en texte** (`"30.00"`) : le frontend convertit avec `Number()`. À garder ou à passer en nombres ?
3. **Pagination incohérente** : parcelles, zones, cultures et missions renvoient un tableau brut (aucune pagination par défaut dans `settings.py`), les autres ressources sont paginées (50 par page). Le frontend ne suit pas `next` : la page Capteurs ne voit que les 50 dernières des 292 mesures valides.
4. **Filtre `statut` des missions** : un seul statut à la fois. L'onglet « À vérifier » (interrompue + non_confirmee) filtre donc côté frontend.
5. **Transitions de mission en double et forme d'erreur différente** : `missions/views.py` a son propre dictionnaire et renvoie un 409 de la forme `{ "detail": ... }`. `missions/services.py` connaît aussi `non_confirmee`, lèverait `TRANSITION_INTERDITE` au bon format, mais n'est pas utilisé par la vue.
6. **Autre exception à l'enveloppe** : `GET /zones/{id}/decision/` renvoie `{ "detail": "Zone introuvable." }` pour une zone d'un autre utilisateur, alors qu'une zone inexistante ou sans décision renvoie le format normal.
7. **Zone sans décision** : 404. Le frontend l'absorbe ; à garder, ou à remplacer par un 200 avec une valeur vide ?
8. **Codes d'erreur** : le backend les écrit en majuscules (`DONNEES_INVALIDES`), le frontend (`api/config.js`) en minuscules (`validation`). Les pages lues utilisent le statut HTTP, pas le code ; à aligner avant que quelqu'un compare les codes.
9. **Langue** : `LANGUAGE_CODE = 'en-us'`, donc les messages de validation par défaut dans `details` arrivent en anglais. À passer en `fr` ou à traduire côté frontend.
10. **Nommage** : `/auth/moi/` renvoie `id`, les autres ressources renvoient `<ressource>_id`.
11. **État du robot** : le polling de 5 s prévu pour l'état du robot n'a aucune adresse côté application (`useRobot.js` est vide). Les adresses `/robot/...` sont destinées au robot.
12. **Doublons côté frontend** : `useDecisionCourante` et `useDecisionZone` appellent la même adresse ; `/irrigations/seuils/` fait double emploi avec `/zones/`.