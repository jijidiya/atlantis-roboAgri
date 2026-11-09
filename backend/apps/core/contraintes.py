"""Contraintes de base de données réutilisables par plusieurs applications.

Ce module évite de répéter la même contrainte (par exemple « entre 0 et 100 »)
dans chaque modèle. Les contraintes sont appliquées par PostgreSQL lui-même :
une valeur invalide est refusée même si elle n'est pas passée par Django.
"""
from django.db import models
from django.db.models import Q


def entre_0_et_100(champ, nom):
    """Crée une contrainte CHECK imposant 0 <= champ <= 100.

    Sert aux pourcentages d'humidité (MPD : NUMERIC(5,2) CHECK entre 0 et 100).

    Arguments :
        champ : nom du champ du modèle à contrôler (ex. "humidite_minimum").
        nom : nom unique de la contrainte dans la base de données.
    """
    return models.CheckConstraint(
        condition=Q(**{f"{champ}__gte": 0, f"{champ}__lte": 100}),
        name=nom,
    )