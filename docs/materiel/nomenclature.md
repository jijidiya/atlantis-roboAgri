# Nomenclature du matériel — RoboAgri-Kin « Atlantis »

Projet de Programmation III · L3 Sciences Informatiques · Université Catholique du Congo
Binôme D (robot, mobilité, tests et intégration)
Dernière mise à jour : 09/11/2026

## Principe

Cette nomenclature indique, pour chaque composant, sa fonction, sa quantité, son prix, son fournisseur et une solution de remplacement. Les dépenses réellement payées sont suivies dans `budget.md`.

Les prix indiqués sont ceux **proposés par le fournisseur** : ils sont à confirmer avant l'achat. Une case vide signifie que l'information n'est pas encore connue.

## Légende des statuts

- **À acheter** : aucun prix reçu pour le moment.
- **Devis reçu** : prix proposé par un fournisseur, à confirmer avec le groupe.
- **Acheté** : paiement enregistré dans `budget.md`.

## Liste des composants

| N° | Composant | Fonction | Qté | Prix unitaire (USD) | Fournisseur | Solution de remplacement | Statut |
|---|---|---|---|---|---|---|---|
| 1 | Carte ESP32 DevKit | Cerveau du robot, communication Wi-Fi | 2  | 30 | Landry Motanda | Autre carte ESP32 compatible | Acheté |
| 2 | Câble USB de données | Programmer l'ESP32 | 1 | 2.17 | ADK Shop |  | Acheté |
| 3 | Kit châssis 2 roues (2WD) | Corps, moteurs et roues | 1 | 20 | Landry Motanda | Châssis fabriqué en carton plume ou en plastique | Acheté |
| 4 | Module L298N | Commande des moteurs | 2  | 15 | Landry Motanda | Autre pont en H (par exemple L9110S) | Acheté |
| 5 | Capteur HC-SR04 | Détection des obstacles | 2  | 10 | Landry Motanda | Capteur à ultrasons équivalent | Acheté |
| 6 | Capteur d'humidité capacitif | Mesure de l'humidité du sol | 2 | 10 | Landry Motanda | Capteur résistif (moins durable) | Acheté |
| 7 | Servomoteur SG90 ou MG90S | Descend et remonte la sonde d'humidité | 2  | 10 | Landry Motanda | Autre micro-servomoteur | Acheté |
| 8 | Condensateur 470 à 1000 µF | Amortit les pics de courant du servomoteur | 2 | 1.74 | ADK Shop | Récupération sur une carte électronique | Acheté |
| 9 | Piles 18650, support et chargeur | Alimentation des moteurs | 1 ensemble | 2.61 | ADK shop | Bloc de piles AA (6 V) | Acheté |
| 10 | Batterie externe (power bank) | Alimentation de l'ESP32 et du servomoteur | 1 |  |  | Batterie externe déjà disponible | À acheter |
| 11 | Interrupteur | Coupure de l'alimentation des moteurs | 1 | 3.5 | Landry Motanda |  | Acheté |
| 12 | Breadboard 830 points | Câblage sans soudure | 1 | 5 | Landry Motanda | Breadboard plus petite | Acheté |
| 13 | Fils Dupont (M-M, M-F, F-F) | Liaisons entre les composants | environ 40 de chaque | 13 | Landry Motanda |  | Acheté |
| 14 | Résistances 1 kΩ, 2 kΩ, 10 kΩ, 47 kΩ, 100 kΩ | Diviseurs de tension | 10 de chaque | 5 | Landry Motanda |  | Acheté |
| 15 | Fil électrique souple rouge et noir | Rallonges des moteurs et de la batterie | 2 à 3 m |  |  | Fil récupéré sur un ancien câble | À acheter |
| 16 | Double face et colliers de serrage | Fixation et rangement des composants | 1 lot |  |  |  | À acheter |


## Outils (hors composants du robot)

| Outil | Usage | Prix (USD) | Fournisseur | Statut |
|---|---|---|---|---|
| Fer à souder | Souder les fils (support de piles, moteurs) | 15 | Landry Motanda | Devis reçu |
| Multimètre | Vérifier les tensions avant de brancher | 3.39 | Galerie chinois Matadi-Kibala | Acheté |

## Remarques

- La version minimale du projet ne comprend pas de pompe à eau : aucune ligne n'est prévue pour ce poste.
- Le schéma de câblage sera placé dans ce même dossier.
