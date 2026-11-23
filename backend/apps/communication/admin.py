from django.contrib import admin
from .models import Message

"""Admin de l'application « communication »."""
from django.contrib import admin

from .models import MessageRecu


@admin.register(MessageRecu)
class MessageRecuAdmin(admin.ModelAdmin):
    list_display = ("message_id", "type_message", "mission", "num_sequence", "date_heure")
    list_filter = ("type_message", "date_heure")
    search_fields = ("message_id", "mission__mission_id")
    readonly_fields = (
        "message_id", "num_sequence", "type_message",
        "contenu", "date_heure", "mission",
    )
    date_hierarchy = "date_heure"

    def has_add_permission(self, request):
        # Les messages viennent du robot, pas de l'admin.
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Message)