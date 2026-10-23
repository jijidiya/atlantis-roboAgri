# Atelier Git : branches, Pull Requests et conflits
 
**Pourquoi cet atelier ?** Nos contributions individuelles sont évaluées à partir de l'historique Git. Chacun doit donc savoir travailler avec des branches et des Pull Requests.
 
**Objectif :** chaque membre réussit le cycle complet une fois, avec son propre compte GitHub.
 
## Comment ça se passe
 
- Quelques membres font le cycle en direct, et les autres suivent.
- Les membres sans PC sur place refont l'atelier chez eux ou plus tard dans la journée, avec la section « Faire l'atelier chez soi ».
- **Date limite pour que chacun ait sa PR ouverte : 30/10/2026.**
## Prérequis
 
- Un compte GitHub personnel
- Git installé (vérifier avec `git --version`)
- Git configuré
- Invitation au dépôt acceptée
## Les 3 notions à savoir expliquer à l'oral
 
- **Branche** : une copie parallèle du projet où l'on travaille sans toucher à `main`.
- **Pull Request (PR)** : une demande pour intégrer sa branche dans `main`, avec relecture par un autre membre avant la fusion.
- **Conflit** : deux personnes modifient la même ligne, et Git ne sait pas laquelle garder. C'est à nous de choisir.
## Faire l'atelier chez soi
 
1. Configurer son identité (même email que celui de GitHub) :
```bash
   git config --global user.name "Prénom Nom"
   git config --global user.email "email@github.com"
```
 
2. Cloner le dépôt :
```bash
   git clone <url-du-depot>
   cd .\atlantis-roboAgri
```
 
3. Créer sa branche :
```bash
   git checkout -b docs/presentation-<prenom>
```
 
4. Ajouter son nom et son binôme dans la section « Équipe » du README.
5. Commit, avec un message conforme à `CONTRIBUTING.md` :
```bash
   git add README.md
   git commit -m "<message au format CONTRIBUTING.md>"
```
 
6. Pousser :
```bash
   git push -u origin docs/presentation-<prenom>
```
 
7. Ouvrir la PR sur GitHub (bouton « Compare & pull request ») avec un titre explicite.
## Relire la PR d'un autre binôme
 
Vérifier le nom de la branche, le message de commit et le contenu modifié, puis cliquer sur *Approve*. La relecture est faite par un membre d'un **autre** binôme.
 
## Exercice du conflit
 
1. Les deux membres d'un binôme partent de `main` à jour et créent chacun une branche.
2. Ils modifient **la même ligne** [ligne à préciser].
3. Le premier fusionne sa PR. Le second reçoit alors un conflit.
4. Pour le résoudre :
```bash
   git pull origin main
```
 
   Ouvrir le fichier et repérer les marqueurs :
 
```
   <<<<<<< HEAD
   ta version
   =======
   la version de l'autre
   >>>>>>> main
```
 
   Garder la bonne version, supprimer les marqueurs, puis :
 
```bash
   git add <fichier>
   git commit
   git push
```
 
## Règles d'or
 
- **Aucun push direct sur `main`.**
- Nom de branche : `docs/presentation-<prenom>`
- Messages de commit : voir `CONTRIBUTING.md`
- Une PR = un objectif clair, avec un titre explicite.
## Problèmes fréquents
 
- **Ma contribution n'apparaît pas sur mon profil** : l'email Git est différent de celui du compte GitHub.
- **Push refusé sur `main`** : normal, crée une branche et passe par une PR.
- **J'ai modifié avant de créer ma branche** : `git checkout -b <ma-branche>` emporte les modifications avec toi.
- **Authentification refusée** : utiliser un *Personal Access Token* à la place du mot de passe, ou une clé SSH.
## Critères d'acceptation
 
- [ ] Les 10 membres apparaissent comme contributeurs
- [ ] Aucun push direct sur `main`
- [ ] Chacun sait expliquer branche, PR et conflit
**Contact en cas de blocage : @jijidiya.**
                        