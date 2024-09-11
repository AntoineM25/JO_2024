from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files import File
from io import BytesIO
import secrets, re, qrcode

# Modèle utilisateur
SEXE_CHOICES = [
    ('H', 'Homme'),
    ('F', 'Femme'),
    ('NB', 'Non-binaire'),
]

def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Le mot de passe doit contenir au moins une majuscule.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial.')

class Utilisateur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=5, choices=SEXE_CHOICES, default='H')
    email = models.EmailField(max_length=50, unique=True)
    mot_de_passe = models.CharField(max_length=50, validators=[validate_password])
    adresse = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)  
    ville = models.CharField(max_length=50)
    date_de_naissance = models.DateField(null=False, blank=False, default='2000-01-01')
    date_d_inscription = models.DateField(auto_now_add=True)
    est_administrateur = models.BooleanField(default=False)
    cle_securisee_1 = models.CharField(max_length=64, blank=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.cle_securisee_1:  # Si la clé n'est pas définie
            self.cle_securisee_1 = secrets.token_hex(32)  # Générer la clé sécurisée 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# Modèle sport
from django.db import models

class Sport(models.Model):
    nom = models.CharField(max_length=100)
    date_evenement = models.DateField()

    def __str__(self):
        return self.nom

# Modèle ticket
class Ticket(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="tickets")
    TYPE_TICKET_CHOICES = [
        ('solo', 'Solo'),
        ('duo', 'Duo'),
        ('famille', 'Famille'),
    ]
    type_ticket = models.CharField(max_length=10, choices=TYPE_TICKET_CHOICES)
    prix_solo = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)
    prix_duo = models.DecimalField(max_digits=10, decimal_places=2, default=35.00)
    prix_famille = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

    # Clé étrangère pour lier un ticket à un sport spécifique
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, default=1)

    # Obtenir le prix selon le type de ticket
    def get_prix(self):
        if self.type_ticket == 'solo':
            return self.prix_solo
        elif self.type_ticket == 'duo':
            return self.prix_duo
        elif self.type_ticket == 'famille':
            return self.prix_famille
        return 0

    def __str__(self):
        return f"{self.utilisateur} - {self.sport.nom} - {self.type_ticket}"
    
# Modèle paiement
class Paiement(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode_paiement = models.CharField(max_length=50)
    statut_paiement = models.BooleanField(default=False)
    date_paiement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ticket} - {self.montant} - {self.date_paiement}"

# Modèle génération_ticket
class GenerationTicket(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name="generation_tickets")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    cle_securisee_2 = models.CharField(max_length=64, blank=True, editable=False)  
    quantite_vendue = models.IntegerField(default=0)
    date_generation = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Génération de la clé sécurisée 2 si elle n'existe pas
        if not self.cle_securisee_2:
            self.cle_securisee_2 = secrets.token_hex(32)  # Générer la clé sécurisée 2

        # Concaténation des clés sécurisées 1 et 2
        cle_finale = f"{self.ticket.utilisateur.cle_securisee_1}{self.cle_securisee_2}"

        # Génération du QR Code basé sur la clé finale
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(cle_finale)
        qr.make(fit=True)

        # Sauvegarder le QR code comme fichier image
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_code.save(f'qr_code_{self.ticket.id}.png', File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket} - {self.date_generation}"

