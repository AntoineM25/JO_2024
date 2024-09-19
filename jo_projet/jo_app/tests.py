from django.test import TestCase
from jo_app.models import Utilisateur, Sport, Ticket, Paiement, GenerationTicket, Offre, validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from decimal import Decimal

## TEST DES MODELS ##

from django.core.exceptions import ValidationError

# Test du modèle Utilisateur
class UtilisateurModelTest(TestCase):

    def setUp(self):
        # Crée un utilisateur pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )

    def test_creation_utilisateur(self):
        # Vérifie que l'utilisateur a été créé avec les bons attributs
        utilisateur = Utilisateur.objects.get(email='gilles.dupont@exemple.com')
        self.assertEqual(utilisateur.nom, 'Dupont')
        self.assertEqual(utilisateur.prenom, 'Gilles')
        self.assertEqual(utilisateur.sexe, 'H')
        self.assertEqual(utilisateur.adresse, '123 Rue Test')
        self.assertEqual(utilisateur.code_postal, '75000')
        self.assertEqual(utilisateur.ville, 'Paris')
        self.assertEqual(str(utilisateur.date_de_naissance), '1942-08-01')

    def test_email_unique(self):
        # Vérifie que l'email de l'utilisateur est unique
        with self.assertRaises(Exception):
            Utilisateur.objects.create(
                nom='Dupont',
                prenom='Jean',
                sexe='H',
                email='gilles.dupont@exemple.com',  # Même email que l'utilisateur existant
                adresse='456 Rue Duplication',
                code_postal='75001',
                ville='Paris',
                date_de_naissance='1985-05-23'
            )

    def test_cle_securisee_generation(self):
        # Vérifie que la clé sécurisée est automatiquement générée
        self.assertIsNotNone(self.utilisateur.cle_securisee_1)
        self.assertEqual(len(self.utilisateur.cle_securisee_1), 64)

    def test_champs_obligatoires(self):
        # Vérifie que la création d'un utilisateur sans nom lève une exception
        with self.assertRaises(ValidationError):
            utilisateur = Utilisateur(
                prenom='SansNom',
                sexe='H',
                email='sans.nom@example.com'
            )
            utilisateur.full_clean()  # Utilisé pour déclencher les validations

    def test_validation_mot_de_passe(self):
        # Vérifie la validation du mot de passe si tu utilises une fonction de validation
        try:
            self.utilisateur.set_password('MotdePasse1!')
            self.utilisateur.full_clean()
        except ValidationError as e:
            self.fail(f"Le mot de passe n'a pas été validé correctement: {e}")


# Test du modèle Ticket
class TicketModelTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur, d'un sport et d'une offre pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        
        self.sport = Sport.objects.create(
            nom='Basketball',
            date_evenement='2024-08-01'
        )

        self.offre = Offre.objects.create(
            type='solo',
            prix=20.00
        )

    def test_creation_ticket(self):
        # Création du ticket pour l'utilisateur, l'offre et le sport
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=2
        )
        # Vérification si le ticket a été créé avec les bons attributs
        self.assertEqual(ticket.utilisateur.email, 'gilles.dupont@exemple.com')
        self.assertEqual(ticket.sport.nom, 'Basketball')
        self.assertEqual(ticket.offre.type, 'solo')
        self.assertEqual(ticket.quantite, 2)

    def test_calcul_prix_total_ticket(self):
        # Création du ticket pour tester le calcul du prix total
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=3
        )
        # Vérification du prix total
        self.assertEqual(ticket.get_prix_total(), 60.00)  # 20.00 (prix de l'offre) * 3 (quantité)

        
