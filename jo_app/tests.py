from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from jo_app.models import (
    GenerationTicket,
    Offre,
    Paiement,
    Sport,
    Ticket,
    Utilisateur,
    validate_password,
)
from .forms import ConnexionForm, TicketForm, UtilisateurForm, PaiementForm


## TEST DES MODELS ##

# Test du modèle Utilisateur
class UtilisateurModelTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Gilles",
            sexe="H",
            email="gilles.dupont@exemple.com",
            adresse="123 Rue Test",
            code_postal="75000",
            ville="Paris",
            date_de_naissance="1942-08-01",
        )

    def test_creation_utilisateur(self):
        utilisateur = Utilisateur.objects.get(email="gilles.dupont@exemple.com")
        self.assertEqual(utilisateur.nom, "Dupont")
        self.assertEqual(utilisateur.prenom, "Gilles")
        self.assertEqual(utilisateur.sexe, "H")
        self.assertEqual(utilisateur.adresse, "123 Rue Test")
        self.assertEqual(utilisateur.code_postal, "75000")
        self.assertEqual(utilisateur.ville, "Paris")
        self.assertEqual(str(utilisateur.date_de_naissance), "1942-08-01")

    def test_email_unique(self):
        with self.assertRaises(Exception):
            Utilisateur.objects.create(
                nom="Dupont",
                prenom="Jean",
                sexe="H",
                email="gilles.dupont@exemple.com",
                adresse="456 Rue Duplication",
                code_postal="75001",
                ville="Paris",
                date_de_naissance="1985-05-23",
            )

    def test_cle_securisee_generation(self):
        self.assertIsNotNone(self.utilisateur.cle_securisee_1)
        self.assertEqual(len(self.utilisateur.cle_securisee_1), 64)

    def test_champs_obligatoires(self):
        with self.assertRaises(ValidationError):
            utilisateur = Utilisateur(
                prenom="SansNom", sexe="H", email="sans.nom@example.com"
            )
            utilisateur.full_clean()  

    def test_validation_mot_de_passe(self):
        try:
            self.utilisateur.set_password("MotdePasse1!")
            self.utilisateur.full_clean()
        except ValidationError as e:
            self.fail(f"Le mot de passe n'a pas été validé correctement: {e}")


# Test du modèle Ticket
class TicketModelTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Gilles",
            sexe="H",
            email="gilles.dupont@exemple.com",
            adresse="123 Rue Test",
            code_postal="75000",
            ville="Paris",
            date_de_naissance="1942-08-01",
        )

        self.sport = Sport.objects.create(nom="Basketball", date_evenement="2024-08-01")

        self.offre = Offre.objects.create(type="solo", prix=20.00)

    def test_creation_ticket(self):
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=2
        )
        self.assertEqual(ticket.utilisateur.email, "gilles.dupont@exemple.com")
        self.assertEqual(ticket.sport.nom, "Basketball")
        self.assertEqual(ticket.offre.type, "solo")
        self.assertEqual(ticket.quantite, 2)

    def test_calcul_prix_total_ticket(self):
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=3
        )
        self.assertEqual(
            ticket.get_prix_total(), 60.00
        ) 


# Test du modèle Sport
class SportModelTest(TestCase):

    def setUp(self):
        self.sport = Sport.objects.create(
            nom="Natation",
            date_evenement="2024-07-25",
            description="Compétition de natation olympique.",
        )

    def test_creation_sport(self):
        sport = Sport.objects.get(nom="Natation")
        self.assertEqual(sport.nom, "Natation")
        self.assertEqual(str(sport.date_evenement), "2024-07-25")
        self.assertEqual(sport.description, "Compétition de natation olympique.")
        self.assertFalse(sport.image)  

    def test_str_representation(self):
        self.assertEqual(str(self.sport), "Natation")


