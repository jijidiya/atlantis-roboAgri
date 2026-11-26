# RoboAgri-Kin : backend

API et application de gestion du projet **RoboAgri-Kin** (Projet de Programmation III, L3 Sciences Informatiques, UCC).
Le backend gère les parcelles, les zones, les cultures, les missions du robot, les mesures d'humidité du sol, les décisions d'irrigation et les incidents.

- **Version du document** : 2.0 (dernière mise à jour : 18 novembre 2026). Voir l'historique à la fin.
- **Technologies** : Python, Django, Django REST Framework, PostgreSQL (TimescaleDB pour les mesures), JWT, drf-spectacular, Pytest.
- **Frontend** : voir `../frontend/` (React + Vite).
- **Documents liés** : `docs/api-frontend-backend.md` (format des API), `docs/protocole-communication.md` (échanges robot ↔ application), `docs/conception/architecture.md`.

---

## 1. Prérequis

| Outil | Version | Remarque |
|---|---|---|
| Python | 3.12 ou plus récent | testé avec 3.14 |
| PostgreSQL | 14 ou plus récent | installé en local (Docker viendra plus tard) |
| Git | récent | |

Django doit être en version **5.1 ou plus** (les contraintes utilisent `CheckConstraint(condition=...)`).

Les bibliothèques Python notables (dans `requirements.txt`) :

- `djangorestframework` : API REST
- `djangorestframework-simplejwt` : authentification par jetons JWT
- `drf-spectacular` : génération du schéma OpenAPI
- `django-cors-headers` : CORS pour le frontend
- `pytest` + `pytest-django` : tests

---

## 2. Installation

Toutes les commandes sont pour **PowerShell (Windows)**, depuis le dossier `backend/`.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell refuse d'activer l'environnement virtuel :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 3. Configuration (`.env`)

Les réglages sensibles sont lus dans un fichier `backend/.env`, **jamais commité** (il est dans `.gitignore`).
Copier le modèle puis adapter les valeurs :

```powershell
Copy-Item .env.example .env
```

Contenu de `.env.example` :

```
DEBUG=True
SECRET_KEY=change-moi-par-une-cle-secrete-aleatoire
BASE_NOM=roboagri
BASE_UTILISATEUR=roboagri
BASE_MOT_DE_PASSE=roboagri
BASE_HOTE=localhost
BASE_PORT=5432
CLE_ROBOT=change-moi-par-un-jeton-robot
ALLOWED_HOSTS=localhost,127.0.0.1,<votre_ip_locale>
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Pour générer une vraie `SECRET_KEY` :

```powershell
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

**`CLE_ROBOT`** est le jeton que le robot (ou le simulateur) envoie dans l'en-tête `X-Cle-Robot` pour s'authentifier sur les endpoints `/robot/*`. Elle ne doit jamais figurer dans le code.

---

## 4. Base de données

Dans `psql` (ou pgAdmin), connecté en tant que `postgres` :

```sql
CREATE USER roboagri WITH PASSWORD 'roboagri';
CREATE DATABASE roboagri OWNER roboagri;
ALTER USER roboagri CREATEDB;   -- nécessaire pour que Pytest crée sa base de test
```

Puis, depuis `backend/` :

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Pour `createsuperuser`, Django demande l'**email** (identifiant de connexion), le nom, le prénom et le mot de passe.

> **Repartir de zéro** : si les migrations sont incohérentes (`InconsistentMigrationHistory`), supprimer et recréer la base (`DROP DATABASE roboagri;` puis `CREATE DATABASE roboagri OWNER roboagri;`), puis relancer `migrate`.

---

## 5. Lancer le serveur

```powershell
python manage.py runserver
```

| Adresse | Contenu |
|---|---|
| http://127.0.0.1:8000/admin/ | Administration Django (saisie et vérification des données) |
| http://127.0.0.1:8000/api/v1/parcelles/ | API des parcelles (page de test DRF) |
| http://127.0.0.1:8000/api/v1/missions/ | API des missions |
| http://127.0.0.1:8000/api/docs/ | **Swagger UI** (documentation interactive, test des endpoints) |
| http://127.0.0.1:8000/api/redoc/ | **ReDoc** (documentation lisible) |
| http://127.0.0.1:8000/api/schema/ | Schéma OpenAPI brut (YAML) |

---

## 6. Structure

