"""
Ce module contient les modèles de données de l'application.
Il contient les classes Utilisateur, Sport, Offre, Ticket, Paiement et GenerationTicket.
"""

import logging
import os
import re
import secrets
import traceback
from io import BytesIO

import cloudinary.uploader
import qrcode
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

SEXE_CHOICES = [
    ("H", "Homme"),
    ("F", "Femme"),
    ("NB", "Non-binaire"),
]


def validate_password(value):
    """
    Ce validateur vérifie que le mot de passe contient au moins 8 caractères, une majuscule et un caractère spécial.
    """
    if len(value) < 8:
        raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            "Le mot de passe doit contenir au moins un caractère spécial."
        )


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        """
        Crée et enregistre un utilisateur normal.
        """
        if not email:
            raise ValueError("Les utilisateurs doivent avoir une adresse email")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)

        if password:
            validate_password(password)
            user.set_password(password)
        else:
            raise ValueError("Le mot de passe est obligatoire")

        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        """
        Crée et enregistre un superutilisateur.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, nom, prenom, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """
    Ce modèle représente un utilisateur de l'application.
    """

    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=5, choices=SEXE_CHOICES, default="H")
    email = models.EmailField(max_length=50, unique=True)
    adresse = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=50)
    date_de_naissance = models.DateField(null=False, blank=False, default="2000-01-01")
    date_d_inscription = models.DateField(auto_now_add=True)
    cle_securisee_1 = models.CharField(max_length=64, blank=True, editable=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    objects = UtilisateurManager()

    def save(self, *args, **kwargs):
        """
        Génère une clé sécurisée pour l'utilisateur s'il n'en a pas déjà une.
        """
        if not self.cle_securisee_1:
            self.cle_securisee_1 = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Retourne le nom complet de l'utilisateur.
        """
        return f"{self.prenom} {self.nom}"


class Sport(models.Model):
    """
    Ce modèle représente un événement sportif.
    """

    nom = models.CharField(max_length=100)
    date_evenement = models.DateField()
    image = models.ImageField(upload_to="images/sports/", blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        """
        Retourne le nom de l'événement sportif.
        """
        return self.nom


class Offre(models.Model):
    """
    Ce modèle représente une offre de ticket pour un événement sportif.
    """

    type = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """
        Retourne le type et le prix de l'offre.
        """
        return f"{self.type} - {self.prix}€"


class Ticket(models.Model):
    """
    Ce modèle représente un ticket acheté par un utilisateur.
    """

    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name="tickets"
    )
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, default=1)
    quantite = models.PositiveIntegerField(default=1)
    est_achete = models.BooleanField(default=False)

    def get_prix_total(self):
        """
        Retourne le prix total du ticket.
        """
        return self.offre.prix * self.quantite

    def __str__(self):
        """
        Retourne une chaîne de caractères représentant le ticket.
        """
        return f"{self.sport.nom} - {self.offre.type} - Quantité: {self.quantite}"


class Paiement(models.Model):
    """
    Ce modèle représente un paiement effectué pour un ticket.
    """

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="paiements"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode_paiement = models.CharField(max_length=50)
    statut_paiement = models.BooleanField(default=False)
    date_paiement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Retourne une chaîne de caractères représentant le
        """
        return f"{self.ticket} - {self.montant} - {self.date_paiement}"


class GenerationTicket(models.Model):
    """
    Ce modèle représente un ticket généré pour un utilisateur.
    """

    ticket = models.ForeignKey(
        "Ticket", on_delete=models.CASCADE, related_name="generation_tickets"
    )
    cle_securisee_2 = models.CharField(max_length=64, blank=True, editable=False)
    quantite_vendue = models.IntegerField(default=0)
    date_generation = models.DateTimeField(auto_now_add=True)
    qr_code = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Génère un QR code pour le ticket s'il n'en a pas déjà un.
        """
        if not self.cle_securisee_2:
            self.cle_securisee_2 = secrets.token_hex(32)

        cle_finale = f"{
            self.ticket.utilisateur.cle_securisee_1}{
            self.cle_securisee_2}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(cle_finale)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        try:
            result = cloudinary.uploader.upload(
                buffer,
                folder="qr_codes",
                public_id=f"qr_code_{
                    self.ticket.id}",
            )
            self.qr_code = result["secure_url"]
        except Exception as e:
            logger.error(f"Error uploading QR code to Cloudinary: {str(e)}")
            traceback.print_exc()
            raise e

        super().save(*args, **kwargs)
