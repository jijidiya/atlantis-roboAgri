"""Modèles de l'application « utilisateurs » (table UTILISATEUR).

On remplace le modèle utilisateur de Django par le nôtre afin de respecter le
MPD (nom, prenom, role, actif, date_creation, mot_de_passe). Ce modèle doit
exister avant la toute première migration, car il est déclaré dans
settings.py par AUTH_USER_MODEL = "utilisateurs.Utilisateur".
"""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

    
class GestionnaireUtilisateur(BaseUserManager):
    """Gestionnaire chargé de créer les utilisateurs (méthodes imposées par Django)."""

    def create_user(self, email, password=None, **champs):
        """Crée un utilisateur ordinaire.

        Le mot de passe est toujours haché par set_password : il n'est jamais
        stocké en clair (MPD : « hash, jamais en clair »).
        """
        if not email:
            raise ValueError("L'email est obligatoire")
        utilisateur = self.model(email=self.normalize_email(email), **champs)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, password=None, **champs):
        """Crée un administrateur (commande « createsuperuser »)."""
        champs.setdefault("role", "administrateur")
        champs["is_superuser"] = True
        return self.create_user(email, password, **champs)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """Personne qui se connecte à l'application (table `utilisateur`).

    Deux rôles existent : « administrateur » (peut n'avoir aucune parcelle,
    RG1) et « proprietaire » (possède des parcelles).

    Les noms `password`, `is_active` et `is_staff` restent en anglais car
    Django les exige. La colonne SQL, elle, s'appelle bien `mot_de_passe`.
    """

    ROLES = [
        ("administrateur", "Administrateur"),
        ("proprietaire", "Propriétaire"),
    ]

    utilisateur_id = models.AutoField(primary_key=True)
    # Ajout par rapport au MPD : sert d'identifiant de connexion (voir USERNAME_FIELD).
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=ROLES, default="proprietaire")
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    # Redéfinit le champ `password` de Django pour utiliser la colonne `mot_de_passe`.
    password = models.CharField(max_length=128, db_column="mot_de_passe")

    USERNAME_FIELD = "email"             # champ utilisé pour se connecter
    REQUIRED_FIELDS = ["nom", "prenom"]  # demandés par « createsuperuser »
    objects = GestionnaireUtilisateur()

    @property
    def is_active(self):
        """Django lit ce nom : un compte désactivé (actif = False) ne peut plus se connecter."""
        return self.actif

    @property
    def is_staff(self):
        """Seuls les administrateurs accèdent à l'interface d'administration Django."""
        return self.role == "administrateur"

    class Meta:
        db_table = "utilisateur"

    def __str__(self):
        return f"{self.prenom} {self.nom}"