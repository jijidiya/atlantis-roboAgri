# RoboAgri-Kin : frontend

Interface React de l'application RoboAgri-Kin : parcelles, missions, mesures d'humidité, irrigation (recommandations), incidents, historique et rapports.

## Prérequis

- Node.js (version LTS) et npm
- Le backend Django lancé sur `http://127.0.0.1:8000` (voir `backend/README.md`)

## Installation et lancement

Depuis la racine du dépôt, commandes séparées :

```powershell
cd frontend
npm install
npm run dev
```

L'application s'ouvre sur `http://localhost:5173`.
Penser à refaire `npm install` après chaque `git pull` qui modifie `package.json`.

Sous Windows, si PowerShell bloque `npm` :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Connexion

Charger d'abord les données de démo côté backend (`python donnees_demo.py`), puis se connecter avec un compte `@demo.roboagri.cd`. Les identifiants de démo sont dans `backend/donnees_demo.py`.

## Adresse de l'API

L'adresse de base vient de la variable `VITE_API_URL` (voir `src/api/config.js`). Les fichiers `.env` ne sont jamais commités.

## Organisation de `src/`

| Dossier | Rôle |
|---|---|
| `pages/` | Un écran par page (Missions, Irrigation, Incidents, etc.) |
| `components/` | Éléments réutilisables (Layout, StatCard, StatusBadge, EtatVide, Toggle) |
| `hooks/` | Un hook TanStack Query par ressource (`useMissions`, `useMesures`, etc.) |
| `api/` | Communication avec le backend (`http.js` gère le token et le renouvellement après un 401) |
| `utils/` | Fonctions utilitaires (`formatage.js`) |

Chemin d'une donnée : **page → hook → `api/http.js` → backend Django**.

## Principe d'honnêteté

L'interface n'affiche que ce que le backend fournit réellement. Aucune valeur inventée.