```
backend/
  manage.py
  pytest.ini
  conftest.py              # fixtures partagées par les tests
  requirements.txt
  .env / .env.example
  config/                  # settings.py, urls.py
  apps/
    core/                    # outils communs (exceptions, permissions, pagination, filtres)
    utilisateurs/            # UTILISATEUR + authentification JWT
    parcelles/               # PARCELLE, ZONE, CULTURE, CULTIVER
    missions/                # MISSION, ETAPE
    communication/           # MESSAGE (messages reçus du robot)
    mesures/                 # MESURE (hypertable TimescaleDB)
    analyse/                 # ANALYSE (modèle seulement, pas d'API)
    incidents/               # INCIDENT
    irrigation/              # DECISION, IRRIGATION
    dashboard/               # (pas encore de modèle ni d'API)
  tests/                   # tests transverses et d'intégration
```

Chaque application suit le même schéma : `models.py`, `admin.py`, `serializers.py`, `views.py`, `urls.py`, parfois `services.py` et `handlers.py`.

Un module ne dépend que des modules plus « bas » dans cet ordre :
`utilisateurs` → `parcelles` → `missions` → `communication` / `mesures` → `analyse` → `irrigation`.

Pour éviter les imports circulaires, les clés étrangères vers une autre application s'écrivent par chaîne : `"parcelles.Zone"`.

---

## 7. État d'avancement

| Module | Modèles | API | Tests |
|---|---|---|---|
| utilisateurs | fait | **fait (JWT)** | **fait** |
| parcelles | fait | fait | fait |
| missions | fait | fait | fait |
| communication | **fait (`Message`)** | **fait (robot + lecture)** | à faire |
| mesures | fait | **fait (lecture seule)** | à faire |
| analyse | fait | à faire | à faire |
| incidents | fait | **fait (lecture seule)** | à faire |
| irrigation | fait | **fait** | partiel |
| dashboard | sans modèle | à faire | à faire |

> Les fonctionnalités non réalisées sont signalées ici, comme l'exige le sujet.

---

## 8. API (résumé)

Format JSON, adresses terminées par `/`. Préfixe commun : `/api/v1/`.
Détail complet et interactif : `http://127.0.0.1:8000/api/docs/`.

### 8.1 Authentification

Authentification par **JWT** (`djangorestframework-simplejwt`). Le login accepte `email` (recommandé) ou l'alias `nom_utilisateur`.

| Méthode | URL | Rôle |
|---|---|---|
| POST | `/api/v1/auth/connexion/` | Login → `{ acces, rafraichissement, utilisateur }` |
| POST | `/api/v1/auth/rafraichir/` | Renouveler l'`acces` à partir du `rafraichissement` |
| GET | `/api/v1/auth/moi/` | Profil courant → `{ id, email, nom, prenom, role }` |
| PATCH | `/api/v1/auth/moi/` | Modifier prénom, nom, email |

Les routes protégées attendent l'en-tête `Authorization: Bearer <acces>`.

### 8.2 Parcelles, zones, cultures

| Méthode | URL | Rôle |
|---|---|---|
| GET, POST | `/api/v1/parcelles/` | Lister, créer (avec leurs zones en lecture) |
| GET, PUT, PATCH, DELETE | `/api/v1/parcelles/{id}/` | Consulter, modifier, supprimer |
| GET, POST | `/api/v1/zones/?parcelle={id}` | Lister (filtre facultatif), créer |
| GET, PUT, PATCH, DELETE | `/api/v1/zones/{id}/` | Consulter, modifier, supprimer |
| GET | `/api/v1/zones/{id}/decision/` | Décision d'irrigation courante pour la zone |
| GET, POST | `/api/v1/cultures/` | Lister, créer |

### 8.3 Missions

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/api/v1/missions/?parcelle={id}&statut={statut}` | Lister (filtres facultatifs) |
| POST | `/api/v1/missions/` | Créer une mission avec ses étapes |
| GET | `/api/v1/missions/{id}/` | Consulter (avec étapes) |
| POST | `/api/v1/missions/{id}/demarrer/` | `planifiee` → `en_cours` |
| POST | `/api/v1/missions/{id}/terminer/` | `en_cours` → `terminee` |
| POST | `/api/v1/missions/{id}/interrompre/` | `en_cours` → `interrompue` |

Exemple de création d'une mission :

```json
{
  "parcelle": 1,
  "etapes": [
    {"numero_ordre": 1, "zone": 1},
    {"numero_ordre": 2, "zone": 2}
  ]
}
```

Codes de réponse : `201` créé, `400` données invalides, `409` changement de statut interdit.

### 8.4 Mesures, décisions, irrigations, incidents

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/api/v1/mesures/?mission={id}&zone={id}&statut={statut}&du={date}&au={date}` | Mesures filtrées |
| GET | `/api/v1/mesures/{id}/` | Détail d'une mesure |
| GET | `/api/v1/decisions/?zone={id}&statut={statut}&du={date}&au={date}` | Décisions d'irrigation |
| GET | `/api/v1/irrigations/?zone={id}&automatique={bool}&statut={statut}` | Historique des interventions |
| POST | `/api/v1/irrigations/` | Créer un arrosage manuel |
| GET | `/api/v1/irrigations/seuils/` | Seuils de toutes les zones de l'utilisateur |
| GET | `/api/v1/incidents/?mission={id}&type_incident={type}&du={date}&au={date}` | Incidents |

