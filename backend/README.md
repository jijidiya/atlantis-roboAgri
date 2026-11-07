# RoboAgri-Kin : backend

API Django (DRF) reliée à une base PostgreSQL avec l'extension TimescaleDB.

## Prérequis

- Python 3.11 ou plus récent
- PostgreSQL 15+ avec l'extension **TimescaleDB**, ou Docker Desktop (au choix, voir ci-dessous)
- Git

## 1. Installation

```bash
cd backend
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## 2. Configuration (`.env`)

Les réglages sont lus dans `backend/.env`. Ce fichier n'est **jamais** commité.

```bash
cp .env.example .env          # Windows PowerShell : Copy-Item .env.example .env
```

Puis ouvrir `.env` et renseigner au minimum `DB_PASSWORD` et `DJANGO_SECRET_KEY`.
La base s'appelle `wall-eDB` (variable `DB_NAME`).

## 3. Base de données

### Option A : la base existe déjà (cas actuel)

La base `wall-eDB` est créée et l'extension TimescaleDB est activée. Il suffit de
renseigner `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` dans `.env`.

Pour vérifier l'extension :

```bash
psql -U postgres -d "wall-eDB" -c "\dx timescaledb"
```

Si elle est absente, une seule fois, en superutilisateur :

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### Option B : créer la base avec Docker

```bash
docker compose up -d      # démarre PostgreSQL + TimescaleDB
docker compose ps         # attendre l'état "healthy"
```

- Les données sont dans le volume persistant `donnees_db` : elles survivent à
  `docker compose down`. Pour **tout effacer** : `docker compose down -v`.
- L'extension est activée à la première création par
  `docker/init/01-timescaledb.sql`. Ce script ne se rejoue pas sur un volume
  existant.

## 4. Démarrer le projet

```bash
python manage.py migrate
python manage.py loaddata parcelles_demo missions_demo mesures_demo irrigation_demo
python manage.py runserver
```

- API : <http://127.0.0.1:8000/api/>
- Administration : <http://127.0.0.1:8000/admin/> (après `python manage.py createsuperuser`)

Si `migrate` réussit, le projet est bien connecté à la base.

## 4 bis. Jeton du robot

Le robot s'authentifie avec un jeton (`Authorization: Token <jeton>`, docs/protocole.md).

```bash
python manage.py createsuperuser
python manage.py drf_create_token <nom_utilisateur>
```

Points d'entrée du robot : `GET /api/robot/mission`, `POST /api/robot/messages`,
`POST /api/robot/messages/sync`, `POST /api/robot/etat`.

Détection des missions non confirmées (à lancer toutes les 3 s en production) :

```bash
python manage.py detecter_missions_non_confirmees
```

## 5. Tests

```bash
python -m pytest
```

Les tests utilisent SQLite en mémoire (aucun serveur requis). Pour les lancer sur
PostgreSQL (le rôle doit pouvoir créer des bases) :

```bash
python -m pytest --ds=config.settings.dev
```

### Style du code

```bash
black .
ruff check .
```

## Problèmes fréquents sous Windows

| Symptôme | Cause et solution |
|---|---|
| `l'exécution de scripts est désactivée` à l'activation du venv | Dans PowerShell : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, ou utiliser `cmd` avec `.venv\Scripts\activate.bat`. |
| `python` ouvre le Microsoft Store | Utiliser `py -m venv .venv`, ou désactiver l'alias dans *Paramètres > Applications > Alias d'exécution*. |
| `pip install psycopg` échoue (compilation) | Le projet utilise `psycopg[binary]` qui n'a pas besoin de compilateur. Mettre pip à jour : `python -m pip install -U pip`. |
| `connection refused` sur le port 5432 | PostgreSQL ou le conteneur n'est pas démarré, ou `DB_HOST`/`DB_PORT` est faux. Vérifier avec `docker compose ps`. |
| Le port 5432 est déjà utilisé | Un PostgreSQL local tourne déjà. Changer `DB_PORT` (ex. `5433`) dans `.env`, puis `docker compose up -d`. |
| `database "wall-edb" does not exist` | Le nom contient une majuscule et un tiret : il est sensible à la casse. Garder exactement `wall-eDB` et, dans `psql`, les guillemets : `-d "wall-eDB"`. |
| `password authentication failed` | `DB_USER`/`DB_PASSWORD` ne correspondent pas à ceux de la base. Si le volume Docker existe déjà, le mot de passe d'origine reste : `docker compose down -v` puis `up -d` (efface les données). |
| Caractères bizarres en lisant `.env` | Enregistrer `.env` en **UTF-8**. Le projet tolère le BOM, mais pas l'UTF-16 (défaut de certains éditeurs). |
| `docker compose` : « the input device is not a TTY » ou le script SQL ignoré | Fins de ligne CRLF dans `docker/init/*.sql`. Le `.gitattributes` force LF ; refaire `git checkout -- docker/init`. |
| Docker Desktop ne démarre pas | Activer la virtualisation dans le BIOS et WSL 2 (`wsl --install`). |
| `.env` créé en `.env.txt` | Activer l'affichage des extensions de fichiers dans l'Explorateur, ou utiliser `Copy-Item .env.example .env`. |

## Architecture

Voir `architecture.pdf` : une application Django par module (`parcelles`, `missions`,
`mesures`, `irrigation`, `dashboard`, `communication`), dépendances uniquement vers le bas.
