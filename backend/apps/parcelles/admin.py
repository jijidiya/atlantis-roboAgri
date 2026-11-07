from django.contrib import admin

from .models import Cultiver, Culture, Parcelle, Zone

admin.site.register([Parcelle, Zone, Culture, Cultiver])
