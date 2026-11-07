"""Réglages des tests : SQLite en mémoire, donc aucun serveur PostgreSQL requis.

Pour tester sur PostgreSQL (le rôle doit avoir le droit CREATEDB) :
    python -m pytest --ds=config.settings.dev
"""

from .dev import *  # noqa: F401,F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
