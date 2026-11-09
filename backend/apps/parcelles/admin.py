"""Administration des parcelles : permet de saisir et vérifier les données de démonstration."""
from django.contrib import admin

from .models import Cultiver, Culture, Parcelle, Zone


class ZoneEnLigne(admin.TabularInline):
    """Affiche les zones directement dans la page d'une parcelle."""

    model = Zone
    extra = 1


@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    list_display = ("nom", "utilisateur", "superficie")
    inlines = [ZoneEnLigne]


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("nom", "parcelle", "humidite_minimum",
                    "humidite_maximum", "irrigation_auto_active")
    list_filter = ("parcelle", "irrigation_auto_active")


admin.site.register([Culture, Cultiver])