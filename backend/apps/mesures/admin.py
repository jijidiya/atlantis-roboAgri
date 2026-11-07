"""Administration des mesures."""

from django.contrib import admin

from .models import MesureHumidite

admin.site.register(MesureHumidite)