# Test du modèle Paiement
class PaiementModelTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Gilles",
            sexe="H",
            email="gilles.dupont@exemple.com",
            adresse="123 Rue Test",
            code_postal="7500",
            ville="Paris",
            date_de_naissance="1942-08-01",
        )
        self.sport = Sport.objects.create(nom="Football", date_evenement="2024-09-15")
        self.offre = Offre.objects.create(type="famille", prix=50.00)
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=1
        )

    def test_creation_paiement(self):
        paiement = Paiement.objects.create(
            ticket=self.ticket,
            montant=self.ticket.get_prix_total(),
            methode_paiement="Carte de crédit",
            statut_paiement=True,
        )
        self.assertEqual(paiement.ticket, self.ticket)
        self.assertEqual(paiement.montant, self.ticket.get_prix_total())
        self.assertEqual(paiement.methode_paiement, "Carte de crédit")
        self.assertTrue(paiement.statut_paiement)
        self.assertIsNotNone(
            paiement.date_paiement
        )  

    def test_str_representation(self):
        paiement = Paiement.objects.create(
            ticket=self.ticket,
            montant=self.ticket.get_prix_total(),
            methode_paiement="Carte de crédit",
            statut_paiement=True,
        )
        self.assertEqual(
            str(paiement),
            f"{self.ticket} - {paiement.montant} - {paiement.date_paiement}",
        )


class GenerationTicketModelTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Gilles",
            sexe="H",
            email="gilles.dupont@exemple.com",
            adresse="123 Rue Test",
            code_postal="75000",
            ville="Paris",
            date_de_naissance="1942-08-01",
        )
        self.sport = Sport.objects.create(nom="Natation", date_evenement="2024-07-25")
        self.offre = Offre.objects.create(type="famille", prix=50.00)
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=1
        )

    @patch("cloudinary.uploader.upload")  
    def test_generation_ticket_creation(self, mock_upload):
        mock_upload.return_value = {"secure_url": "http://example.com/fake_qrcode.png"}

        generation_ticket = GenerationTicket.objects.create(
            ticket=self.ticket, quantite_vendue=1
        )

        self.assertIsNotNone(generation_ticket.cle_securisee_2)
        self.assertEqual(len(generation_ticket.cle_securisee_2), 64)

        self.assertEqual(
            generation_ticket.qr_code, "http://example.com/fake_qrcode.png"
        )


# Test de la fonction de validation du mot de passe
class PasswordValidationTest(TestCase):

    def test_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password("Abc!12")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins 8 caractères.",
        )

    def test_password_no_uppercase(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password("abcd1234!")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins une majuscule.",
        )

    def test_password_no_special_character(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password("Abcdefgh")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins un caractère spécial.",
        )

    def test_valid_password(self):
        try:
            validate_password("Abcdefg!")
        except ValidationError:
            self.fail(
                "La validation du mot de passe a échoué alors qu'elle aurait dû réussir."
            )


# Test du modèle Offre
class OffreModelTest(TestCase):

    def setUp(self):
        self.offre = Offre.objects.create(type="Famille", prix=Decimal("49.99"))

    def test_creation_offre(self):
        offre = Offre.objects.get(type="Famille")
        self.assertEqual(offre.type, "Famille")
        self.assertEqual(offre.prix, Decimal("49.99"))


## Test des vues ##

# Test de la vue home
class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(
            reverse("home")
        )  # Assurez-vous d'avoir le bon nom d'URL
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


