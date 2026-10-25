# Conventions de code

## 1. Langue
- Tous les noms que nous créons (variables, fonctions, classes, tables, champs, JSON, statuts) sont en français, sans accents.
- Commentaires, docstrings, documentation et messages de commit sont en français.
- Un seul mot par concept, partout (code, BDD, JSON, doc). Voir le glossaire.

## 2. Règles de nommage (tous langages)
1. Variable = nom, fonction = verbe à l'infinitif : `humidite_sol`, `enregistrer_mesure()`.
2. Pas de mélange dans un même nom : `get_mesure` est interdit, on écrit `obtenir_mesure`.
3. Booléens : `est_valide`, `a_obstacle`.
4. Collections au pluriel : `zones`, `mesures`.
5. Unité dans le nom : `humidite_pourcent`, `duree_mission_secondes`, `distance_cm`.
6. Pas d'abréviations floues : `hum`, `mes`, `cap`. Seuls `id`, `db` et `url` sont admis.
7. Noms complets si plusieurs cas existent : `seuil_humidite` plutôt que `seuil`.

## 3. Python (général)
- Norme : PEP 8, appliquée par `black` et `ruff`.
- `snake_case` pour fonctions et variables, `MAJUSCULES` pour les constantes.
- 4 espaces d'indentation.
- Imports en haut du fichier, un par ligne, jamais `from x import *`.
- Docstring pour chaque fonction et classe publique, format Google.

## 4. Python orienté objet
- Classes en `PascalCase`, au singulier : `Mission`, `MesureHumidite`.
- Méthodes = verbes : `demarrer()`, `interrompre()`.
- Attribut ou méthode interne : préfixe `_` (`_calculer_seuil`).
- Une classe = une responsabilité.
- Chaque classe a une docstring et un `__str__` lisible.
- Pas de modification directe d'un attribut depuis l'extérieur : on passe par une méthode.
- Modèles Django : au singulier, avec `verbose_name` pour l'affichage.

## 5. Base de données et SQL
- Tables (modèles Django) au singulier : `Parcelle`, `Zone`, `Culture`, `Mission`, `EtapeMission`, `MesureHumidite`, `Irrigation`, `Incident`.
- Champs en `snake_case` : `date_creation`, `seuil_pourcent`, `duree_secondes`.
- Clé primaire : `id`. Clé étrangère : `zone_id`, `mission_id`.
- SQL brut : mots-clés en `MAJUSCULES`, une clause par ligne, jamais de `SELECT *` dans l'application.
- Toute modification de structure passe par les migrations Django, jamais à la main.
- Statuts de mission : `planifiee`, `en_cours`, `terminee`, `interrompue`.

## 6. JavaScript
- `camelCase` pour variables et fonctions (`humiditeSol`), `PascalCase` pour les classes, `MAJUSCULES` pour les constantes.
- `const` par défaut, `let` si besoin, jamais `var`.
- `===` et jamais `==`.
- Points-virgules, guillemets simples, 2 espaces d'indentation.
- Outils : `prettier` et `eslint`.
- Les clés JSON venant de l'API gardent leur nom en `snake_case` (`donnees.zone_id`). On ne les renomme pas.

## 7. React (frontend)
- Composants fonctionnels uniquement, pas de classes.
- Un composant par fichier, en `PascalCase`, avec le même nom que le fichier : `CarteParcelle.jsx`.
- Les props et les variables d'état en `camelCase`, avec les mêmes mots que le glossaire : `humiditeSol`, `zoneSelectionnee`.
- Les hooks personnalisés commencent par `use` (obligatoire pour React) : `useMesures`, `useMissions`.
- Fonctions qui réagissent à un événement : préfixe `gerer` (`gererClicZone`). Props qui reçoivent une fonction : préfixe `sur` (`surChangementZone`).
- Les appels à l'API sont dans `frontend/src/services/`, jamais directement dans les composants.
- Dossiers de `frontend/src/` : `composants/`, `pages/`, `hooks/`, `services/`.
- Un composant qui dépasse environ 150 lignes se découpe en sous-composants.

## 8. Firmware ESP32 (MicroPython)
- Mêmes règles que Python (sections 3 et 4).
- Constantes de broches en `MAJUSCULES`, regroupées dans `config.py` : `BROCHE_CAPTEUR_HUMIDITE`, `BROCHE_MOTEUR_GAUCHE`.
- Secrets (mot de passe WiFi, adresse du serveur) dans `secrets.py`, listé dans `.gitignore`. Un `secrets_exemple.py` est committé.
- `black` et `ruff` s'utilisent sur le PC, pas sur l'ESP32.

## 9. Contrat robot ↔ application
- Champs JSON : `robot_id`, `mission_id`, `zone_id`, `type`, `valeur`, `sequence`, `statut`.
- Les statuts ont exactement les mêmes valeurs que dans la BDD.
- Ce contrat est documenté dans `docs/protocole.md`. Toute modification passe par une pull request relue par les binômes B (API), D (robot) et E (communication).

## 10. Commentaires
- Expliquer le *pourquoi*, pas le *quoi*.
- `# TODO(nom): ...` toujours avec un nom.
- Pas de code commenté dans le dépôt.

## 11. Git
- `main` protégée, branches `feature/...` et `fix/...`.
- Toute pull request est relue par un autre binôme avant fusion dans `main`.
- Commits : `feat(mission): ajoute l'état interrompue`.
- Chacun commit sous son propre nom.

## 12. Structure du dépôt (mono-repo)
- `backend/` : Django + DRF (API, modèles, migrations, tests Pytest dans `backend/tests/`)
- `frontend/` : React + Vite (interface, carte Leaflet, graphiques)
- `firmware/` : MicroPython pour l'ESP32 (`config.py`, `secrets_exemple.py`)
- `docs/` : conventions, protocole, UML, schéma de câblage, budget
- `tests/` : tests d'intégration de bout en bout
- `README.md` : installation et lancement. `CONTRIBUTING.md` renvoie vers ce fichier.

## 13. Glossaire
| Concept | Nom dans le code |
|---|---|
| parcelle | `parcelle` |
| zone | `zone` |
| culture | `culture` |
| mission / étape | `mission` / `etape` |
| mesure | `mesure` |
| humidité du sol | `humidite_sol` |
| irrigation | `irrigation` (on n'utilise pas « arrosage » dans le code) |
| seuil | `seuil` |
| étalonnage | `etalonnage` |
| capteur | `capteur` |
| statut | `statut` |
| incident | `incident` |
| historique | `historique` |
| rapport | `rapport` |
| tableau de bord | `tableau_de_bord` |