**Pagination** : `/mesures/`, `/decisions/`, `/irrigations/`, `/incidents/` retournent `{ count, next, previous, results }` (20 par défaut, 100 maximum via `?page_size=`). Les listes `/parcelles/`, `/zones/`, `/cultures/`, `/missions/` retournent un **tableau brut**.

**Créer un arrosage manuel** :

```json
POST /api/v1/irrigations/
{"zone": 3, "duree_secondes": 20}
```

Réponse `201` si OK, `403` avec le code `arrosage_interdit` si la mesure est invalide, le robot injoignable ou une commande identique en cours.

### 8.5 Robot

Le robot s'authentifie avec un jeton statique dans l'en-tête **`X-Cle-Robot`** (valeur `CLE_ROBOT` du `.env`), pas avec un JWT.

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/api/v1/robot/mission-suivante/` | Prochaine mission planifiée (204 s'il n'y en a pas) |
| POST | `/api/v1/robot/messages/` | Envoyer un message (mesure, état, incident) |

Un **seul** endpoint `POST /robot/messages/` accepte les 3 types de messages, distingués par le champ `type`. Format détaillé dans `docs/protocole-communication.md`. Réponse `deja_recu: true` si le `message_id` a déjà été traité (anti-doublon, RG10).

Valeurs d'énumération vérifiées :

- `type` : `mesure`, `etat`, `incident`
- `etat` : `en_cours`, `terminee`, `interrompue`
- `type_incident` : `obstacle`, `capteur_defaillant`, `perte_communication`, `mesure_invalide`

### 8.6 Règles générales

- **Format des décimaux** : les valeurs `Decimal` (`superficie`, `humidite_minimum`, `valeur_humidite`, `volume_ml`...) sont renvoyées **sous forme de texte** (`"500.00"`). Les convertir côté frontend (`Number(...)`).
- **Statuts et dates de mission** : gérés par le serveur. Le frontend n'envoie jamais `statut`, `date_creation`, `date_debut`, `date_fin`.
- **Format d'erreur** : trois formats coexistent, normalisés côté frontend :
  - `{ erreur: { code, message, details } }` : exceptions métier (code en minuscules)
  - `{ detail: "..." }` : erreurs DRF standard (401, 403, 404, 409)
  - `{ champ: ["message", ...] }` : erreurs de validation DRF (400)
- **Filtrage par rôle** : `administrateur` voit toutes les ressources ; `proprietaire` voit uniquement ses parcelles, zones, missions, mesures, décisions, irrigations, incidents. Le filtrage est fait dans `get_queryset()` de chaque ViewSet.
- **CORS** : `django-cors-headers` autorise uniquement l'origine du frontend (`http://localhost:5173` en développement).

---

## 9. Documentation interactive

Le schéma OpenAPI est généré automatiquement par `drf-spectacular` :

| URL | Contenu |
|---|---|
| `/api/schema/` | Schéma OpenAPI brut (YAML) |
| `/api/docs/` | Swagger UI : permet de tester les endpoints avec un jeton `Bearer` |
| `/api/redoc/` | ReDoc : documentation lisible, organisée par tags |

Pour régénérer le fichier en local (utile pour valider ou versionner le schéma) :

```powershell
python manage.py spectacular --validate --file openapi-schema.yaml
```

---

## 10. Règles de gestion appliquées