# Test de la vue inscription
class InscriptionViewTest(TestCase):
    def test_inscription_view(self):
        response = self.client.get(reverse("inscription"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inscription.html")

    def test_valid_registration(self):
        response = self.client.post(
            reverse("inscription"),
            {
                "nom": "Dupont",
                "prenom": "Gilles",
                "sexe": "H",
                "email": "gilles.dupont@exemple.com",
                "adresse": "123 Rue Test",
                "code_postal": "75000",
                "ville": "Paris",
                "date_de_naissance": "1942-08-01",
                "password1": "Test@123",
                "password2": "Test@123",
            },
        )
        self.assertRedirects(response, reverse("connexion"))
        self.assertTrue(
            Utilisateur.objects.filter(email="gilles.dupont@exemple.com").exists()
        )


# Test de la vue ticket (création ticket)
class TicketCreateViewTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="gilles.dupont@exemple.com",
            nom="Dupont",
            prenom="Gilles",
            password="Test@1234",
            adresse="123 Rue Test",
            code_postal="75000",
            ville="Paris",
            date_de_naissance="1942-08-01",
        )
        self.client.login(email="gilles.dupont@exemple.com", password="Test@1234")

        self.sport = Sport.objects.create(nom="Basketball", date_evenement="2024-08-01")
        self.offre = Offre.objects.create(type="Solo", prix=50.00)

    def test_ticket_create_view(self):
        response = self.client.get(
            reverse("ticket_create") + f"?sport={self.sport.nom}"
        )
        self.assertEqual(response.status_code, 200)

    def test_valid_ticket_creation(self):
        response = self.client.post(
            reverse("ticket_create"),
            {
                "sport": self.sport.id,
                "offre": self.offre.id,
                "quantite": 1,
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.utilisateur, self.utilisateur)
        self.assertEqual(ticket.sport, self.sport)
        self.assertEqual(ticket.offre, self.offre)
        self.assertEqual(ticket.quantite, 1)


# Test de la vue ticket (liste ticket)
class TicketListViewTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="gilles.dupont@exemple.com",
            password="Test@123",
            nom="Dupont",
            prenom="Gilles",
        )
        self.sport = Sport.objects.create(nom="Football", date_evenement="2024-09-15")
        self.offre = Offre.objects.create(type="Solo", prix=49.99)

        Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=1
        )

        self.client.login(email="gilles.dupont@exemple.com", password="Test@123")

    def test_ticket_list_view(self):
        response = self.client.get(reverse("ticket_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Football"
        )  


# Test de la vue du panier
class PanierViewTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="gilles.dupont@exemple.com",
            password="Test@123",
            nom="Dupont",
            prenom="Gilles",
        )
        self.sport = Sport.objects.create(nom="Natation", date_evenement="2024-07-25")
        self.offre = Offre.objects.create(type="Standard", prix=50.0)
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, offre=self.offre, sport=self.sport, quantite=1
        )
        self.client.login(email="gilles.dupont@exemple.com", password="Test@123")

    def test_acces_panier(self):
        response = self.client.get(reverse("panier"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panier.html")
        self.assertContains(response, "Total du panier")

    def test_mise_a_jour_quantite(self):
        response = self.client.post(
            reverse("panier"), {f"quantite_{self.ticket.id}": 3, "action": "update"}
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.quantite, 3)

    def test_suppression_ticket(self):
        response = self.client.post(
            reverse("panier"), {"action": f"delete_{self.ticket.id}"}
        )
        self.assertFalse(Ticket.objects.filter(id=self.ticket.id).exists())

    def test_quantite_invalide(self):
        response = self.client.post(
            reverse("panier"),
            {f"quantite_{self.ticket.id}": -1, "action": "update"}, 
        )
        self.ticket.refresh_from_db()
        self.assertNotEqual(
            self.ticket.quantite, -1
        )  


# Test de la vue pour le téléchargement du billet
class TelechargerBilletViewTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="gilles.dupont@exemple.com",
            password="Test@123",
            nom="Dupont",
            prenom="Gilles",
        )
        self.sport = Sport.objects.create(nom="Natation", date_evenement="2024-07-25")
        self.offre = Offre.objects.create(type="Standard", prix=50.0)
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, offre=self.offre, sport=self.sport, quantite=1
        )

        with patch("jo_app.models.cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = {"secure_url": "http://test.com/qr_code.png"}
            self.billet = GenerationTicket.objects.create(ticket=self.ticket)

        self.client.login(email="gilles.dupont@exemple.com", password="Test@123")

    def test_acces_telechargement_billet(self):
        response = self.client.get(reverse("telecharger_billet", args=[self.billet.id]))
        self.assertEqual(
            response.status_code, 200
        )  
        self.assertIn(
            "application/pdf", response["Content-Type"]
        )  

    def test_acces_billet_non_existant(self):
        response = self.client.get(
            reverse("telecharger_billet", args=[9999])
        )  
        self.assertEqual(response.status_code, 404)

    def test_acces_billet_autre_utilisateur(self):
        autre_utilisateur = Utilisateur.objects.create_user(
            email="jean.dupont@exemple.com",
            password="Test@123",
            nom="Dupont",
            prenom="Jean",
        )
        self.client.login(email="jean.dupont@exemple.com", password="Test@123")

        response = self.client.get(reverse("telecharger_billet", args=[self.billet.id]))
        self.assertEqual(
            response.status_code, 404
        )  


## Test des formulaires ##

# Test du formulaire utilisateur
class UtilisateurFormTest(TestCase):

    def test_form_with_valid_data(self):
        form = UtilisateurForm(
            data={
                "nom": "Dupont",
                "prenom": "Gilles",
                "sexe": "H",
                "email": "gilles.dupont@example.com",
                "adresse": "123 Rue Test",
                "code_postal": "75000",
                "ville": "Paris",
                "date_de_naissance": "1990-01-01",
                "password1": "Password@123",
                "password2": "Password@123",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_password(self):
        form = UtilisateurForm(
            data={
                "nom": "Dupont",
                "prenom": "Gilles",
                "sexe": "H",
                "email": "gilles.dupont@example.com",
                "adresse": "123 Rue Test",
                "code_postal": "75000",
                "ville": "Paris",
                "date_de_naissance": "1990-01-01",
                "password1": "pass",
                "password2": "pass",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_form_with_mismatched_passwords(self):
        form = UtilisateurForm(
            data={
                "nom": "Dupont",
                "prenom": "Gilles",
                "sexe": "H",
                "email": "gilles.dupont@example.com",
                "adresse": "123 Rue Test",
                "code_postal": "75000",
                "ville": "Paris",
                "date_de_naissance": "1990-01-01",
                "password1": "Password@123",
                "password2": "Different@123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


# Test du formulaire ticket
class TicketFormTest(TestCase):

    def setUp(self):
        self.offre = Offre.objects.create(type="Standard", prix=50.0)
        self.sport = Sport.objects.create(nom="Football", date_evenement="2024-07-01")

    def test_ticket_form_valid_data(self):
        form_data = {
            "offre": self.offre.id,
            "sport": self.sport.id,
        }
        form = TicketForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ticket_form_empty_data(self):
        form = TicketForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("offre", form.errors)
        self.assertIn("sport", form.errors)

    def test_ticket_form_initial_values(self):
        form = TicketForm()
        self.assertEqual(
            form.fields["sport"].choices[0], ("", "Choisissez votre sport !")
        )
        self.assertEqual(
            form.fields["offre"].choices[0], ("", "Choisissez votre offre !")
        )


# Test du formulaire paiement
class PaiementFormTest(TestCase):

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            password="Test@123",
            nom="Test",
            prenom="Utilisateur",
        )
        self.offre = Offre.objects.create(type="VIP", prix=100.0)
        self.sport = Sport.objects.create(nom="Tennis", date_evenement="2024-07-01")
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, offre=self.offre, sport=self.sport, quantite=2
        )

    def test_paiement_form_valid_data(self):
        form_data = {
            "ticket": self.ticket.id,
            "montant": self.ticket.get_prix_total(),
            "methode_paiement": "carte",
        }
        form = PaiementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_paiement_form_invalid_data(self):
        form_data = {
            "ticket": "",
            "montant": "",
            "methode_paiement": "",
        }
        form = PaiementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("ticket", form.errors)
        self.assertIn("montant", form.errors)
        self.assertIn("methode_paiement", form.errors)

    def test_paiement_form_method_choices(self):
        form = PaiementForm()
        self.assertIn(
            ("carte", "Carte de crédit"), form.fields["methode_paiement"].choices
        )
        self.assertIn(("paypal", "PayPal"), form.fields["methode_paiement"].choices)
        self.assertIn(
            ("virement", "Virement bancaire"), form.fields["methode_paiement"].choices
        )


# Test du formulaire de connexion
class ConnexionFormTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="Test@123",
            nom="Test",
            prenom="Utilisateur",
        )

    def test_connexion_form_valid_data(self):
        form_data = {
            "username": "testuser@example.com",
            "password": "Test@123",
        }
        form = ConnexionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_connexion_form_invalid_data(self):
        form_data = {
            "username": "testuser@example.com",
            "password": "wrongpassword",
        }
        form = ConnexionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
