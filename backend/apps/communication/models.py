from django.db import models


class MessageRecu(models.Model):
    """Trace de chaque message du robot. L'unicité est garantie par la base."""

    identifiant = models.CharField(max_length=64, unique=True)
    contenu = models.JSONField()
    recu_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recu_le"]
