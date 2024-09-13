from django import forms
from .models import Utilisateur, Ticket, Paiement, GenerationTicket
from django.contrib.auth.forms import AuthenticationForm

# Formulaire d'inscription
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

# Formulaire d'inscription
class UtilisateurForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}))
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez votre mot de passe'}))
    
    class Meta:
        model = Utilisateur
        fields = ["nom", "prenom", "sexe", "email", "adresse", "code_postal", "ville", "date_de_naissance"]
        labels = {
            "nom": "Nom",
            "prenom": "Prénom",
            "sexe": "Sexe",
            "email": "Adresse e-mail",
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
            "adresse": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre adresse"}),
            "code_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre code postal"}),
            "ville": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre ville"}),
            "date_de_naissance": forms.DateInput(attrs={"type": "date", "class": "form-control"})
        }


# Formulaire choix de ticket
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['type_ticket', 'sport']  
        labels = {
            'type_ticket': "Choix de l'offre",
            'sport': "Sport choisi",
        }
        widgets = {
            'type_ticket': forms.Select(attrs={'class': 'form-control'}),
            'sport': forms.Select(attrs={'class': 'form-control'}),
        }
    
# Formulaire du paiement
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['ticket', 'montant', 'methode_paiement']
        labels = {
            'ticket': 'Ticket',
            'montant': 'Montant',
            'methode_paiement': 'Mode de paiement',
        }
        widgets = {
            'ticket': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'methode_paiement': forms.Select(attrs={'class': 'form-control'}),
        }

# Formulaire de connexion
class ConnexionForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre adresse email'}))
    mot_de_passe = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}))
