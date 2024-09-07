from django.db import models

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
    cle_securisee_1 = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# Modèle ticket
# Modèle paiement
# Modèle génération_ticket