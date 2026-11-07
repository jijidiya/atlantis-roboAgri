"""Commande à lancer régulièrement : détecte les missions non confirmées."""

from django.core.management.base import BaseCommand

from apps.communication.handlers import detecter_missions_non_confirmees


class Command(BaseCommand):
    """Applique la règle du silence et du plafond (docs/protocole.md, 6.6)."""

    help = "Passe à « non_confirmee » les missions dont le robot est silencieux."

    def handle(self, *args, **options):
        changements = detecter_missions_non_confirmees()
        for mission, cause in changements:
            self.stdout.write(f"Mission {mission.id} non confirmée (cause : {cause})")
        self.stdout.write(f"{len(changements)} mission(s) passée(s) à non_confirmee.")
