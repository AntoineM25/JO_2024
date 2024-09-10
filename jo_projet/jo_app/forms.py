from django import forms
from .models import Utilisateur

# Formulaire d'inscription
class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ["nom", "prenom", "sexe", "email", "mot_de_passe", "adresse", "code_postal", "ville", "date_de_naissance"]
        widgets = {
            "mot_de_passe": forms.PasswordInput(),  # Pour afficher le champ mot de passe en tant que champ sécurisé
        }