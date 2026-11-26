"""Routeur DRF personnalisé pour forcer les identifiants numériques."""
from rest_framework.routers import DefaultRouter

class IntRouter(DefaultRouter):
    """Comme DefaultRouter, mais les IDs dans l'URL sont des entiers."""
    lookup_value_regex = "[0-9]+"