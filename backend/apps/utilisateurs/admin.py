"""Configuration de l'interface d'administration Django pour les utilisateurs."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    """Affichage et formulaires adaptés à notre modèle (email au lieu de username)."""

    ordering = ("email",)
    list_display = ("email", "nom", "prenom", "role", "actif")
    list_filter = ("role", "actif")
    search_fields = ("email", "nom", "prenom")
    filter_horizontal = ()  # pas de groupes ni de permissions détaillées pour l'instant

    # Formulaire de modification d'un utilisateur existant.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identité", {"fields": ("nom", "prenom", "role", "actif")}),
    )
    # Formulaire de création : demande le mot de passe deux fois.
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nom", "prenom", "role", "actif",
                       "password1", "password2"),
        }),
    )