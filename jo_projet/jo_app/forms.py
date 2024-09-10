from django import forms
from .models import Utilisateur 

# Formulaire d'inscription
class UtilisateurForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Veuillez entrer une adresse email valide.")

    class Meta:
        model = Utilisateur  # Utilisation de ton modèle Utilisateur
        fields = ["username", "email", "password1", "password2"]  # Champs requis
        labels = {
            "username": "Nom d'utilisateur",
            "email": "Adresse e-mail",
            "password1": "Mot de passe",
            "password2": "Confirmez le mot de passe",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Entrez votre nom d'utilisateur", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Entrez votre e-mail", "class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"placeholder": "Entrez votre mot de passe", "class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"placeholder": "Confirmez votre mot de passe", "class": "form-control"}),
        }

    def save(self, commit=True):
        user = super(UtilisateurForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
