from django.contrib import admin

from .models import EtapeMission, Mission

admin.site.register([Mission, EtapeMission])
