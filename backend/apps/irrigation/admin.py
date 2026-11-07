from django.contrib import admin

from .models import Incident, Irrigation

admin.site.register([Irrigation, Incident])
