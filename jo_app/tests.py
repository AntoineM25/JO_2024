"""
Ce module gère les tests unitaires de l'application.
"""

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

from .forms import ConnexionForm, PaiementForm, TicketForm, UtilisateurForm


class UtilisateurModelTest(TestCase):
    """
    Test du modèle Utilisateur.
    """

    def setUp(self):
        """
        Création d'un utilisateur pour les tests.
        """
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
        """
        Test de la création d'un utilisateur.
        """
        utilisateur = Utilisateur.objects.get(email="gilles.dupont@exemple.com")
        self.assertEqual(utilisateur.nom, "Dupont")
        self.assertEqual(utilisateur.prenom, "Gilles")
        self.assertEqual(utilisateur.sexe, "H")
        self.assertEqual(utilisateur.adresse, "123 Rue Test")
        self.assertEqual(utilisateur.code_postal, "75000")
        self.assertEqual(utilisateur.ville, "Paris")
        self.assertEqual(str(utilisateur.date_de_naissance), "1942-08-01")

    def test_email_unique(self):
        """
        Test de l'unicité de l'adresse email de l'utilisateur.
        """
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
        """
        Test de la génération de la clé sécurisée 1.
        """
        self.assertIsNotNone(self.utilisateur.cle_securisee_1)
        self.assertEqual(len(self.utilisateur.cle_securisee_1), 64)

    def test_champs_obligatoires(self):
        """
        Test de la validation des champs obligatoires.
        """
        with self.assertRaises(ValidationError):
            utilisateur = Utilisateur(
                prenom="SansNom", sexe="H", email="sans.nom@example.com"
            )
            utilisateur.full_clean()

    def test_validation_mot_de_passe(self):
        """
        Test de la validation du mot de passe.
        """
        try:
            self.utilisateur.set_password("MotdePasse1!")
            self.utilisateur.full_clean()
        except ValidationError as e:
            self.fail(f"Le mot de passe n'a pas été validé correctement: {e}")


class TicketModelTest(TestCase):
    """
    Test du modèle Ticket.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport et d'une offre pour les tests.
        """
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
        """
        Test de la création d'un ticket.
        """
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=2
        )
        self.assertEqual(ticket.utilisateur.email, "gilles.dupont@exemple.com")
        self.assertEqual(ticket.sport.nom, "Basketball")
        self.assertEqual(ticket.offre.type, "solo")
        self.assertEqual(ticket.quantite, 2)

    def test_calcul_prix_total_ticket(self):
        """
        Test du calcul du prix total d'un ticket.
        """
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur, sport=self.sport, offre=self.offre, quantite=3
        )
        self.assertEqual(ticket.get_prix_total(), 60.00)


class SportModelTest(TestCase):
    """
    Test du modèle Sport.
    """

    def setUp(self):
        """
        Création d'un sport pour les tests.
        """
        self.sport = Sport.objects.create(
            nom="Natation",
            date_evenement="2024-07-25",
            description="Compétition de natation olympique.",
        )

    def test_creation_sport(self):
        """
        Test de la création d'un sport.
        """
        sport = Sport.objects.get(nom="Natation")
        self.assertEqual(sport.nom, "Natation")
        self.assertEqual(str(sport.date_evenement), "2024-07-25")
        self.assertEqual(sport.description, "Compétition de natation olympique.")
        self.assertFalse(sport.image)

    def test_str_representation(self):
        """
        Test de la représentation en chaîne de caractères d'un sport.
        """
        self.assertEqual(str(self.sport), "Natation")


class PaiementModelTest(TestCase):
    """
    Test du modèle Paiement.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport, d'une offre et d'un ticket pour
        """
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
        """
        Test de la création d'un paiement.
        """
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
        self.assertIsNotNone(paiement.date_paiement)

    def test_str_representation(self):
        """
        Test de la représentation en chaîne de caractères d'un paiement.
        """
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
    """
    Test du modèle GenerationTicket.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport, d'une offre, d'un ticket et d'un billet de génération pour les tests.
        """
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
        """
        Test de la création d'un billet de génération.
        """
        mock_upload.return_value = {"secure_url": "http://example.com/fake_qrcode.png"}

        generation_ticket = GenerationTicket.objects.create(
            ticket=self.ticket, quantite_vendue=1
        )

        self.assertIsNotNone(generation_ticket.cle_securisee_2)
        self.assertEqual(len(generation_ticket.cle_securisee_2), 64)

        self.assertEqual(
            generation_ticket.qr_code, "http://example.com/fake_qrcode.png"
        )


