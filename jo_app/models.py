from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from io import BytesIO
import secrets, re, qrcode, os, logging, cloudinary.uploader

logger = logging.getLogger(__name__)

SEXE_CHOICES = [
    ('H', 'Homme'),
    ('F', 'Femme'),
    ('NB', 'Non-binaire'),
]

# Fonction de validation du mot de passe
def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Le mot de passe doit contenir au moins une majuscule.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial.')

# Gestionnaire personnalisé d'utilisateur
class UtilisateurManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        """Crée et enregistre un utilisateur normal."""
        if not email:
            raise ValueError('Les utilisateurs doivent avoir une adresse email')
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        
        # Valider le mot de passe avant de le définir
        if password:
            validate_password(password)
            user.set_password(password)  # Hacher le mot de passe
        else:
            raise ValueError('Le mot de passe est obligatoire')
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        """Crée et enregistre un superutilisateur."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, nom, prenom, password, **extra_fields)

# Modèle utilisateur
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=5, choices=SEXE_CHOICES, default='H')
    email = models.EmailField(max_length=50, unique=True)
    adresse = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=50)
    date_de_naissance = models.DateField(null=False, blank=False, default='2000-01-01')
    date_d_inscription = models.DateField(auto_now_add=True)
    cle_securisee_1 = models.CharField(max_length=64, blank=True, editable=False)

    # Champs nécessaires pour le système d'authentification
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Déclaration du champ utilisé pour la connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    # Utilisation du manager personnalisé
    objects = UtilisateurManager()

    def save(self, *args, **kwargs):
        if not self.cle_securisee_1:
            self.cle_securisee_1 = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# Modèle sport
from django.db import models

class Sport(models.Model):
    nom = models.CharField(max_length=100)
    date_evenement = models.DateField()
    image = models.ImageField(upload_to='images/sports/', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

# Modèle offre
class Offre(models.Model):
    type = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.type} - {self.prix}€"

# Modèle ticket
class Ticket(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="tickets")
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, default=1)
    quantite = models.PositiveIntegerField(default=1)  
    est_achete = models.BooleanField(default=False)
    
    def get_prix_total(self):
        return self.offre.prix * self.quantite

    def __str__(self):
        return f"{self.sport.nom} - {self.offre.type} - Quantité: {self.quantite}"

# Modèle paiement
class Paiement(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode_paiement = models.CharField(max_length=50)
    statut_paiement = models.BooleanField(default=False)
    date_paiement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ticket} - {self.montant} - {self.date_paiement}"



# Modèle generation_ticket
class GenerationTicket(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name="generation_tickets")
    qr_code = models.ImageField(blank=True, upload_to='qr_codes/')
    cle_securisee_2 = models.CharField(max_length=64, blank=True, editable=False)
    quantite_vendue = models.IntegerField(default=0)
    date_generation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.cle_securisee_2:
            self.cle_securisee_2 = secrets.token_hex(32)

        cle_finale = f"{self.ticket.utilisateur.cle_securisee_1}{self.cle_securisee_2}"

        # Génération du QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(cle_finale)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

         # Utiliser ImageField pour sauvegarder le fichier sur Cloudinary
        self.qr_code.save(None, ContentFile(buffer.getvalue()), save=False)
        # nom_fichier = f'ticket_{self.ticket.id}_{secrets.token_hex(4)}.png'
        # self.qr_code.save(nom_fichier, File(buffer), save=True)
        # self.qr_code.save(f'qr_code_{self.ticket.id}.png', File(buffer), save=True)
        
        if not self.qr_code:
                raise ValueError("QR Code image was not saved to Cloudinary.")

        logger.info(f"Successfully saved QR Code for ticket {self.ticket.id}: {self.qr_code.url}")
        
        print(f'Successfully saved QR Code for ticket {self.ticket.id}: {self.qr_code.url}')
        
    # except Exception as e:
    #     # Catch and log any error that occurs during the save process
    #     logger.error(f"Error saving QR Code for ticket {self.ticket.id}: {str(e)}")
    #     raise e

        super().save(*args, **kwargs)