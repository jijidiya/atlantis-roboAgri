from django.contrib import admin

from .models import Culture, Cultiver, Parcelle, Zone

admin.site.register([Parcelle, Zone, Culture, Cultiver])
