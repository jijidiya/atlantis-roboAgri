# Nomenclature du matériel — RoboAgri-Kin « Atlantis »

Projet de Programmation III · L3 Sciences Informatiques · Université Catholique du Congo
Binôme D (robot, mobilité, tests et intégration)
Dernière mise à jour : 28/10/2026

## Principe

Cette nomenclature indique, pour chaque composant, sa fonction, sa quantité, son prix, son fournisseur et une solution de remplacement Les dépenses réellement payées sont suivies dans `budget.md`.

Les prix indiqués sont ceux **proposés par le fournisseur** : ils sont à confirmer avant l'achat. Une case vide signifie que l'information n'est pas encore connue.

## Légende des statuts

- **À acheter** : aucun prix reçu pour le moment.
- **Devis reçu** : prix proposé par un fournisseur, à confirmer avec le groupe.
- **Acheté** : paiement enregistré dans `budget.md`.

## Liste des composants

| N° | Composant | Fonction | Qté | Prix unitaire (USD) | Fournisseur | Solution de remplacement | Statut |
|---|---|---|---|---|---|---|---|
| 1 | Carte ESP32 DevKit | Cerveau du robot, communication Wi-Fi | 2 conseillé | 30 | Landry Motanda | Autre carte ESP32 compatible | Devis reçu |
| 2 | Câble USB de données | Programmer l'ESP32 | 1 |  |  |  | À acheter |
| 3 | Kit châssis 2 roues (2WD) | Corps, moteurs et roues | 1 | 20 | Landry Motanda | Châssis fabriqué en carton plume ou en plastique | Devis reçu |
| 4 | Module L298N | Commande des moteurs | 2 conseillé | 15 | Landry Motanda | Autre pont en H (par exemple L9110S) | Devis reçu |
| 5 | Capteur HC-SR04 | Détection des obstacles | 2 conseillé | 10 | Landry Motanda | Capteur à ultrasons équivalent | Devis reçu |
| 6 | Capteur d'humidité capacitif | Mesure de l'humidité du sol | 1 | 5 | Landry Motanda | Capteur résistif (moins durable) | Devis reçu |
| 7 | Servomoteur SG90 ou MG90S | Descend et remonte la sonde d'humidité | 2 conseillé | 10 | Landry Motanda | Autre micro-servomoteur | Devis reçu |
| 8 | Condensateur 470 à 1000 µF | Amortit les pics de courant du servomoteur | 1 à 2 |  |  | Récupération sur une carte électronique | À acheter |
| 9 | Piles 18650, support et chargeur | Alimentation des moteurs | 1 ensemble |  |  | Bloc de piles AA (6 V) | À acheter |
| 10 | Batterie externe (power bank) | Alimentation de l'ESP32 et du servomoteur | 1 |  |  | Batterie externe déjà disponible | À acheter |
| 11 | Interrupteur | Coupure de l'alimentation des moteurs | 1 |  |  |  | À acheter |
| 12 | Breadboard 830 points | Câblage sans soudure | 1 | 5 | Landry Motanda | Breadboard plus petite | Devis reçu |
| 13 | Fils Dupont (M-M, M-F, F-F) | Liaisons entre les composants | environ 40 de chaque | 5 | Landry Motanda |  | Devis reçu |
| 14 | Résistances 1 kΩ, 2 kΩ, 10 kΩ, 47 kΩ, 100 kΩ | Diviseurs de tension | 10 de chaque | 5 | Landry Motanda |  | Devis reçu |
| 15 | Fil électrique souple rouge et noir | Rallonges des moteurs et de la batterie | 2 à 3 m |  |  | Fil récupéré sur un ancien câble | À acheter |
| 16 | Double face et colliers de serrage | Fixation et rangement des composants | 1 lot |  |  |  | À acheter |
| 17 | Matériel de la coque (bol, carton plume, peinture, colle chaude, velcro, autocollants, tige du bras) | Habillage de la coccinelle et bras du servomoteur | 1 lot |  |  | Matériaux de récupération | À acheter |

## Outils (hors composants du robot)

| Outil | Usage | Prix (USD) | Fournisseur |
|---|---|---|---|
| Fer à souder | Souder les fils (support de piles, moteurs) | 15 | Landry Motanda |
| Multimètre | Vérifier les tensions avant de brancher |  |  |

## Remarques

- La version minimale du projet ne comprend pas de pompe à eau : aucune ligne n'est prévue pour ce poste.
- Les composants numérotés 1 à 11 sont prioritaires. Le matériel de la coque (n° 17) sera acheté après les tests du montage.
- Le schéma de câblage sera placé dans ce même dossier.
