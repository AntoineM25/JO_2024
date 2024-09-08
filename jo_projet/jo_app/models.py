from django.db import models
from django.utils import timezone
import secrets

# Modèle utilisateur
class Utilisateur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True)
    mot_de_passe = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    date_de_naissance = models.DateField()
    date_d_inscription = models.DateField(auto_now_add=True)
    est_administrateur = models.BooleanField(default=False)
    cle_securisee_1 = models.CharField(max_length=50, blank=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.cle_securisee_1:  # Si la clé n'est pas définie
            self.cle_securisee_1 = secrets.token_hex(3)  # Générer la clé sécurisée 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

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
    nom_evenement = models.CharField(max_length=100)
    date_evenement = models.DateField()

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
        return f"{self.utilisateur} - {self.nom_evenement} - {self.type_ticket}"
    
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
    qr_code = models.ImageField(upload_to='qr_codes/')
    cle_securisee_2 = models.CharField(max_length=50, blank=True, editable=False)  
    quantite_vendue = models.IntegerField(default=0)
    date_generation = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.cle_securisee_2:  # Si la clé n'est pas définie
            self.cle_securisee_2 = secrets.token_hex(3)  # Générer la clé sécurisée 2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket} - {self.date_generation}"