class PasswordValidationTest(TestCase):
    """
    Test de la fonction de validation du mot de passe.
    """

    def test_password_too_short(self):
        """
        Test de la validation d'un mot de passe trop court.
        """
        with self.assertRaises(ValidationError) as cm:
            validate_password("Abc!12")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins 8 caractères.",
        )

    def test_password_no_uppercase(self):
        """
        Test de la validation d'un mot de passe sans majuscule.
        """
        with self.assertRaises(ValidationError) as cm:
            validate_password("abcd1234!")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins une majuscule.",
        )

    def test_password_no_special_character(self):
        """
        Test de la validation d'un mot de passe sans caractère spécial.
        """
        with self.assertRaises(ValidationError) as cm:
            validate_password("Abcdefgh")
        self.assertEqual(
            cm.exception.messages[0],
            "Le mot de passe doit contenir au moins un caractère spécial.",
        )

    def test_valid_password(self):
        """
        Test de la validation d'un mot de passe valide.
        """
        try:
            validate_password("Abcdefg!")
        except ValidationError:
            self.fail(
                "La validation du mot de passe a échoué alors qu'elle aurait dû réussir."
            )


class OffreModelTest(TestCase):
    """
    Test du modèle Offre.
    """

    def setUp(self):
        """
        Création d'une offre pour les tests.
        """
        self.offre = Offre.objects.create(type="Famille", prix=Decimal("49.99"))

    def test_creation_offre(self):
        """
        Test de la création d'une offre.
        """
        offre = Offre.objects.get(type="Famille")
        self.assertEqual(offre.type, "Famille")
        self.assertEqual(offre.prix, Decimal("49.99"))


