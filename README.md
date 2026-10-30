# RoboAgri-Kin

Robot mobile à faible coût qui mesure l'humidité du sol dans plusieurs zones d'une parcelle et transmet les données à une application de gestion pour faciliter les décisions d'irrigation.

Projet de Programmation III, L3 Sciences Informatiques, Université Catholique du Congo (2026-2027).

## Architecture

| Composant | Technologie |
|---|---|
| Robot | ESP32, MicroPython, L298N, HC-SR04, capteur d'humidité capacitif |
| Backend | Django + Django REST Framework |
| Base de données | PostgreSQL + TimescaleDB (mesures) |
| Frontend | React + Vite, Leaflet, Plotly/Recharts |
| Communication | HTTP sur Wi-Fi (MQTT prévu ensuite) |
| Tests | Pytest |
| Conteneurs | Docker / docker-compose |

## Structure du dépôt

```
backend/    API Django + DRF
frontend/   Application React
firmware/   Programme de l'ESP32
docs/       Cahier des charges, UML, rapport, schémas de câblage
tests/      Tests d'intégration et protocole d'essais
```

## Démarrage rapide

```bash
git clone <url-du-depot>
cd <nom-du-depot>
cp .env.example .env      # puis adapter les valeurs
docker-compose up --build
```

- API : http://localhost:8000
- Frontend : http://localhost:5173

> Les instructions détaillées seront dans `docs/manuel-installation.md`.

## Équipe

| Binôme | Membres | Responsabilités |
|---|---|---|
| A | Junior & Esther | Coordination, documentation, spécifications |
| B | Sabin &  | Données, API, étalonnage |
| C | Magnificat & | Interface, missions, tableau de bord |
| D | Bramcy & Astride  | Robot, mobilité, tests d'intégration |
| E | Danella & Messie | Capteurs, décision, communication |
| B | Sabin & Gabriel | Données, API, étalonnage |
| C | Magnificat & Jeanine | Interface, missions, tableau de bord |
| D |  Bramcy &  | Robot, mobilité, tests d'intégration |
| E |  Danella & Messie. | Capteurs, décision, communication |

## Avancement

Voir l'onglet **Projects** du dépôt.

## Contribuer

Lire [CONTRIBUTING.md](CONTRIBUTING.md) avant toute modification.