# Test du modèle Sport
class SportModelTest(TestCase):

    def setUp(self):
        # Création du sport pour les tests
        self.sport = Sport.objects.create(
            nom='Natation',
            date_evenement='2024-07-25',
            description='Compétition de natation olympique.'
        )

    def test_creation_sport(self):
        # Vérification que le sport a bien été créé avec les bons attributs
        sport = Sport.objects.get(nom='Natation')
        self.assertEqual(sport.nom, 'Natation')
        self.assertEqual(str(sport.date_evenement), '2024-07-25')
        self.assertEqual(sport.description, 'Compétition de natation olympique.')
        # Vérifie que le champ image est vide par défaut
        self.assertFalse(sport.image)  # Renvoie False si l'image n'a pas été définie

    def test_str_representation(self):
        # Vérification de la représentation en chaîne du modèle
        self.assertEqual(str(self.sport), 'Natation')


# Test du modèle Paiement
class PaiementModelTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur, un sport, et un ticket pour le paiement
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='7500',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        self.sport = Sport.objects.create(
            nom='Football',
            date_evenement='2024-09-15'
        )
        self.offre = Offre.objects.create(
            type='famille',
            prix=50.00
        )
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=1
        )

    def test_creation_paiement(self):
        # Création d'un paiement pour le ticket
        paiement = Paiement.objects.create(
            ticket=self.ticket,
            montant=self.ticket.get_prix_total(),
            methode_paiement='Carte de crédit',
            statut_paiement=True
        )
        # Vérification que le paiement a bien été créé avec les bons attributs
        self.assertEqual(paiement.ticket, self.ticket)
        self.assertEqual(paiement.montant, self.ticket.get_prix_total())
        self.assertEqual(paiement.methode_paiement, 'Carte de crédit')
        self.assertTrue(paiement.statut_paiement)
        self.assertIsNotNone(paiement.date_paiement)  # Vérifie que la date de paiement a été correctement définie

    def test_str_representation(self):
        # Création d'un paiement pour tester la méthode __str__
        paiement = Paiement.objects.create(
            ticket=self.ticket,
            montant=self.ticket.get_prix_total(),
            methode_paiement='Carte de crédit',
            statut_paiement=True
        )
        # Vérification de la représentation en chaîne du paiement
        self.assertEqual(str(paiement), f"{self.ticket} - {paiement.montant} - {paiement.date_paiement}")

# Test du modèle Génération de ticket
class GenerationTicketModelTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur, d'un sport et d'une offre pour le test
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='7500',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        self.sport = Sport.objects.create(
            nom='Natation',
            date_evenement='2024-07-25'
        )
        self.offre = Offre.objects.create(
            type='famille',
            prix=50.00
        )
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=1
        )

    def test_generation_ticket_creation(self):
        # Création d'un GenerationTicket pour le ticket
        generation_ticket = GenerationTicket.objects.create(
            ticket=self.ticket,
            quantite_vendue=1
        )

        # Vérifie que la clé sécurisée 2 a été générée
        self.assertIsNotNone(generation_ticket.cle_securisee_2)
        self.assertEqual(len(generation_ticket.cle_securisee_2), 64)

        # Vérifie que le QR code a été généré
        self.assertTrue(generation_ticket.qr_code.name.endswith('.png'))

