# Guide de contribution

## Règles d'or
1. **Jamais de push direct sur `main`.** Tout passe par une Pull Request.
2. **Chaque personne commit avec son propre compte GitHub.** Nos contributions individuelles sont évaluées à partir de l'historique Git.
3. **Jamais de secret dans le dépôt** (mots de passe, tokens, identifiants Wi-Fi). Utiliser `.env` et `firmware/secrets.py`, qui sont ignorés par Git.
4. Ce qui est commité doit fonctionner : tester avant de pousser.

## Configuration Git (une seule fois)
    git config --global user.name "Prénom Nom"
    git config --global user.email "email-utilise-sur-github"

## Branches
Créer une branche depuis `main` à jour :

    git checkout main
    git pull
    git checkout -b <type>/<description-courte>

Types : `feature/`, `fix/`, `docs/`, `test/`, `chore/`
Exemples : `feature/api-mesures`, `fix/calibration-capteur`, `docs/diagramme-classes`

## Commits
Format : `type: message court à l'impératif`

    feat: ajoute l'endpoint de réception des mesures
    fix: corrige l'association mesure-zone
    docs: complète le cahier des charges
    test: ajoute les tests de la règle d'irrigation

Petits commits, fréquents, un sujet par commit.

## Pull Requests
1. Pousser sa branche : `git push -u origin <branche>`
2. Ouvrir la PR sur GitHub avec une description claire.
3. **Demander la relecture d'un membre d'un autre binôme.**
4. Corriger selon les commentaires.
5. Une fois approuvée, le relecteur ou l'auteur fait le merge.
6. Supprimer la branche après merge.

Une PR doit rester petite et lisible : une fonctionnalité ou un correctif à la fois.

## Revue de code
- Relire le code comme si on devait l'expliquer à la soutenance.
- Être précis et bienveillant dans les commentaires.
- Approuver seulement si on a compris ce que fait le code.

## Suivi du travail
- Chaque tâche = une **Issue**, avec le label de son binôme et un milestone.
- Lier la PR à l'issue (`Closes #12` dans la description).

## Usage de l'IA
Tout usage d'outils d'IA doit être déclaré selon les consignes de l'enseignant. Chacun doit comprendre et savoir défendre le code qu'il pousse.