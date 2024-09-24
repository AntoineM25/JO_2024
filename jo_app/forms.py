from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import formats

from .models import (Offre, Paiement, Sport, Ticket, Utilisateur,
                     validate_password)


# Formulaire d'inscription
class UtilisateurForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Entrez votre mot de passe"}
        ),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirmez votre mot de passe",
            }
        ),
    )

    class Meta:
        model = Utilisateur
        fields = [
            "nom",
            "prenom",
            "sexe",
            "email",
            "adresse",
            "code_postal",
            "ville",
            "date_de_naissance",
        ]
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
            "nom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Entrez votre nom"}
            ),
            "prenom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Entrez votre prénom"}
            ),
            "sexe": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Entrez votre adresse e-mail",
                }
            ),
            "adresse": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Entrez votre adresse"}
            ),
            "code_postal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Entrez votre code postal",
                }
            ),
            "ville": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Entrez votre ville"}
            ),
            "date_de_naissance": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error("password1", e)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# Formulaire choix de ticket
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["offre", "sport"]
        labels = {
            "offre": "Choix de l'offre",
            "sport": "Choix du sport",
        }
        widgets = {
            "offre": forms.Select(attrs={"class": "form-control", "localize": True}),
            "sport": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sport"].choices = [("", "Choisissez votre sport !")] + [
            (sport.id, f"{sport.nom} - {sport.date_evenement}")
            for sport in Sport.objects.all()
        ]

        self.fields["offre"].choices = [("", "Choisissez votre offre !")] + [
            (offre.id, f"{offre.type} - {formats.localize_input(offre.prix)}€")
            for offre in Offre.objects.all()
        ]


# Formulaire du paiement
class PaiementForm(forms.ModelForm):
    METHODES_PAIEMENT_CHOICES = [
        ("carte", "Carte de crédit"),
        ("paypal", "PayPal"),
        ("virement", "Virement bancaire"),
    ]

    methode_paiement = forms.ChoiceField(
        choices=METHODES_PAIEMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Méthode de paiement",
    )

    class Meta:
        model = Paiement
        fields = ["ticket", "montant", "methode_paiement"]
        labels = {
            "ticket": "Ticket",
            "montant": "Montant",
        }
        widgets = {
            "ticket": forms.Select(attrs={"class": "form-control"}),
            "montant": forms.NumberInput(attrs={"class": "form-control"}),
        }


# Formulaire de connexion
class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Entrez votre adresse email"}
        ),
        label="E-mail",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Entrez votre mot de passe"}
        ),
        label="Mot de passe",
    )
