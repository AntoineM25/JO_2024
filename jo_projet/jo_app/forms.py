from django import forms
from .models import Utilisateur, Ticket, Paiement, GenerationTicket

# Formulaire d'inscription

class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ["nom", "prenom", "sexe", "email", "mot_de_passe", "adresse", "code_postal", "ville", "date_de_naissance"]
        labels = {
            "nom": "Nom",
            "prenom": "Prénom",
            "sexe": "Sexe",
            "email": "Adresse e-mail",
            "mot_de_passe": "Mot de passe",
            "adresse": "Adresse",
            "code_postal": "Code postal",
            "ville": "Ville",
            "date_de_naissance": "Date de naissance",
        }
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre nom"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre prénom"}),
            "sexe": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Entrez votre adresse e-mail"}),
            "mot_de_passe": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Entrez votre mot de passe"}),
            "adresse": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre adresse"}),
            "code_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre code postal"}),
            "ville": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre ville"}),
            "date_de_naissance": forms.DateInput(attrs={"type": "date", "class": "form-control"})
        }

# Formulaire choix de ticket

"""
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['type_ticket', 'sport']  
        labels = {
            'type_ticket': 'Choix du ticket',
            'sport': 'Sport'
        }
        widgets = {
            'type_ticket': forms.Select(attrs={"class": "form-control"}),
            'sport': forms.Select(attrs={"class": "form-control"})  
        } 
"""

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["type_ticket", "nom_evenement", "date_evenement"]
        labels = {
            "type_ticket": "Choix de l'offre",
            "nom_evenement": "Sport choisi",
            "date_evenement": "Date de l'événement",
        }
        widgets = {
            "type_ticket": forms.Select(attrs={"class": "form-control"}),
            "nom_evenement": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "date_evenement": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }

    