# RoboAgri-Kin : backend

API et application de gestion du projet **RoboAgri-Kin** (Projet de Programmation III, L3 Sciences Informatiques, UCC).
Le backend gère les parcelles, les zones, les cultures et les missions du robot, et conservera les mesures d'humidité du sol, les décisions d'irrigation et les incidents.

- **Technologies** : Python, Django, Django REST Framework, PostgreSQL (TimescaleDB prévu pour les mesures), Pytest.
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
Copie le modèle puis adapte les valeurs :

```powershell
Copy-Item .env.example .env
```

Contenu de `.env.example` :

```
DEBUG=True
SECRET_KEY=change-moi-par-une-longue-chaine-aleatoire
BASE_NOM=roboagri
BASE_UTILISATEUR=roboagri
BASE_MOT_DE_PASSE=roboagri
BASE_HOTE=localhost
BASE_PORT=5432
```

Pour générer une vraie `SECRET_KEY` :

```powershell
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

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
| http://127.0.0.1:8000/api/parcelles/ | API des parcelles (page de test DRF) |
| http://127.0.0.1:8000/api/missions/ | API des missions |

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
    core/                    # outils communs (contraintes de base de données)
    utilisateurs/            # UTILISATEUR (modèle utilisateur personnalisé)
    parcelles/               # PARCELLE, ZONE, CULTURE, CULTIVER
    missions/                # MISSION, ETAPE
    communication/           # MESSAGE (à venir)
    mesures/                 # MESURE (à venir)
    analyse/                 # ANALYSE (à venir)
    incidents/               # INCIDENT (à venir)
    irrigation/              # DECISION, IRRIGATION (à venir)
    dashboard/               # tableau de bord et rapports (à venir)
  tests/                   # tous les tests, un sous-dossier par module
```

Chaque application suit le même schéma : `models.py`, `admin.py`, `serializers.py`, `views.py`, `urls.py`.
Un module ne dépend que des modules plus « bas » dans cet ordre :
`utilisateurs` → `parcelles` → `missions` → `communication` / `mesures` → `analyse` → `irrigation`.
Pour éviter les imports circulaires, les clés étrangères vers une autre application s'écrivent par chaîne : `"parcelles.Zone"`.

---

## 7. État d'avancement

| Module | Modèles | API | Tests |
|---|---|---|---|
| utilisateurs | fait | à faire (authentification) | à faire |
| parcelles | fait | fait | fait |
| missions | fait | fait | fait |
| communication | à faire | à faire | à faire |
| mesures | à faire | à faire | à faire |
| analyse | à faire | à faire | à faire |
| incidents | à faire | à faire | à faire |
| irrigation (décision) | à faire | à faire | à faire |
| dashboard | sans modèle | à faire | à faire |

> Les fonctionnalités non réalisées sont signalées ici, comme l'exige le sujet.

---

## 8. API (résumé)

Format JSON, adresses terminées par `/`. Détail complet : `docs/api-frontend-backend.md`.

### Parcelles, zones, cultures

| Méthode | URL | Rôle |
|---|---|---|
| GET, POST | `/api/parcelles/` | Lister, créer (avec leurs zones en lecture) |
| GET, PUT, PATCH | `/api/parcelles/{id}/` | Consulter, modifier |
| GET, POST | `/api/zones/?parcelle={id}` | Lister (filtre facultatif), créer |
| GET, PUT, PATCH | `/api/zones/{id}/` | Consulter, modifier |
| GET, POST | `/api/cultures/` | Lister, créer |

### Missions

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/api/missions/?parcelle={id}&statut={statut}` | Lister (filtres facultatifs) |
| POST | `/api/missions/` | Créer une mission avec ses étapes |
| GET | `/api/missions/{id}/` | Consulter (avec étapes) |
| POST | `/api/missions/{id}/demarrer/` | `planifiee` → `en_cours` |
| POST | `/api/missions/{id}/terminer/` | `en_cours` → `terminee` |
| POST | `/api/missions/{id}/interrompre/` | `en_cours` → `interrompue` |

Exemple de création d'une mission :

```json
{
  "utilisateur": 1,
  "parcelle": 1,
  "etapes": [
    {"numero_ordre": 1, "zone": 1},
    {"numero_ordre": 2, "zone": 2}
  ]
}
```

Codes de réponse : `201` créé, `400` données invalides, `409` changement de statut interdit.

Points à connaître :
- les décimaux (`superficie`, `humidite_minimum`...) sont renvoyés **sous forme de texte** (`"500.00"`) : les convertir côté frontend ;
- le statut et les dates d'une mission sont gérés par le serveur, le frontend ne les envoie pas ;
- l'API est **ouverte** (`AllowAny`) pour l'instant : l'authentification est à mettre en place avant la démonstration finale.

---

## 9. Règles de gestion appliquées

| Règle | Où elle est appliquée |
|---|---|
| Humidité entre 0 et 100, minimum inférieur au maximum (zone) | Base de données (`CHECK`) et serializer des zones |
| Une mission comporte au moins une étape (RG5) | Serializer des missions |
| La zone d'une étape appartient à la parcelle de la mission (RG5) | Serializer des missions (la base ne peut pas la contrôler) |
| Numéro d'ordre des étapes unique dans une mission | Base de données (contrainte d'unicité) et serializer |
| Un statut de mission ne change que par les actions autorisées | Vue des missions (`409` sinon) |
| Suppression refusée si des données en dépendent | `on_delete=PROTECT` (traçabilité) |

---

## 10. Tests

Les tests sont dans `tests/`, un sous-dossier par module. Depuis `backend/` :

```powershell
pytest                    # tous les tests
pytest -v                 # avec le nom de chaque test
pytest tests/missions     # un seul module
```

Pytest crée une base `test_roboagri` temporaire : les vraies données ne sont jamais touchées.
**Règle d'équipe** : un module livré arrive avec ses tests, dans la même pull request.

---

## 11. Conventions

- Noms créés par l'équipe (variables, fonctions, classes, tables, champs, JSON, statuts) en **français sans accents**.
- Commentaires, documentation et messages de commit en **français**.
- Seuls les noms imposés par Django restent en anglais (`password`, `is_active`, `is_staff`...).
- Détail complet : `conventions.md` à la racine du dépôt.

---

## 12. Dépannage

| Message | Cause probable | Solution |
|---|---|---|
| `Cannot import 'apps.xxx'` | `name` incorrect dans `apps/xxx/apps.py` | Mettre `name = "apps.xxx"` |
| `No module named 'apps.core.contraintes'` | Fichier absent ou mal placé | Vérifier `apps/core/contraintes.py` et `apps/core/__init__.py` |
| `Dependency on app with no migrations` | Migrations non générées pour une app | `python manage.py makemigrations utilisateurs parcelles missions` |
| `InconsistentMigrationHistory` | Base migrée avec un ancien modèle utilisateur | Recréer la base (voir section 4) |
| `permission denied to create database` (Pytest) | Droit manquant | `ALTER USER roboagri CREATEDB;` |
| `405 Method Not Allowed` sur `/demarrer/` | Requête GET depuis le navigateur | Utiliser POST (`Invoke-RestMethod -Method Post -Uri ...`) |
| Le navigateur bloque les requêtes du frontend | CORS | Vérifier `CORS_ALLOWED_ORIGINS` dans `settings.py` |

---

## 13. Suite prévue

1. Authentification (connexion par email, jeton) et protection de l'API.
2. Modèles et API de `communication` et `mesures` (anti-doublon sur `message_id`).
3. Règle de décision d'irrigation et incidents.
4. TimescaleDB pour la table des mesures, Docker, puis MQTT.