| Règle | Où elle est appliquée |
|---|---|
| Humidité entre 0 et 100, minimum inférieur au maximum (zone) | Base de données (`CHECK`) et serializer des zones |
| Une mission comporte au moins une étape (RG5) | Serializer des missions |
| La zone d'une étape appartient à la parcelle de la mission (RG5) | Serializer des missions |
| Numéro d'ordre des étapes unique dans une mission | Base de données et serializer |
| Un statut de mission ne change que par les actions autorisées | Vue des missions (`409` sinon) |
| Anti-doublon sur `message_id` | Clé primaire de `Message` + `IntegrityError` dans `handlers` |
| Un utilisateur ne voit que ses ressources | `get_queryset()` filtré dans chaque ViewSet |
| Le robot doit porter `X-Cle-Robot` | Permission `EstRobot` |
| Une mesure invalide est enregistrée mais marquée `invalide` | `mesures/services.py` |
| Suppression refusée si des données en dépendent | `on_delete=PROTECT` (traçabilité) |

---

## 11. Tests

Les tests sont dans `tests/` et `apps/*/tests/`. Depuis `backend/` :

```powershell
pytest                    # tous les tests
pytest -v                 # avec le nom de chaque test
pytest tests/missions     # un seul module
pytest apps/irrigation/tests/
```

Pytest crée une base `test_roboagri` temporaire : les vraies données ne sont jamais touchées.
**Règle d'équipe** : un module livré arrive avec ses tests, dans la même pull request.

---

## 12. Conventions

- Noms créés par l'équipe (variables, fonctions, classes, tables, champs, JSON, statuts) en **français sans accents**.
- Commentaires, documentation et messages de commit en **français**.
- Seuls les noms imposés par Django restent en anglais (`password`, `is_active`, `is_staff`...).
- Détail complet : `conventions.md` à la racine du dépôt.

---

## 13. Dépannage

| Message | Cause probable | Solution |
|---|---|---|
| `Cannot import 'apps.xxx'` | `name` incorrect dans `apps/xxx/apps.py` | Mettre `name = "apps.xxx"` |
| `No module named 'apps.core.contraintes'` | Fichier absent ou mal placé | Vérifier `apps/core/contraintes.py` et `apps/core/__init__.py` |
| `Dependency on app with no migrations` | Migrations non générées pour une app | `python manage.py makemigrations utilisateurs parcelles missions` |
| `InconsistentMigrationHistory` | Base migrée avec un ancien modèle utilisateur | Recréer la base (voir section 4) |
| `permission denied to create database` (Pytest) | Droit manquant | `ALTER USER roboagri CREATEDB;` |
| `405 Method Not Allowed` sur `/demarrer/` | Requête GET depuis le navigateur | Utiliser POST (`Invoke-RestMethod -Method Post -Uri ...`) |
| Le navigateur bloque les requêtes du frontend | CORS | Vérifier `CORS_ALLOWED_ORIGINS` dans `settings.py` |
| `401 Unauthorized` sur `/auth/moi/` | Jeton absent ou expiré | Se reconnecter ; vérifier `Authorization: Bearer <acces>` |
| `403 Forbidden` sur `PATCH /auth/moi/` | Jeton invalide | Se reconnecter pour obtenir un `acces` neuf |
| `RuntimeError: You called this URL via POST without trailing slash` | URL sans `/` final sur un POST | Ajouter le `/` (ex. `/robot/messages/`) |
| `FieldError: Cannot resolve keyword 'mission'` sur mesures | Mauvais chemin ORM | Le lien est `Mesure → Etape → Mission` : utiliser `etape__mission__utilisateur` |

---

## 14. Suite prévue

1. ~~Authentification (connexion par email, JWT)~~ : **fait**
2. ~~Modèles et API de `communication` et `mesures` (anti-doublon)~~ : **fait**
3. ~~Règle de décision d'irrigation et incidents~~ : **fait**
4. **Dashboard et rapports** : endpoint `/dashboard/synthese/` à créer (actuellement les agrégats sont calculés côté frontend)
5. **PATCH incidents** : marquer un incident comme traité (`traite`, `gravite` à ajouter au modèle)
6. **POST /auth/mot-de-passe/** : changement de mot de passe depuis l'interface
7. **Détection robot hors ligne** : commande qui passe les missions `en_cours` sans activité en `non_confirmee` + incident
8. **TimescaleDB effectif** pour les mesures (hypertable)
9. **Docker Compose** : même environnement pour toutes les machines
10. **MQTT** : squelette prévu, non branché

---

## 15. Historique des versions du document

| Version | Date | Changements |
|---|---|---|
| 2.0 | 18 novembre 2026 | Mise à jour complète : authentification JWT, API v1, Swagger et ReDoc, endpoints du robot (`X-Cle-Robot`, anti-doublon), état d'avancement, règles de gestion, dépannage, suite prévue |
| 1.0 | (date à compléter) | Première version : installation, configuration, base de données, structure |