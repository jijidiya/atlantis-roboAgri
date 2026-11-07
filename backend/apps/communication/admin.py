from django.contrib import admin

from .models import EtatRobot, MessageRecu

admin.site.register([MessageRecu, EtatRobot])
