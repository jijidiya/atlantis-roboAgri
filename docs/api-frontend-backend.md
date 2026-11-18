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
- **Erreurs** : `http.js` comprend trois formes (`{erreur:{code,message,details}}`, `{detail}`, `{champ:[messages]}`). Quelle forme le backend envoie réellement est à confirmer.

## 2. Authentification

| Hook | Appel | Corps / paramètres | Réponse | Testé |
|---|---|---|---|---|
| `useConnexion` | POST `/auth/connexion/` | `{ email, mot_de_passe }` | `{ acces, rafraichissement, utilisateur:{id,email,nom,prenom,role} }` | ☐ |
| `http.js` | POST `/auth/rafraichir/` | `{ rafraichissement }` | `{ acces, rafraichissement }` | ☐ |
| `useMoi` | GET `/auth/moi/` | | `{ id, email, nom, prenom, role }` | ☐ |
| `useModifierProfil` | PATCH `/auth/moi/` | `{ prenom, nom, email }` | profil mis à jour | ☐ |

## 3. Parcelles, zones, cultures

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useParcelles` | GET `/parcelles/` | | tableau brut, zones et cultures incluses | non | ☐ |
| `useParcelle(id)` | GET `/parcelles/{id}/` | | objet | non | ☐ |
| `useCreerParcelle` | POST `/parcelles/` | `nom, longitude, latitude, superficie` | objet | | ☐ |
| `useModifierParcelle(id)` | PATCH `/parcelles/{id}/` | champs à changer | objet | | ☐ |
| `useSupprimerParcelle` | DELETE `/parcelles/{id}/` | | 204 | | ☐ |
| `useZones` | GET `/zones/` | `?parcelle=ID` (facultatif) | tableau brut | non | ☐ |
| `useZone(id)` | GET `/zones/{id}/` | | objet | non | ☐ |
| `useCreerZone` | POST `/zones/` | `nom, superficie, humidite_minimum, humidite_maximum, parcelle…` | objet | | ☐ |
| `useModifierZone(id)`, `useModifierSeuilsZones` | PATCH `/zones/{id}/` | `{ humidite_minimum, humidite_maximum }` | objet ; 400 si minimum ≥ maximum | | ☐ |
| `useSupprimerZone` | DELETE `/zones/{id}/` | | 204 | | ☐ |
| `useCultures` | GET `/cultures/` | | tableau brut `{culture_id, nom, variete}` | non | ☐ |
| `useCreerCulture` | POST `/cultures/` | `nom, variete` | objet | | ☐ |

Champs d'une zone : `zone_id, nom, superficie, humidite_minimum, humidite_maximum, geometrie_zone, irrigation_auto_active, parcelle, cultures[]`.
Champs d'une parcelle : `parcelle_id, nom, longitude, latitude, superficie, utilisateur, zones[]`.

## 4. Missions

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useMissions` | GET `/missions/` | `?statut=` (un seul statut), `?parcelle=` | tableau brut | non | ☐ |
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
| `useMesures` | GET `/mesures/` | `mission, zone, statut, du, au` | paginé | 3 s si demandé | ☐ |
| `useMesuresRecentes` | GET `/mesures/` | `page_size, statut` | paginé | 3 s si demandé | ☐ |

Champs : `mesure_id, mission, zone, etape, numero_point, numero_lecture, valeur_brute, valeur_humidite, date_heure_mesure, statut, message, incident, analyse`.

## 6. Irrigation

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useDecisionCourante(zoneId)`, `useDecisionZone(id)` | GET `/zones/{id}/decision/` | | objet décision | non | ☐ |
| `useDecisions` | GET `/decisions/` | `zone, statut, du, au` | paginé | non | ☐ |
| `useIrrigations` | GET `/irrigations/` | `zone, statut` (le backend accepte aussi `automatique, du, au`) | paginé | non | ☐ |
| `useSeuilsZones` | GET `/irrigations/seuils/` | | tableau brut de zones (seuils) | non | ☐ |
| `useCreerIrrigation` | POST `/irrigations/` | `{ zone, duree_secondes }` | objet ; 403 si arrosage interdit | | ☐ |

Champs d'une décision : `decision_id, zone, type_decision, action, justification, humidite_moyenne, seuil_min_applique, seuil_max_applique, statut, date_decision, analyse`.
Champs d'une irrigation : `irrigation_id, zone, automatique, statut, duree_secondes, volume_ml, date_debut, date_fin, decision, utilisateur`.

## 7. Incidents

| Hook | Appel | Paramètres | Réponse | Polling | Testé |
|---|---|---|---|---|---|
| `useIncidents` | GET `/incidents/` | `mission, type_incident, du, au` | paginé | 10 s par défaut | ☐ |

Champs : `incident_id, type_incident, date_incident, mission, mesures[]`. Pas de gravité, de statut ni de zone.

## 8. Différences à discuter avec le groupe B

1. **Décimaux en texte** (`"30.00"`) : le frontend doit convertir avec `Number()`. À garder tel quel ou à passer en nombres ?
2. **Pagination incohérente** : parcelles, zones, cultures et missions renvoient un tableau brut, les autres ressources sont paginées. Le frontend utilise `enListe` pour absorber les deux.
3. **Filtre `statut` des missions** : un seul statut à la fois. L'onglet « À vérifier » (interrompue + non_confirmee) doit donc filtrer côté frontend.
4. **Transitions de mission en double** : `missions/views.py` a son propre dictionnaire, `missions/services.py` en a un second (qui connaît `non_confirmee`) et n'est pas utilisé par la vue.
5. **Nommage** : `/auth/moi/` renvoie `id`, les autres ressources renvoient `<ressource>_id`.
6. **Arrosage manuel** : `IrrigationManuelleSerializer` accepte n'importe quelle zone existante. À vérifier que `services.creer_irrigation_manuelle` contrôle que la zone appartient à l'utilisateur.
7. **Décision d'une zone sans décision** : ce que renvoie `GET /zones/{id}/decision/` quand il n'y en a aucune est à tester.
8. **État du robot** : le polling de 5 s prévu pour l'état du robot n'a aucune adresse côté application (`useRobot.js` est vide). Les adresses `/robot/...` sont destinées au robot.
9. **Doublons côté frontend** : `useDecisionCourante` et `useDecisionZone` appellent la même adresse ; `/irrigations/seuils/` fait double emploi avec `/zones/`.