# Test de la fonction de validation du mot de passe
class PasswordValidationTest(TestCase):

    def test_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('Abc!12')
        self.assertEqual(str(cm.exception), 'Le mot de passe doit contenir au moins 8 caractères.')

    def test_password_no_uppercase(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('abcd1234!')
        self.assertEqual(str(cm.exception), 'Le mot de passe doit contenir au moins une majuscule.')

    def test_password_no_special_character(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('Abcdefgh')
        self.assertEqual(str(cm.exception), 'Le mot de passe doit contenir au moins un caractère spécial.')

    def test_valid_password(self):
        try:
            validate_password('Abcdefg!')
        except ValidationError:
            self.fail('La validation du mot de passe a échoué alors qu\'elle aurait dû réussir.')

# Test du modèle Offre
class OffreModelTest(TestCase):

    def setUp(self):
        # Création d'une offre pour les tests
        self.offre = Offre.objects.create(
            type='Famille',
            prix=Decimal('49.99')
        )

    def test_creation_offre(self):
        # Vérification que l'offre a bien été créée avec les bons attributs
        offre = Offre.objects.get(type='Famille')
        self.assertEqual(offre.type, 'Famille')
        self.assertEqual(offre.prix, Decimal('49.99'))


# Test de la fonction de validation du mot de passe
class PasswordValidationTest(TestCase):

    def test_password_too_short(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('short')
        self.assertEqual(cm.exception.messages, ['Le mot de passe doit contenir au moins 8 caractères.'])

    def test_password_no_uppercase(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('lowercase1!')
        self.assertEqual(cm.exception.messages, ['Le mot de passe doit contenir au moins une majuscule.'])

    def test_password_no_special_character(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password('NoSpecialCharacter1')
        self.assertEqual(cm.exception.messages, ['Le mot de passe doit contenir au moins un caractère spécial.'])


## Test des vues ##

# Test de la vue home
from django.test import TestCase
from django.urls import reverse

class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))  # Assurez-vous d'avoir le bon nom d'URL
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
# Test de la vue inscription
class InscriptionViewTest(TestCase):
    def test_inscription_view(self):
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inscription.html')

    def test_valid_registration(self):
        response = self.client.post(reverse('inscription'), {
            'nom': 'Dupont',
            'prenom': 'Gilles',
            'sexe': 'H',
            'email': 'gilles.dupont@exemple.com',
            'adresse': '123 Rue Test',
            'code_postal': '75000',
            'ville': 'Paris',
            'date_de_naissance': '1942-08-01',
            'password1': 'Test@123',
            'password2': 'Test@123',
        })
        self.assertRedirects(response, reverse('connexion'))
        self.assertTrue(Utilisateur.objects.filter(email='gilles.dupont@exemple.com').exists())

# Test de la vue ticket (création ticket)
class TicketCreateViewTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur pour les tests
        self.utilisateur = Utilisateur.objects.create_user(
            email='gilles.dupont@exemple.com',
            nom='Dupont',
            prenom='Gilles',
            password='Test@1234',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        # Connexion de l'utilisateur
        self.client.login(email='gilles.dupont@exemple.com', password='Test@1234')

        # Création d'un sport et d'une offre pour les tests
        self.sport = Sport.objects.create(
            nom='Basketball',
            date_evenement='2024-08-01'
        )
        self.offre = Offre.objects.create(
            type='Solo',
            prix=50.00
        )

    def test_ticket_create_view(self):
        # Envoi d'une requête GET pour la vue de création de ticket
        response = self.client.get(reverse('ticket_create') + f'?sport={self.sport.nom}')
        self.assertEqual(response.status_code, 200)

    def test_valid_ticket_creation(self):
        # Envoi d'une requête POST pour créer un ticket
        response = self.client.post(reverse('ticket_create'), {
            'sport': self.sport.id,
            'offre': self.offre.id,
            'quantite': 1,
        })
        # Vérifier la redirection après la création du ticket
        self.assertEqual(response.status_code, 302)
        
        # Vérifier si le ticket a été créé
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.utilisateur, self.utilisateur)
        self.assertEqual(ticket.sport, self.sport)
        self.assertEqual(ticket.offre, self.offre)
        self.assertEqual(ticket.quantite, 1)

# Test de la vue ticket (liste ticket)
class TicketListViewTest(TestCase):
    def setUp(self):
        # Création d'un utilisateur, d'un sport, et d'une offre pour les tickets
        self.utilisateur = Utilisateur.objects.create_user(
            email='gilles.dupont@exemple.com',
            password='Test@123',
            nom='Dupont',
            prenom='Gilles'
        )
        self.sport = Sport.objects.create(nom='Football', date_evenement='2024-09-15')
        self.offre = Offre.objects.create(type='Solo', prix=49.99)
        
        # Création d'un ticket
        Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=1
        )
        
        # Connexion de l'utilisateur
        self.client.login(email='gilles.dupont@exemple.com', password='Test@123')

    def test_ticket_list_view(self):
        response = self.client.get(reverse('ticket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Football')  # Vérifie si le nom du sport est affiché dans la page
