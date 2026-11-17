# Choix des composants confirmés — RoboAgri-Kin « Atlantis »

Projet de Programmation III · L3 Sciences Informatiques · Université Catholique du Congo
Binôme D (robot, mobilité, tests et intégration)



## Principe

Ce document confirme les composants retenus pour le robot et justifie chaque choix. Les prix, les quantités et les fournisseurs se trouvent dans `nomenclature.md`. Les dépenses se trouvent dans `budget.md`.

## Composants confirmés

| Composant | Modèle retenu | Pourquoi ce choix | Solution de remplacement |
|---|---|---|---|
| Microcontrôleur | ESP32 DevKit (prise USB-C, 38 broches) | Wi-Fi intégré, peu coûteux, programmable en MicroPython | Autre carte ESP32 compatible |
| Commande des moteurs | Module L298N | L'ESP32 ne peut pas fournir le courant des moteurs. Le L298N donne le sens et la vitesse de chaque moteur | Autre pont en H (par exemple L9110S) |
| Détection des obstacles | Capteur HC-SR04 | Mesure la distance par ultrasons à faible coût (exigence RF04) | Capteur à ultrasons équivalent |
| Mesure de l'humidité | Capteur résistif à deux lames | Seul capteur d'humidité disponible pour la version minimale  | Capteur capacitif v1.2 (échange demandé au fournisseur) |
| Alimentation des moteurs | 4 piles AA alcalines (6 V) dans le support du kit | Support déjà fourni avec ses fils, aucune soudure nécessaire | 2 piles 18650 en série (7,4 V), avec chargeur |
| Alimentation de l'électronique | Batterie externe (power bank) en USB | Alimente l'ESP32, le servomoteur et les capteurs à part, pour que les moteurs ne la fassent pas redémarrer | Convertisseur abaisseur 5 V sur une batterie unique |
| Descente de la sonde | Servomoteur SG90 | Descend la sonde à l'arrêt et la remonte pendant le déplacement, pour la protéger | Autre micro-servomoteur |
| Protection du servomoteur | Condensateur de 470 à 1 000 µF | Absorbe les pics de courant du servomoteur | Condensateur de valeur proche |
| Coupure générale | Interrupteur à bascule | Coupe l'alimentation des moteurs en cas de problème | — |
| Câblage de l'ESP32 | Adaptateur à bornes à vis pour ESP32 | Option facultative: Les fils tiennent mieux avec une vis qu'avec une breadboard qui vibre | Breadboard et fils Dupont |
| Diviseurs de tension | Résistances de 2 kΩ, 47 kΩ et 100 kΩ | Adaptent l'écho du HC-SR04 (5 V vers 3,3 V) et mesurent la tension de la batterie | — |
| Châssis | Kit 2 roues (2WD) avec deux moteurs | Simple, peu coûteux, facile à réparer | Châssis fabriqué en carton plume |