class HomeViewTest(TestCase):
    """
    Test de la vue home.
    """

    def test_home_view(self):
        """
        Test de l'accès à la page d'accueil.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class InscriptionViewTest(TestCase):
    """
    Test de la vue d'inscription.
    """

    def test_inscription_view(self):
        """
        Test de l'accès à la page d'inscription.
        """
        response = self.client.get(reverse("inscription"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inscription.html")

    def test_valid_registration(self):
        """
        Test de l'inscription d'un utilisateur valide.
        """
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


class TicketCreateViewTest(TestCase):
    """
    Test de la vue de création de ticket.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport et d'une offre pour les tests.
        """
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
        """
        Test de l'accès à la page de création de ticket.
        """
        response = self.client.get(
            reverse("ticket_create") + f"?sport={self.sport.nom}"
        )
        self.assertEqual(response.status_code, 200)

    def test_valid_ticket_creation(self):
        """
        Test de la création d'un ticket valide.
        """
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


class TicketListViewTest(TestCase):
    """
    Test de la vue de la liste des tickets.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport, d'une offre et d'un ticket pour
        """
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
        """
        Test de l'accès à la liste des tickets.
        """
        response = self.client.get(reverse("ticket_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Football")


class PanierViewTest(TestCase):
    """
    Test de la vue du panier.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport, d'une offre, d'un ticket et connexion de l'utilisateur pour les tests.
        """
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
        """
        Test de l'accès à la page du panier.
        """
        response = self.client.get(reverse("panier"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panier.html")
        self.assertContains(response, "Total du panier")

    def test_mise_a_jour_quantite(self):
        """
        Test de la mise à jour de la quantité d'un ticket dans le panier.
        """
        response = self.client.post(
            reverse("panier"),
            {
                f"quantite_{
                    self.ticket.id}": 3,
                "action": "update",
            },
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.quantite, 3)

    def test_suppression_ticket(self):
        """
        Test de la suppression d'un ticket du panier.
        """
        response = self.client.post(
            reverse("panier"), {"action": f"delete_{self.ticket.id}"}
        )
        self.assertFalse(Ticket.objects.filter(id=self.ticket.id).exists())

    def test_quantite_invalide(self):
        """
        Test de la mise à jour de la quantité avec une valeur invalide.
        """
        response = self.client.post(
            reverse("panier"),
            {f"quantite_{self.ticket.id}": -1, "action": "update"},
        )
        self.ticket.refresh_from_db()
        self.assertNotEqual(self.ticket.quantite, -1)


class TelechargerBilletViewTest(TestCase):
    """
    Test de la vue pour le téléchargement du billet.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'un sport, d'une offre, d'un ticket et d'un billet pour les tests.
        """
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
        """
        Test de l'accès au téléchargement du billet.
        """
        response = self.client.get(reverse("telecharger_billet", args=[self.billet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response["Content-Type"])

    def test_acces_billet_non_existant(self):
        """
        Test de l'accès à un billet inexistant.
        """
        response = self.client.get(reverse("telecharger_billet", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_acces_billet_autre_utilisateur(self):
        """
        Test de l'accès à un billet d'un autre utilisateur.
        """
        autre_utilisateur = Utilisateur.objects.create_user(
            email="jean.dupont@exemple.com",
            password="Test@123",
            nom="Dupont",
            prenom="Jean",
        )
        self.client.login(email="jean.dupont@exemple.com", password="Test@123")

        response = self.client.get(reverse("telecharger_billet", args=[self.billet.id]))
        self.assertEqual(response.status_code, 404)


class UtilisateurFormTest(TestCase):
    """
    Test du formulaire UtilisateurForm.
    """

    def test_form_with_valid_data(self):
        """
        Test de la validation du formulaire avec des données valides.
        """
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
        """
        Test de la validation du formulaire avec un mot de passe trop court.
        """
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
        """
        Test de la validation du formulaire avec des mots de passe non identiques.
        """
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


class TicketFormTest(TestCase):
    """
    Test du formulaire TicketForm.
    """

    def setUp(self):
        """
        Création d'une offre et d'un sport pour les tests.
        """
        self.offre = Offre.objects.create(type="Standard", prix=50.0)
        self.sport = Sport.objects.create(nom="Football", date_evenement="2024-07-01")

    def test_ticket_form_valid_data(self):
        """
        Test de la validation du formulaire avec des données valid
        """
        form_data = {
            "offre": self.offre.id,
            "sport": self.sport.id,
        }
        form = TicketForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ticket_form_empty_data(self):
        """
        Test de la validation du formulaire avec des données vides.
        """
        form = TicketForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("offre", form.errors)
        self.assertIn("sport", form.errors)

    def test_ticket_form_initial_values(self):
        """
        Test des valeurs initiales des champs du formulaire.
        """
        form = TicketForm()
        self.assertEqual(
            form.fields["sport"].choices[0], ("", "Choisissez votre sport !")
        )
        self.assertEqual(
            form.fields["offre"].choices[0], ("", "Choisissez votre offre !")
        )


class PaiementFormTest(TestCase):
    """
    Test du formulaire PaiementForm.
    """

    def setUp(self):
        """
        Création d'un utilisateur, d'une offre, d'un sport et d'un ticket pour les tests.
        """
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
        """
        Test de la validation du formulaire avec des données valid
        """
        form_data = {
            "ticket": self.ticket.id,
            "montant": self.ticket.get_prix_total(),
            "methode_paiement": "carte",
        }
        form = PaiementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_paiement_form_invalid_data(self):
        """
        Test de la validation du formulaire avec des données invalides.
        """
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
        """
        Test des choix possibles pour la méthode de paiement.
        """
        form = PaiementForm()
        self.assertIn(
            ("carte", "Carte de crédit"), form.fields["methode_paiement"].choices
        )
        self.assertIn(("paypal", "PayPal"), form.fields["methode_paiement"].choices)
        self.assertIn(
            ("virement", "Virement bancaire"), form.fields["methode_paiement"].choices
        )


class ConnexionFormTest(TestCase):
    """
    Test du formulaire ConnexionForm.
    """

    def setUp(self):
        """
        Création d'un utilisateur pour les tests.
        """
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="Test@123",
            nom="Test",
            prenom="Utilisateur",
        )

    def test_connexion_form_valid_data(self):
        """
        Test de la validation du formulaire avec des données valides
        """
        form_data = {
            "username": "testuser@example.com",
            "password": "Test@123",
        }
        form = ConnexionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_connexion_form_invalid_data(self):
        """
        Test de la validation du formulaire avec des données invalid
        """
        form_data = {
            "username": "testuser@example.com",
            "password": "wrongpassword",
        }
        form = ConnexionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
